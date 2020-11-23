import sys
import json
import random
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from http import HTTPStatus

HOST = 'localhost'
PORT = 8000

"""適当なサーバーを立ててPOSTを受け取るだけ"""
class TestHandler(BaseHTTPRequestHandler):
    server_version = "HTTP Stub/0.1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        enc = sys.getfilesystemencoding()
        title = "HTTP Stub"

        r = []
        r.append('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                 '"http://www.w3.org/TR/html4/strict.dtd">')
        r.append('<html>\n<head>')
        r.append('<meta http-equiv="Content-Type" '
                 'content="text/html; charset=%s">' % enc)
        r.append('<title>%s</title>\n</head>' % title)
        r.append('<body>\n<h1>%s</h1>' % title)
        r.append('<hr>\n<ul>')
        r.append("Stub Opened.")
        r.append('</ul>\n<hr>\n</body>\n</html>\n')
        encoded = '\n'.join(r).encode(enc, 'surrogateescape')

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()

        self.wfile.write(encoded)

    def do_POST(self):

        length = self.headers.get('content-length')
        nbytes = int(length)
        #print(self.rfile)
        request_body = self.rfile.read(nbytes).decode('utf-8')
        #print(request_body)

        try:
            data = json.loads(request_body)

            for key in data:
                print('key:{0} value:{1}'.format(key, data[key]))

            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            if random.randrange(10) % 2: my_response = {'action': 'enter'}
            else: my_response = {'action': 'exit'}
            #self.wfile.write(json.dumps(my_response).encode('utf-8'))
            self.wfile.write(json.dumps({'action': 'error'}).encode('utf-8'))
            return

        except:
            self.send_error(400, 'request NG!')
            self.end_headers()
            return

if __name__ == "__main__":
    server = HTTPServer((HOST,PORT), TestHandler)
    server.serve_forever()
