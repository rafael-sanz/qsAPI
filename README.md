## About
qsAPI is a client for Qlik Sense QPS and QRS interfaces written in python that provides an environment for managing a Qlik Sense site via programming or interactive console. The module provides a set of commands for viewing and editing configuration settings, as well as managing tasks and other features available through APIs.

## Installation
You could use your preferred IDE (Eclipse, Visual Studio, NetBeans, …) with the python interpreter 3.x. Take a look at (http://www.activestate.com/activepython) or (https://www.python.org). Once the module is loaded you can view a list of available commands with the autocomplete tooltips.

The python “requests” library is a requisite (http://docs.python-requests.org/en/master/user/install/). Just execute in the command line:
```python
pip install requests
```
The module can be used importing qsAPI.py at the beginning of your python script or console, the module will then be loaded and ready to use.
```python
>>> import qsAPI
```

![IDE screenshot](https://raw.githubusercontent.com/rafael-sanz/qsAPI/master/qsAPI.png)


Or just a simple interactive console command line if complex scripts are no needed: 
![console screenshot](https://raw.githubusercontent.com/rafael-sanz/qsAPI/master/qsAPI_console.png)


## Usage
### Connecting with certificates
The first step is to build a handler invoking the constructor of the class you will use containing the host parameters, this will attempt to connect to the Qlik Sense server.
```python
>>> qrs=qsAPI.QRS(proxy=’hostname', certificate='path\\client.pem')
```
## Examples
#### Count users using a filter
```python
qrs.count('user',"Name eq 'sa_repository'")
```
#### Duplicate an application in the server
```python
qrs.AppCopy('a99babf2-3c9d-439d-99d2-66fa7276604e',"HELLO world")
```
#### Export an application
```python
qrs.AppExport('a99babf2-3c9d-439d-99d2-66fa7276604e',"c:\\path\\myAppName.qvf")
```

#### Export all published applications to directories
```python
for app in qrs.AppGet(pFilter="stream.name ne 'None'"):
	os.makedirs(app['stream']['name'], exist_ok=True)
	qrs.AppExport(app['id'], app['stream']['name']+'\\'+app['name'])
```

#### Retrieve security rules using a filter
```python
qrs.SystemRules("type eq 'Custom'")
```

#### Retrieve a list of sessions for a user
```python
[x['SessionId'] for x in qps.GetUser('DIR', 'name').json()]
```
#### teardown of all connections for the user and related sessions
```python
qps.DeleteUser('DIR','name')
```

##### More examples
Take a look at the Wiki area: (https://github.com/rafael-sanz/qsAPI/wiki)


## TODO
The module is in progress, just a subset of method are implemented. But all the endpoints could be handled through the inner class “driver” and the methods `get, post, put, delete`.
```python
qps.driver.get('/qrs/about/api/enums').json()
```

## License
This software is made available "AS IS" without warranty of any kind. Qlik support agreement does not cover support for this software.
