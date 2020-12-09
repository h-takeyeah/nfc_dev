import nfc
import mysql.connector as mc
from auto_close_cursor import AutoCloseCursor as atclscur
import soundutils as su
import dispatcherutils

PASORI_S380_PATH = 'usb:054c:06c3'

class AccessManager:
    """入退室管理の処理を行う本体
        クラスを作らなくてもいいのだがmysql.connector.connect()で生成したconnectorを
        使いまわしたかったのでこうした。global使うとスコープが分からなくなりそうだった。
        他にもっといい方法ありそう...

    Attributes
    ----------
        cnx : mysql.connector.connection.MySQLConnection
        judge_action : 入室タッチか退室タッチか判定する

    """

    def __init__(self):
        self.cnx = None
        self.member_list = set()
        self.allow_guest = True

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
            cur.execute('SELECT id FROM member_list')
            response = cur.fetchall()
            for row in response:
                self.member_list.add(row[0])

        return True

    def set_allow_guest(self, allow_guest):
        """

        Parameters
        ----------
            allow_guest : bool
                登録されていない人を記録するかどうか

        Returns
        -------

        """
        self.allow_guest = allow_guest
        return

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
            bc = nfc.tag.tt3.BlockCode(0, service=0) # To get member ID
            block_data = tag.read_without_encryption([sc], [bc])

        # cf. https://github.com/nfcpy/nfcpy/blob/master/src/nfc/tag/__init__.py
        except nfc.tag.TagCommandError as e:
            su.play_voice('warning')
            if e.errno == 0x1A6: # 0x01A6 => "invalid service code number or attribute"
                print('\033[01;33m[!]\033[0m Your IC card seems to be unavailable. Is it valid one?\n')
                return False
            elif e.errno == 0x0: # nfc.tag.TIMEOUT_ERROR => "unrecoverable timeout error"
                print('\033[01;33m[!]\033[0m Too short. Please touch your card again\n') # Text color red
                return False
            else:
                print('\033[01;33m[!]\033[0m {}\n'.format(e))
                return False

        if not self.insert_record(int(block_data[1:9].decode('utf-8'))): # Insert failue
            return False

        return True

    def insert_record(self, member_id):
        """データベースにINSERT文かUPDATE文を発行して入退室記録をつける
           access_logにクエリを出す
           学籍番号にまつわるレコードのうち入室時間は記録されていて退室時間がNULLであるものを取ってくる
           そのようなレコードがなければ入室のアクションなので新たに挿入する(INSERT)
           そのようなレコードがあればそのレコードのexited_at列を現在時刻で更新する(UPDATE)

        Parameters
        ----------
            member_id : int

        Returns
        -------
           bool
                INSERT(またはUPDATE)が成功したらTrue,それ以外ならFalse

        """
        if member_id not in self.member_list: # is member?
            print('\033[01;33m[!]\033[0m Your ID is not registered.\n')
            if self.allow_guest:
                su.play_voice('not_registered')
                pass
            else:
                su.play_voice('error')
                return False

        with atclscur(self.cnx) as cur:
            cur.execute('SELECT member_id,entered_at FROM access_log WHERE member_id = {} AND exited_at IS NULL'.format(member_id))
            res = cur.fetchone()

        action = 'enter'
        query = 'INSERT INTO access_log (member_id) VALUES ({})'.format(member_id) # enter
        if res != None:
            action = 'exit'
            query = 'UPDATE access_log SET exited_at=NOW() WHERE member_id = {} AND entered_at = \'{}\''.format(res[0], res[1]) # exit

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

            su.play_voice(action) # Greeting

            props = {'id': member_id, 'action': action}
            dispatcherutils.dispatch_touch_event(props) # Dispatch information on enttry/exited to View app
            return True

