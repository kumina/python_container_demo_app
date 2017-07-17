#!/usr/bin/env python3

import http.server
import prometheus_client

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


# A simple HTTP server class that makes use of http.server. For
# production applications, it makes a lot more sense to use Twisted or
# GUnicorn, as these provide better performance/scalability. This
# application is simple enough that http.server suffices.
#
# Notice that this class does not override the log_message() function.
# By default, this function logs requests to stderr. This is fine in our
# case, as stderr will be logged by Kubernetes by default. There is no
# need to write logs into files or to a remote server manually.
class MyWebpage(http.server.BaseHTTPRequestHandler):
    # This annotation causes the Prometheus client library to measure
    # the running time of this function.
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


if __name__ == '__main__':
    # Let the Prometheus client export its metrics on port 8080. It is
    # also possible to integrate these metrics into the public web
    # server under a special URL (e.g., "/metrics"). Using a separate
    # port has the advantage that it's unlikely that the metrics become
    # visible to the public by accident.
    prometheus_client.start_http_server(8080)
    # Let our web application run on port 80. It's perfectly fine to run
    # all of our web applications as root and let them listen on a
    # privileged port.
    httpd = http.server.HTTPServer(('0.0.0.0', 80), MyWebpage)
    httpd.serve_forever()
