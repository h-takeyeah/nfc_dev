#!/usr/bin/env python3

import json
import nfc
import mysql.connector as mc
from datetime import datetime
from closable_cursor import ClosableCursor as clscur

PASORI_S380_PATH = 'usb:054c:06c3' 
CONFIG_FILE = 'config.json'

class manager:
    PASORI_S380_PATH = 'usb:054c:06c3'
    def __init__(self):
        self.cnx = None

    def connect_to_db(self, config): # config : <class 'dict'>
        try:
            self.cnx = mc.connect(**config, buffered=True) # buffered : To avoid 'Unread result found' error.
            return True

        except mc.Error as e:
            print('Error code: {}'.format(e.errno))
            print('SQLSTATE value: {}'.format(e.sqlstate))
            print('Error messsage: {}'.format(e.msg))
            print('\033[01;31mStop\033[0m')
            return False

    def run(self):
        with nfc.ContactlessFrontend(PASORI_S380_PATH) as clf:
            while clf.connect(rdwr={'on-connect': self.on_connect}):
                pass
                

    def sc_from_raw(self, sc):
        return nfc.tag.tt3.ServiceCode(sc >> 6, sc & 0x3f)

    

    def on_connect(self, tag):
        try:
            sc = self.sc_from_raw(0x200B)
            bc = nfc.tag.tt3.BlockCode(0, service=0) # To get student ID
            block_data = tag.read_without_encryption([sc], [bc])

        except nfc.tag.TagCommandError as e:
            print('\033[01;31m{}\n\033[01;33mToo short. Please touch your card again\033[0m'.format(e)) # Text color red

        if not self.insert_record(block_data[1:9].decode('utf-8')): # Insert failue
            return False

        return True

    def insert_record(self, student_id):
        estimated_action = self.which_action(student_id)
        print('estimated_action is ' + estimated_action)
        whois = self.get_member(student_id) # whois : (student_id, name) 
        query = ''

        if estimated_action == 'enter':
            query = 'INSERT INTO room_entries (student_id, student_name) VALUES {}'.format(whois)
 
        elif estimated_action == 'exit':
            query = 'INSERT INTO room_exits (student_id, student_name) VALUES {}'.format(whois)

        elif estimated_action == 'error':
            print('\033[01;31mThere is some error in log table.\033[0m')
            return False

        with clscur(self.cnx) as cur:
            try:
                cur.execute(query)
                self.cnx.commit()
                return True

            except mc.Error as e:
                print('Error code: {}'.format(e.errno))
                print('SQLSTATE value: {}'.format(e.sqlstate))
                print('Error messsage: {}'.format(e.msg))
                print('\033[01;31mStop\033[0m')
                return False

    def which_action(self, student_id):
        with clscur(self.cnx) as cur:
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
        with clscur(self.cnx) as cur:
            cur.execute('SELECT id,name FROM active_members WHERE id = {}'.format(whose_id))
            member_record = cur.fetchone()
        
        if member_record == None:
            member_record = (whose_id, 'Unknown student') # Make sure to use 'tuple' (not 'list')
        
        return member_record

    def get_now(self):
        return datetime.now().isoformat(' ', 'seconds')
    
def main():
    print('\033[01;32mGood morning!\033[0m\nPlease wait.')
    with open(CONFIG_FILE) as f:
        config = json.load(f).get('sql_connector_parameters').get('parameter1') # <class 'dict'>
    
    print('Trying to establish connection to {}... '.format(config.get('database')), end='')
    
    m = manager()
    if not m.connect_to_db(config):
        print('\033[01;31mStop\033[0m')
        exit()
    else:
        print('Success')

    m.run()

if __name__ == "__main__":
    main()

