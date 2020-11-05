import nfc
import mysql.connector as mc
import time
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
            print('Error code: {}'.format(e.errno))
            print('SQLSTATE value: {}'.format(e.sqlstate))
            print('Error messsage: {}'.format(e.msg))
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
            print('\033[01;31m{}\n\033[01;33mToo short. Please touch your card again\033[0m'.format(e)) # Text color red

        if not self.insert_record(block_data[1:9].decode('utf-8')): # Insert failue
            return False

        return True

    def insert_record(self, student_id):
        """INSERT文を発行する。またそのための下準備を各関数に命令する
            judge_action()に今のタッチが入室なのか退室なのかを判定させる
            get_member()に学籍番号と紐づく名前を取ってこさせる
            もろもろ大丈夫そうならINSERTする

        Parameters
        ----------
            student_id : str

        Returns
        -------
           bool
                INSERTが成功したらTrue,それ以外ならFalse

        """
        estimated_action = self.judge_action(student_id)
        value = self.get_member(student_id) # who : (student_id, name)
        value.append(time.strftime('%Y-%m-%d %H:%M:%S'))
        value = tuple(value)
        query = ''

        if estimated_action == 'enter':
            query = 'INSERT INTO access_log (student_id, student_name, exited_at) VALUES {}'.format(value)
        elif estimated_action == 'exit':
            query = 'INSERT INTO access_log (student_id, student_name, entered_at) VALUES {}'.format(value)

        print(query)

        #elif estimated_action == 'error':
        #    query = 'INSERT INTO error_log (student_id, student_name) VALUES {}'.format(who)
        #    print('\033[01;31mThere is some error in erroe_log table.\033[0m')

        with atclscur(self.cnx) as cur:
            try:
                cur.execute(query)
                self.cnx.commit()

            except mc.Error as e:
                print('Error code: {}'.format(e.errno))
                print('SQLSTATE value: {}'.format(e.sqlstate))
                print('Error messsage: {}'.format(e.msg))
                print('\033[01;31mReturn\033[0m')
                return False

            #soundutils.play_voice(estimated_action) # Greeting

            props = {'id': value[0], 'name': value[1], 'action': estimated_action}
            dispatcherutils.dispatch_touch_event(props) # Dispatch information on enttry/exited to View app
            return True

    def judge_action(self, student_id):
        """今のタッチが入室のタッチなのかそれとも退室のタッチなのかを判定する

        Parameters
        ----------
            student_id : str

        Returns
        -------
            str
                在室中(in)なら退室時のタッチと判定して'exit'、そうでなかったら'enter'を返す

        """
        with atclscur(self.cnx) as cur:
            cur.execute('SELECT mode FROM in_room WHERE id = {}'.format(student_id))
            mode = cur.fetchone()
            self.switch_mode(student_id)
            return 'exit' if mode != None and mode == 'in' else 'enter'

    def switch_mode(self, student_id):
        #with atclscur(self.cnx) as cur:
        #    cur.execute('REPLACE INTO in_room')
        return

    def get_member(self, whose_id):
        """学籍番号をキーにして学籍番号と名前のタプルを返す
            学籍番号が登録されているもの以外だった場合は氏名を'Unknown'として返す

        Parameters
        ----------
            whose_id : str
                学籍番号

        Returns
        -------
            list
                [学籍番号,氏名]

        """
        if int(whose_id) in self.member_list:
            return [whose_id, self.member_list[int(whose_id)]]
        
        else:
            return [whose_id, 'Unknown student'] # Make sure to use 'tuple' (not 'list')

