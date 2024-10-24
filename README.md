[![codecov](https://codecov.io/gh/idjaw/edunet/graph/badge.svg?token=5MZIOFVHA9)](https://codecov.io/gh/idjaw/edunet)
![PyPI - Version](https://img.shields.io/pypi/v/edunet)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/edunet)
[![EduNet](https://github.com/idjaw/edunet/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/idjaw/edunet/actions/workflows/test.yml)

# EduNet
This application allows you to simulate different network operations in a simple plug-in manner.

The motivation with this project was to simply learn more about sockets, protocols, and making them all talk to one another.

The end result of this project is to be able to craft together any network entities and have them communicate as intended.

## Simple Supported Use Case

There is a built-in simple supported use case called SimpleHTTPNode.

Bringing this up will start a TCP listener on localhost on port 9999 accepting valid HTTP requests.
What will be sent back are valid HTTP responses.

## Complex Use Cases

As it will be supported soon, the intent is by using the core architecture,
we will be able to implement a router with basic features like:

- Routing table
- DHCP assignment
- Packet forwarding
- Network Access Translation (NAT)

## Simple Example to put it all together

### Installing
```shell
pip install edunet
```

### Usage
Going back to the Simple use case, as is you can simply do something like:

#### Starting service

```python
from edunet.core.applications.simple_http_application import SimpleHTTPApplication
from edunet.core.networking.handlers.simple_http_connection_handler import SimpleHTTPConnectionHandler
from edunet.core.networking.listeners.tcp_listener import TCPListener 

# create an HTTP application 
app = SimpleHTTPApplication()

# create a Connection Handler that takes an application
handler = SimpleHTTPConnectionHandler(app)

# A listener is needed to allow connections to come through
listener = TCPListener("127.0.0.1", 9999, handler)

listener.start()
```

#### Calling service
You can now communicate with it over HTTP by any means

### curl
```shell
curl -X GET http://127.0.0.1:9999
```

### python
```python
import urllib.request
response = urllib.request.urlopen("http://localhost:9999")
print(response.read().decode("utf-8"))
```
