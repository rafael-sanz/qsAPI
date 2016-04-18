## About
qsAPI is a client for Qlik Sense QPS and QRS interfaces written in python that provides an environment for managing a Qlik Sense site via programming or interactive console. The module provides a set of commands for viewing and editing configuration settings, as well as managing tasks and other features available through APIs.

## Installation
You could use your preferred IDE (Eclipse, Visual Studio, NetBeans, …) with the python interpreter 3.x. Once the module is loaded you can view a list of available commands with the autocomplete tooltips.

The python “requests” library is a requisite (http://docs.python-requests.org/en/master/user/install/). Just execute in the command line:
```sh
pip install requests
```
The module can be used importing qsAPI.py at the beginning of your python script or console, the module will then be loaded and ready to use.
```sh
>>> import qsAPI
```

## Usage
### Connecting with certificates
The first step is to build a handler invoking the constructor of the class you will use containing the host parameters, this will attempt to connect to the Qlik Sense server.
```sh
>>> qrs=qsAPI.QRS(proxy=’hostname', certificate='path\\client.pem')
```
## Examples
#### Count users using a filter
```sh
qrs.count('user',"Name eq 'sa_repository'")
```
#### Duplicate an application in the server
```sh
qrs.AppCopy('a99babf2-3c9d-439d-99d2-66fa7276604e',"HELLO world")
```
#### Export an application
```sh
qrs.AppExport('a99babf2-3c9d-439d-99d2-66fa7276604e',"c:\\path\\myAppName.qvf")
```
#### Retrieve security rules using a filter
```sh
qrs.SystemRules("type eq 'Custom'")
```

#### Retrieve a list of sessions for a user
```sh
[x['SessionId'] for x in qps.GetUser('DIR', 'name').json()]
```

## TODO
The module is in progress, just a subset of method are implemented. But all the endpoints could be handled through the inner class “driver” and the methods get/post/put/delete.
```sh
qps.driver.get('/qrs/about/api/enums').json()
```

## License
This software is made available "AS IS" without warranty of any kind. Qlik support agreement does not cover support for this software.
