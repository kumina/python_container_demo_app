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
* Explicit declaration of dependencies (via requirements.txt)
* A crude example on how to format the output into JSON, so it can more easily
  be parsed by Logstash and ElasticSearch
  * Also, send the logs to stdout
* Handle a SIGTERM gracefully, as this is how Kubernetes would stop a Pod

## Todo

* Horizontal Pod Scaling metrics
* Actual Deployment specification for Kubernetes

## Notes:

* Services are of type Nodeport (because it's used on local dev clusters.)


## Helper script
ENV variable: `BUILD_REGISTRY` can be set when you want to build the image with registry prefix.

Example: `export BUILD_REGISTRY=registry.example.com/common/`

options:
- first argument is the directory ID to build and run
- second argument is the action to take
  * `norun` - will only build the image
  * `docker` - will build the image and run it in your local docker
  * `kind` - will build the image and load it into kind and run it on your current context's cluster (which should be kind)
  * `registry` - will build the image and push it to the registry and run it on your current context's cluster
  * `(default)`- will build the image without pushing and run it on your current context's cluster

```bash
./build-run-dir.sh 01 docker 

./build-run-dir.sh 02 kind 

./build-run-dir.sh 03 

BUILD_REGISTRY=registry.example.com/common/ ./build-run-dir.sh 04
```
