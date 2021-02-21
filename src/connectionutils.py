import json
import sys
import urllib.error as ue
import urllib.request as ur
from http import HTTPStatus

API_ENDPOINT = 'http://localhost:8000/room'


def open_url(req):
    try:
        with ur.urlopen(req) as res:
            return res.status
    except ue.HTTPError as e:
        return e.code
    except ue.URLError as e:
        print('URLError:', e.reason, file=sys.stderr)
        return -1
    except Exception:
        print('Unexpected error:', sys.exc_info()[0], file=sys.stderr)
        return -1


def ping_test():
    req = ur.Request(url=API_ENDPOINT)
    return (open_url(req) == HTTPStatus.OK)


def is_inroom(parsed_id):
    req = ur.Request(url='{}/{}'.format(API_ENDPOINT, parsed_id))
    return (open_url(req) == HTTPStatus.OK)


def enter_room(parsed_id):
    data = json.dumps({'id': parsed_id}).encode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    req = ur.Request(
        url=API_ENDPOINT, data=data,
        headers=headers, method='POST')
    return (open_url(req) == HTTPStatus.CREATED)


def leave_room(parsed_id):
    req = ur.Request(
        url='{}/{}'.format(API_ENDPOINT, parsed_id), method='DELETE')
    return (open_url(req) == HTTPStatus.NO_CONTENT)
