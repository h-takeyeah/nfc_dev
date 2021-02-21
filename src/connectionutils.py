import json
import urllib.error as ue
import urllib.request as ur
from http import HTTPStatus

API_ENDPOINT = 'http://localhost:8000/room'


def do_request(req):
    try:
        with ur.urlopen(req) as res:
            return res.status
    except ue.HTTPError as e:  # 4xx, 5xx
        return e.code
    except Exception:
        raise


def ping_test():
    req = ur.Request(url=API_ENDPOINT)
    try:
        if (do_request(req) == HTTPStatus.OK):
            return
    except Exception as e:
        print(e)
        return False


def is_inroom(parsed_id):
    req = ur.Request(url='{}/{}'.format(API_ENDPOINT, parsed_id))
    return (do_request(req) == HTTPStatus.OK)


def enter_room(parsed_id):
    data = json.dumps({'id': parsed_id}).encode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    req = ur.Request(
        url=API_ENDPOINT, data=data,
        headers=headers, method='POST')
    return (do_request(req) == HTTPStatus.CREATED)


def leave_room(parsed_id):
    req = ur.Request(
        url='{}/{}'.format(API_ENDPOINT, parsed_id), method='DELETE')
    return (do_request(req) == HTTPStatus.NO_CONTENT)
