#!/usr/bin/env python3

import json
from access_manager import AccessManager

CONFIG_FILE = 'config.json'

print('[*] \033[01;32mHello!\033[0m\n[*] Please wait.') # green
with open(CONFIG_FILE) as f:
    config = json.load(f).get('sql_connector_parameters').get('default') # <class 'dict'>

manager = AccessManager()

print('[*] Trying to establish connection to {}... '.format(config.get('database')), end='')
if not manager.connect_to_db(config):
    print('\033[01;31m[!] Stop\033[0m') # red
    exit()
else:
    print('Success')

print('[*] \033[01;32mNow main routine started -- Press Ctrl+C to stop.\033[0m\n')
manager.run()
