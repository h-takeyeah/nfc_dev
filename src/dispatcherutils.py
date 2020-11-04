import urllib.request
import urllib.error
import json
from datetime import datetime

HOST = 'localhost'
PORT = 3001

# https://qiita.com/podhmo/items/dc748a9d40026c28556d
def support_datetune_default(o):
    if isinstance(o, datetime):
        return o.strftime('%H:%M')
    raise TypeError(repr(o) + 'is not JSON serializable')

def dispatch_touch_event(obj):
    """JSONをPOSTして入退室またはエラーが発生したことを伝える

    Parameters
    ----------
        obj : dict

    """
    if 'timestamp' not in obj:
        obj['timestamp'] = datetime.now()

    json_data = json.dumps(obj, default=support_datetune_default).encode('utf-8')
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    req = urllib.request.Request(url='http://{}:{}/api/card_touched'.format(HOST,PORT), headers=headers, data=json_data, method='POST')
 
    try: urllib.request.urlopen(req)
    except urllib.error.URLError as e:
        print('\033[;33m## == Info from DISPATCH_UTIL ==')
        print('## \033[01;31m{}\033[;33m'.format(e))
        print('## Sending a message to Viewer failed. (not serious)\033[0m\n')
        pass

    return

