#!/usr/bin/env python3

import json
from access_manager import AccessManager

CONFIG_FILE = 'config.json'

print('[*] \033[01;32mHello!\033[0m\n[*] Please wait.') # green
with open(CONFIG_FILE) as f:
    json_data = json.load(f)
    config = json_data.get('sql_connector_parameters').get('default') # <class 'dict'>
    allow_guest = json_data.get('allow_guest')

manager = AccessManager()

print('[*] Trying to establish connection to {}... '.format(config.get('database')), end='')
if not manager.connect_to_db(config):
    print('\033[01;31m[!] Stop\033[0m') # red
    exit()
else:
    print('Success')

manager.set_allow_guest(allow_guest) # accept not registered person or not

print('[*] \033[01;32mNow main routine started -- Press Ctrl+C to stop.\033[0m\n')
manager.run()
