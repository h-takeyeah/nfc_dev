import urllib.request
import json
from http import HTTPStatus

HOST = 'localhost'
PORT = 8000
def dispatch_touch_event(obj):
    """JSONをPOSTして入退室またはエラーが発生したことを伝える

    Parameters
    ----------
        obj : dict

    """

    json_data = json.dumps(obj).encode('utf-8')
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    req = urllib.request.Request(url='http://{}:{}'.format(HOST,PORT), headers=headers, data=json_data, method='POST')
 
    try: urllib.request.urlopen(req)
    except urllib.error.URLError as e:
        print('\033[;33m## == Info from DISPATCH_UTIL ==')
        print('##  \033[01;31m{}\033[;33m'.format(e))
        print('##  This is not a critical error, but sending to message to View app (monitor) has failed.\033[0m\n')
        pass

    return

