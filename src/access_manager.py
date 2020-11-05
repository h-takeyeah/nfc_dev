import nfc
import mysql.connector as mc
from auto_close_cursor import AutoCloseCursor as atclscur
import soundutils
import dispatcherutils

PASORI_S380_PATH = 'usb:054c:06c3'

class AccessManager:
    """入退室管理の処理を行う本体
        クラスを作らなくてもいいのだがmysql.connector.connect()で生成したconnectorを
        使いまわしたかったのでこうした。global使うとスコープが分からなくなりそうだった。
        他にもっといい方法ありそう...

    Attributes
    ----------
        get_member : 学生証から読み取った学籍番号をメンバーの名前を対応させる
        cnx : mysql.connector.connection.MySQLConnection
        judge_action : 入室タッチか退室タッチか判定する

    """

    def __init__(self):
        self.cnx = None
        self.member_list = {}

    def connect_to_db(self, config): # config : <class 'dict'>
        """

        Parameters
        ----------
            config : dict
                mysql.connector.connect()に渡すパラメーター群
                設定できる値は以下のAPIリファレンスを参照のこと
                https://dev.mysql.com/doc/connector-python/en/connector-python-connectargs.html

        Returns
        -------
           bool
               SQLサーバーとの接続に成功したらTrue,それ以外はFalse

        """
        try:
            self.cnx = mc.connect(**config, buffered=True) # buffered : To avoid 'Unread result found' error.

        except mc.Error as e:
            print('[!] Error code: {}'.format(e.errno))
            print('[!] SQLSTATE value: {}'.format(e.sqlstate))
            print('[!] Error messsage: {}'.format(e.msg))
            return False
        
        with atclscur(self.cnx) as cur:
            cur.execute('SELECT id,name FROM member_list')
            response = cur.fetchall()
            for row in response:
                self.member_list[row[0]] = row[1]

        return True

    def run(self):
        """メインルーチン
        これがずっと回る

        """
        with nfc.ContactlessFrontend(PASORI_S380_PATH) as clf:
            while clf.connect(rdwr={'on-connect': self.on_connect}):
                pass

    def on_connect(self, tag):
        """This function is called when a remote tag has been activated.
            カードにアクセスできた後の処理はこの関数を起点にして行う

        Parameters
        ----------
            tag : nfc.tag.Tag

        Returns
        -------
            bool
               SQLサーバーにレコードを記録するところまで成功したらTrue,
               だめだったらFalse

        """
        try:
            sc = nfc.tag.tt3.ServiceCode(0x200B >> 6, 0x200B & 0x3f)
            bc = nfc.tag.tt3.BlockCode(0, service=0) # To get student ID
            block_data = tag.read_without_encryption([sc], [bc])

        except nfc.tag.TagCommandError as e:
            print('\033[01;31m[!] {}\n\033[01;33m[!] Too short. Please touch your card again\033[0m\n'.format(e)) # Text color red

        try:
            if not self.insert_record(block_data[1:9].decode('utf-8')): # Insert failue
                return False
        except UnboundLocalError: # local variable 'block_data' referenced before assignment
            print('\033[01;33m[!] Your card seems to be unavailable. \n[!] Is this really an ID card for Shizuoka University?\033[0m\n')

        return True

    def insert_record(self, student_id):
        """データベースにINSERT文かUPDATE文を発行して入退室記録をつける
           access_logにクエリを出す
           学籍番号にまつわるレコードのうち入室時間は記録されていて退室時間がNULLであるものを取ってくる
           そのようなレコードがなければ入室のアクションなので新たに挿入する(INSERT)
           そのようなレコードがあればそのレコードに対してexited_at列に退室時間を追加するという更新処理を施す(UPDATE)

        Parameters
        ----------
            student_id : str

        Returns
        -------
           bool
                INSERT(またはUPDATE)が成功したらTrue,それ以外ならFalse

        """
        with atclscur(self.cnx) as cur:
            cur.execute('SELECT student_id,entered_at FROM access_log WHERE student_id = {} AND exited_at IS NULL'.format(student_id))
            res = cur.fetchone()

        who = self.get_member(student_id)
        action = 'enter'
        query = 'INSERT INTO access_log (student_id,student_name) VALUES {}'.format(who) # enter
        if res != None:
            action = 'exit'
            query = 'UPDATE access_log SET exited_at=NOW() WHERE student_id = {} AND entered_at = \'{}\''.format(res[0], res[1]) # exit

        with atclscur(self.cnx) as cur:
            try:
                cur.execute(query)
                self.cnx.commit()

            except mc.Error as e:
                print('[!] Error code: {}'.format(e.errno))
                print('[!] SQLSTATE value: {}'.format(e.sqlstate))
                print('[!] Error messsage: {}'.format(e.msg))
                print('\033[01;31m[!] Return due to SQL error.\033[0m')
                return False

            soundutils.play_voice(action) # Greeting

            props = {'id': who[0], 'name': who[1], 'action': action}
            dispatcherutils.dispatch_touch_event(props) # Dispatch information on enttry/exited to View app
            return True

    def get_member(self, whose_id):
        """学籍番号をキーにして学籍番号と名前のタプルを返す
           学籍番号が登録されているもの以外だった場合は氏名を'Guest'として返す

        Parameters
        ----------
            whose_id : str
                学籍番号

        Returns
        -------
            tuple
                (学籍番号, 氏名)

        """
        if int(whose_id) in self.member_list:
            return (whose_id, self.member_list[int(whose_id)])
        
        else:
            return (whose_id, 'Guest') # Make sure to use 'tuple' (not 'list')

