from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import datetime

import zope.event
from cgi import parse_header, parse_multipart, parse_qs
import json
from logger import Logger

class ThreadedHTTPServer(HTTPServer):
    def process_request(self, request, client_address):
        thread = Thread(target=self.__new_request, args=(self.RequestHandlerClass, request, client_address, self))
        thread.start()
    def __new_request(self, handlerClass, request, address, server):
        handlerClass(request, address, server)
        self.shutdown_request(request)

class ServerHandler(BaseHTTPRequestHandler):
    def parse_POST(self):
      ctype, pdict = parse_header(self.headers.getheader('content-type'))
      if ctype == 'application/json':
        length = int(self.headers.getheader('content-length'))
        data = parse_qs(self.rfile.read(length), keep_blank_values=1)
        # print('json '+str(data)[2:-8])
        return json.loads(str(data)[2:-8])
      else:
          postvars = {}

    def do_POST(self):
        #print('do_POST Called!!! ' + str(datetime.datetime.now()))
        params = self.parse_POST()
        # print(params)
        zope.event.notify(params)
        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        self.end_headers()
        self.wfile.write("{'x':'y'}")

    def log_message(self, format, *args):
        return        

class WebhookServer(object):

    def __init__(self, host, port):
        self.server = ThreadedHTTPServer((host, port), ServerHandler)
        self.server_thread = Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def start(self):
        self.server_thread.start()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()        
