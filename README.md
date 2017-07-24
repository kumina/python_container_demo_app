# Python Example App for Kubernetes

Developing for Kubernetes is not very hard, but there are some things that one
needs to keep in mind to make it all work correctly. This simple example project
hopes to show off some of the features that you should be setting up in your
application (whether it is Python or some other language) to make it work nicely
with Kubernetes and Prometheus.

What this script shows:

* Prometheus metrics
  * Using a different port (optional)
  * Gathering the metrics with a client library
* Settable ports on which the application listens for incoming requests
* Settable config options which can be used for connecting to databases and the
  like
* Liveness check, to make sure an unresponsive container will be restarted by
  Kubernetes
* Readiness check, to determine when a container is done with starting up
* Sending logs to stdout for easy capture outside of the container (not really
  shown, as this is the default for http.server.BaseHTTPRequestHandler)
* Explicit declaration of dependencies (via requirements.txt)

## Todo

* Format log output as JSON, so we can parse it easily with Logstash and store
  it in ElasticSearch
* Horizontal Pod Scaling metrics
* Actual Deployment specification for Kubernetes
