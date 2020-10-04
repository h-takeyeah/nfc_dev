import json
import nfc
import mysql.connector as mc
from collections import namedtuple
from auto_close_cursor import AutoCloseCursor as atclscur
import sound_util
import dispatch_util

class manager:
    """入退室管理の処理を行う本体
        クラスを作らなくてもいいのだがmysql.connector.connect()で生成したconnectorを
        使いまわしたかったのでこうした。global使うとスコープが分からなくなりそうだった。
        他にもっといい方法ありそう...

    Attributes
    ----------
        get_member : 学生証から読み取った学籍番号をメンバーの名前を対応させる
        cnx : mysql.connector.connection.MySQLConnection
        which_action : 入室タッチか退室タッチか判定する

    """
    PASORI_S380_PATH = 'usb:054c:06c3' 
    
    def __init__(self):
        self.cnx = None

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
            return True

        except mc.Error as e:
            print('Error code: {}'.format(e.errno))
            print('SQLSTATE value: {}'.format(e.sqlstate))
            print('Error messsage: {}'.format(e.msg))
            return False

    def run(self):
        """メインルーチン
        これがずっと回る

        """
        with nfc.ContactlessFrontend(self.PASORI_S380_PATH) as clf:
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
            which_action()に今のタッチが入室なのか退室なのかを判定させる
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
        estimated_action = self.which_action(student_id)
        whois = self.get_member(student_id) # whois : (student_id, name)
        query = ''

        if estimated_action == 'enter':
            query = 'INSERT INTO room_entries (student_id, student_name) VALUES {}'.format(whois)
 
        elif estimated_action == 'exit':
            query = 'INSERT INTO room_exits (student_id, student_name) VALUES {}'.format(whois)

        elif estimated_action == 'error':
            query = 'INSERT INTO error_log (student_id, student_name) VALUES {}'.format(whois)
            print('\033[01;31mThere is some error in log table.\033[0m')

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

            sound_util.play_voice(estimated_action) # Greeting

            state = {'id': whois[0], 'name': whois[1], 'action': estimated_action}
            dispatch_util.dispatch_touch_event(state) # Dispatch information on enttry/exited to View app
            return True

    def which_action(self, student_id):
        """今のタッチが入室のタッチなのかそれとも退室のタッチなのかを判定する

        Parameters
        ----------
            student_id : str

        Returns
        -------
            str
                入室なら'enter'、退室なら'exit'。またレコードをチェックした際に
                対応する入室記録が無いのに退室記録だけあったことが分かったら'error'
                'error'はテーブルがまっさらな状態でプログラムをスタートさせれば、
                テーブルをUPDATEしない限り発生しないはず...

        """
        with atclscur(self.cnx) as cur:
            cur.execute('SELECT entered_at FROM room_entries WHERE student_id = {} AND DATE(entered_at) >= CURRENT_DATE() AND DATE(entered_at) < DATE_ADD(CURRENT_DATE(), INTERVAL 1 DAY) ORDER BY entered_at DESC LIMIT 1'.format(student_id))
            last_entered_at = cur.fetchone()
            
            cur.execute('SELECT exited_at FROM room_exits WHERE student_id = {} AND DATE(exited_at) >= CURRENT_DATE() AND DATE(exited_at) < DATE_ADD(CURRENT_DATE(), INTERVAL 1 DAY) ORDER BY exited_at DESC LIMIT 1'.format(student_id))
            last_exited_at = cur.fetchone()
                        
            if last_entered_at == None and last_exited_at != None: # Only exit log exists. (=has no pair) # Irregular
                return 'error'
            
            elif last_entered_at == None or last_exited_at == None:
                if last_entered_at == None and last_exited_at == None: # First access
                    return 'enter'
                elif last_entered_at != None and last_exited_at == None: # In room, he is about to exit. (second access)
                    return 'exit'

            else: # Regular
                if last_entered_at > last_exited_at:
                    return 'exit'
                else:
                    return 'enter'

    def get_member(self, whose_id):
        """member_listテーブルから与えられた学籍番号と紐づく氏名を取ってくる
            学籍番号が登録されているもの以外だった場合は氏名を'Unknown'として返す

        Parameters
        ----------
            whose_id : str
                学籍番号

        Returns
        -------
            tuple
                INSERT文にそのまま使えるように(学籍番号,氏名)の形式で返す

        """
        with atclscur(self.cnx) as cur:
            cur.execute('SELECT id,name FROM member_list WHERE id = {}'.format(whose_id))
            member_record = cur.fetchone()

        if member_record == None:
            member_record = (whose_id, 'Unknown student') # Make sure to use 'tuple' (not 'list')

        return member_record

