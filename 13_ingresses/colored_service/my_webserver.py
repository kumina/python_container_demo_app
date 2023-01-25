#!/usr/bin/env python3

import os
import sys
import http.server
import prometheus_client
import json
import signal
import threading

# Collecting useful metrics.
#
# Applications running on Kubernetes may be highly distributed, meaning
# that it's very important to have metrics available to aid debugging.
# At Kumina, we make use of Prometheus to monitor our infrastructure.
# Prometheus scrapes processes by sending them HTTP GET requests,
# expecting that the target responds with a list of (labelled) key-value
# pairs.
#
# Let's declare a histogram that we can use to keep track of the latency
# of incoming HTTP requests. Histograms consist of a count (the number
# of requests), the sum (the total amount of latency in seconds) and
# buckets that keep track of the distribution of samples.
#
# Please take some time to read Prometheus' best practices on metric and
# label naming, to ensure your app uses a consistent naming scheme:
# https://prometheus.io/docs/practices/naming/
#
# Note that it's all right to extend this histogram to keep track of
# these stats per hostname, but never add the request URI as a label, as
# this would cause HTTP scans to blow up the size of the histogram!
REQUEST_LATENCY = prometheus_client.Histogram(
    'my_webpage_request_latency_seconds',
    'Time it took to process incoming HTTP requests, in seconds.')

ready = False
color = 'black'

# A simple HTTP server class that makes use of http.server. For
# production applications, it makes a lot more sense to use Twisted or
# GUnicorn, as these provide better performance/scalability. This
# application is simple enough that http.server suffices.
class MyWebpage(http.server.BaseHTTPRequestHandler):
    # This decorator causes the Prometheus client library to measure
    # the running time of this function.
    @REQUEST_LATENCY.time()
    def do_GET(s):
        if s.path == '/healthz/live':
            s.liveness_check()
        elif s.path == '/healthz/ready':
            s.readiness_check()
        else:
            s.default_response()

    # We respond with a simple page on most requests.
    def default_response(s):
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
                    <p><font color="%s">This is a demo page!</font></p>
                </body>
            </html>''' % color.encode('utf-8'))

    # This is the liveness check that we setup in Kubernetes for monitoring
    # the instance. A liveness check that fails will trigger a restart of
    # a Pod. Liveness checks are generally performed every 10 seconds (but
    # this is configurable). This behaviour makes this check ideal for making
    # sure the app is still running correctly by adding in additional internal
    # checks that would trigger a failure of this check in case of problems.
    # If this check fails, the Pod will be restarted.
    def liveness_check(s):
        s.send_response(200)
        s.send_header('Content-Type', 'text/html')
        s.end_headers()
        s.wfile.write(b'''Ok.''')

    # A readiness check indicates whether a Pod is ready to receive traffic.
    # Failing a readiness check will not make the Pod restart itself, it will
    # just be removed as an EndPoint until the check succeeds again. This can
    # be used to allow a container to do some initialisation during startup and
    # even to put a Pod in 'maintenance mode'.
    def readiness_check(s):
        if ready:
            s.send_response(200)
            s.send_header('Content-Type', 'text/plain')
            s.end_headers()
            s.wfile.write(b'''Ok.''')
        else:
            # The actual response does not really matter, as long as it's not
            # a HTTP 200 status.
            s.send_response(503)
            s.send_header('Content-Type', 'text/plain')
            s.end_headers()
            s.wfile.write(b'''Not ready yet.''')

    # Here we deal with the log output. This needs to be a unique key, as
    # ElasticSearch will set a data type for a specific key and will reject
    # all log messages that contain the same key but with a different data
    # type. So we start with the top level element 'my_webserver', so all
    # keys are unique (my_webserver.client_ip, my_webserver.timestamp and
    # my_webserver.message).
    #
    # Note here, that it is left as an exercise for the reader to split up
    # the content of 'message' even better. This is considered outside the
    # scope of this example. If you're interested in doing so, check the source
    # of BaseHTTPRequestHandler and override the method 'log_request'.
    def log_message(self, format, *args):
        log = { 'my_webserver':
                {
                    'client_ip': self.address_string(),
                    'timestamp': self.log_date_time_string(),
                    'message': format % args
                }
            }
        print(json.dumps(log))


if __name__ == '__main__':
    # First we collect the environment variables that were set in either
    # the Dockerfile or the Kubernetes Pod specification.
    listen_port = int(os.getenv('LISTEN_PORT', 80))
    prom_listen_port = int(os.getenv('PROM_LISTEN_PORT', 8080))
    database_host = os.getenv('DATABASE_HOST', 'mysql')
    database_port = int(os.getenv('DATABASE_PORT', 3306))
    shared_storage_path = os.getenv('SHARED_STORAGE_PATH', '/shared')
    color = int(os.getenv('APP_COLOR', 'black'))
    # Let the Prometheus client export its metrics on a separate port. It
    # is also possible to integrate these metrics into the public web
    # server under a special URL (e.g., "/metrics"). Using a separate
    # port has the advantage that it's unlikely that the metrics become
    # visible to the public by accident.
    prometheus_client.start_http_server(prom_listen_port)
    # Let our web application run and listen on the specified port. It's
    # perfectly fine to run # all of our web applications as root and let
    # them listen on a privileged port.
    httpd = http.server.HTTPServer(('0.0.0.0', listen_port), MyWebpage)
    httpd.database_host = database_host
    httpd.database_port = database_port
    httpd.shared_storage_path = shared_storage_path
    # Make sure you have the webserver signal when it's done. You can see
    # this in action a bit better by adding a delay (time.sleep(5)), so
    # you can see that it actually takes a little while before the Pod
    # becomes Healthy.
    ready = True

    # Simple handler function to show that we are handling the SIGTERM
    def do_shutdown(signum, frame):
        global httpd

        log = {'my_webserver': {'message': 'Graceful shutdown.'}}
        print(json.dumps(log))
        threading.Thread(target=httpd.shutdown).start()
        sys.exit(0)

    # We catch the SIGTERM signal here and shut down the HTTPServer
    signal.signal(signal.SIGTERM, do_shutdown)

    # Forever serve requests. Or at least until we receive the proper signal.
    httpd.serve_forever()
