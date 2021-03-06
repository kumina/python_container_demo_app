#!/usr/bin/env python3

import http.server
import sys
import threading
import signal
import json
import prometheus_client


REQUEST_LATENCY = prometheus_client.Histogram(
    'my_webpage_request_latency_seconds',
    'Time it took to process incoming HTTP requests, in seconds.')


class MyWebpage(http.server.BaseHTTPRequestHandler):
    @REQUEST_LATENCY.time()
    def do_GET(s):
        s.send_response(200)
        s.send_header('Content-Type', 'text/html')
        s.end_headers()
        s.wfile.write(b'''
<!DOCTYPE html>
<html>
    <head>
        <title>Hello!</title>
    </head>
    <body>
        <p>This is a demo page!</p>
    </body>
</html>''')

    def log_message(self, format, *args):
        log = {
            'timestamp': self.log_date_time_string(),
            'my_webserver':
                {
                   'client_ip': self.address_string(),
                   'message': format % args
                }
        }
        print(json.dumps(log))


if __name__ == '__main__':
    def do_shutdown(signum, frame):
        threading.Thread(target=httpd.shutdown).start()
        sys.exit(0)

    signal.signal(signal.SIGTERM, do_shutdown)

    prometheus_client.start_http_server(9999)
    httpd = http.server.HTTPServer(('0.0.0.0', 8080), MyWebpage)
    httpd.serve_forever()