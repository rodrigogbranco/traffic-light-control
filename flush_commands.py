from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import datetime

class ThreadedHTTPServer(HTTPServer):
    def process_request(self, request, client_address):
        thread = Thread(target=self.__new_request, args=(self.RequestHandlerClass, request, client_address, self))
        thread.start()
    def __new_request(self, handlerClass, request, address, server):
        handlerClass(request, address, server)
        self.shutdown_request(request)

class ServerHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        print('do_POST Called ' + str(datetime.datetime.now()))
        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        self.end_headers()
        self.wfile.write("{'x':'y'}")

if __name__ == "__main__":
    server = ThreadedHTTPServer(('', 7000), ServerHandler)
    print('Starting server...')
    server.serve_forever()