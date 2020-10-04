#!/usr/bin/env python3

import json
import gate_manager

CONFIG_FILE = 'config.json'

print('[msg] \033[01;32mHello!\033[0m\n[msg] Please wait.') # green
with open(CONFIG_FILE) as f:
    config = json.load(f).get('sql_connector_parameters').get('default') # <class 'dict'>

m = gate_manager.manager()

print('[msg] Trying to establish connection to {}... '.format(config.get('database')), end='') 
if not m.connect_to_db(config):
    print('\033[01;31mStop\033[0m') # red
    exit()
else:
    print('Success')

print('[msg] \033[01;32mNow main routine started -- Press Ctrl+C to stop.\033[0m\n')
m.run()

