import urllib.request
import urllib.error
import json
from pathlib import Path

API_ENDPOINT = 'localhost:3000'
API_VERSION = 'v1'

def ping_test():
    """expressサーバーの死活チェック(起動時)"""
    req = urllib.request.Request(url='http://{}'.format(API_ENDPOINT, API_VERSION), method='GET')
    try:
        urllib.request.urlopen(req)
        pass
    except urllib.error.URLError as ue:
        print(str(ue))
        return str(ue)
    except Exception as e:
        print(str(e))
        import sys
        return str(sys.exc_info()[0])

    return 'OK'

def dispatch_touch_event(obj):
    """学籍番号をexpressサーバーに投げる

    Parameters
    ----------
        obj : dict

    """

    json_data = json.dumps(obj).encode('utf-8')
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    req = urllib.request.Request(url='http://{}'.format(ENDPOINT), headers=headers, data=json_data, method='POST')
 
    try:
        with urllib.request.urlopen(req) as res:
            pass

    except urllib.error.URLError as ue:
        print('\033[01;33m[!]\033[0m {}\n'.format(ue))
        return {'status': 'NG'}
    
    else:
        try:
            data = json.loads(res.read().decode()) # 'bytes' => 'str' => some object

        except json.JSONDecodeError as jde: # デコードできなかったとき。これもほぼありえない
            print('\033[01;33m[!]\033[0m {}\n'.format(jde))
            return {'status': 'NG'}

        else:
            if isinstance(data, dict):
                data['status'] = 'OK'
                return data
            else: # デコードしてみたらdictじゃなかったとき。ほぼありえない
                return {'status': 'NG'}

