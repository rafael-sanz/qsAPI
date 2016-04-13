## About
qsAPI is a client for Qlik Sense QPS and QRS interfaces written in python that provides an environment for managing a Qlik Sense via programming or interactive console. The module provides a set of commands for viewing and editing configuration settings, as well as managing tasks and other features available through the APIs.

## Installation
Is prerequisite the python library “requests” (http://docs.python-requests.org/en/master/user/install/). Just execute in the command line:
```sh
pip install requests
```
The module can be used importing qsAPI.py at beginning of your python script or console, the module will then be loaded and ready to use.
```sh
>>> import qsAPI
```
You could use your preferred IDE (Eclipse, Visual Studio, NetBeans, …) Once the module is loaded you can view a list of available commands with the autocomplete tooltips.

## Usage
### Connecting with certificates
The first is build a handler invoking the constructor of class you will use with the host parameters, this will attempt to connect to the Qlik Sense server.
```sh
>>> qrs=qsAPI.QRS(proxy=’hostname', certificate='path\\client.pem')
```
## Examples
#### Count the users using a filter
```sh
qrs.count('user',"Name eq 'sa_repository'")
```
#### Copy and application
```sh
qrs.AppCopy('a99babf2-3c9d-439d-99d2-66fa7276604e',"HELLO world")
```
#### Retrieve a list of sessions for a user
```sh
[x['SessionId'] for x in qps.GetUser('DIR', 'name').json()]
```

## TODO
The module is in progress, just a subset of method are implemented. But all the endpoints could be handled through the inner class “driver” and the methods get|post|put|delete.
```sh
qps.driver.get('/qrs/about/api/enums').json()
```

## License
This software is made available "AS IS" without warranty of any kind. Qlik support agreement does not cover support for this software.
