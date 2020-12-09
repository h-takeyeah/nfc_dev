import os
import urllib.request
import urllib.error
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
ENDPOINT = os.getenv('AMS_ENDPOINT')

def ping_test():
    """expressサーバーの死活チェック(起動時)"""
    req = urllib.request.Request(url='http://{}'.format(ENDPOINT), method='GET')
    try: urllib.request.urlopen(req)
    except urllib.error.URLError as ue:
        return str(ue)

    return 'OK'

# cf. https://qiita.com/podhmo/items/dc748a9d40026c28556d
def support_datetune_default(o):
    """datetime型はそのままではJSONに乗せられないので文字列に変換してやる

    Parameters
    ----------
        o : Object (expected to be 'datetime')

    Returns
    -------
       str 

    Raises
    ------
        repr :
        TypeError :
        o :

    """
    if isinstance(o, datetime):
        return o.strftime('%H:%M')
    raise TypeError(repr(o) + 'is not JSON serializable')

def dispatch_touch_event(obj):
    """学籍番号をexpressサーバーに投げる

    Parameters
    ----------
        obj : dict

    """
    #if 'timestamp' not in obj:
    #    obj['timestamp'] = datetime.now()

    json_data = json.dumps(obj, default=support_datetune_default).encode('utf-8')
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    #req = urllib.request.Request(url='http://{}:{}/api/card_touched'.format(HOST,PORT), headers=headers, data=json_data, method='POST')
    req = urllib.request.Request(url='http://{}'.format(ENDPOINT), headers=headers, data=json_data, method='POST')
 
    try:
        with urllib.request.urlopen(req) as res:
            try:
                data = json.loads(res.read().decode()) # 'bytes' => 'str' => some object
                if isinstance(data, dict):
                    data['status'] = 'OK'
                    return data
                else: # デコードしてみたらdictじゃなかったとき。ほぼありえない
                    return {'status': 'NG'}

            except json.JSONDecodeError as jde: # デコードできなかったとき。これもほぼありえない
                print('\033[01;33m[!]\033[0m {}\n'.format(jde))
                return {'status': 'NG'}

    except urllib.error.URLError as ue:
        print('\033[01;33m[!]\033[0m {}\n'.format(ue))
        return {'status': 'NG'}

