#!/usr/bin/env python3

import json
import nfc
import mysql.connector as mc
from datetime import datetime

PASORI_S380_PATH = 'usb:054c:06c3' 
CONFIG_FILE = 'config.json'

class manager:
    PASORI_S380_PATH = 'usb:054c:06c3'
    def __init__(self):
        self.cnx = None

    def connect_to_db(self, config): # config : <class 'dict'>
        try:
            self.cnx = mc.connect(**config)
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

        who = get_member(block_data[1:9].decode('utf-8'))
        if who = None:
            print('Unknown')
        
        

    def get_now():
        return datetime.now().isoformat(' ', 'seconds')

def on_connect(tag):
    print('connect yade!!!')

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

    with nfc.ContactlessFrontend(PASORI_S380_PATH) as clf:
        while clf.connect(rdwr={'on-connect': on_connect}):
            pass

        #print('Closing sql connector...', end='')
        #cnx.close()
        #print('OK')
        #print(Bye)
        #exit()

if __name__ == "__main__":
    main()

