#!/usr/bin/env python3

import http.server


class MyWebpage(http.server.BaseHTTPRequestHandler):
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


if __name__ == '__main__':
    httpd = http.server.HTTPServer(('127.0.0.1', 8080), MyWebpage)
    httpd.serve_forever()
