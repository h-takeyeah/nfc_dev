#!/usr/bin/env python3

import urllib.request
import json
from http import HTTPStatus

def dispatch_touch_event(obj):
    """入退室またはエラーが発生したことを伝える

    Parameters
    ----------
        obj : dict

    """

    json_data = json.dumps(obj).encode('utf-8')
    headers = {'Content-Type' : 'application/json'}

    req = urllib.request.Request(url='http://localhost:8000', data=json_data, method='POST')
    with urllib.request.urlopen(req) as res:
        pass

    return
