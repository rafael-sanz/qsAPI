# -*- coding: UTF-8 -*-

'''
@author:     Rafael Sanz
@contact:    rafael.sanz@selab.es
@Copyright:  2016 <Rafael Sanz - (R)SELAB>

# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
'''

# Qlik sense 3.0, initial release 28/6/2016.
# since June 2017, version sequence jumps to 11.11.1
_minServerAPIversion = '3.0.0'

import uuid as _uuid
from distutils.version import LooseVersion as _lv
from ._controller import _Controller  

    
class QPS(object):
    '''Qlik Sense Proxy Service REST API'''
    
    VERSION_API= _lv(_minServerAPIversion)
    
    def __init__(self, schema='https', proxy='localhost', port=4243, vproxy=None, certificate=None, verify=False, \
                 user={'userDirectory':'internal', 'userID':'sa_repository', 'password': None}, \
                 verbosity='INFO', logger='qsapi'):  
        
        schema, proxy, port=_Controller.normalize(schema, proxy, port, certificate) 
        p_vproxy={'preffix': vproxy, 'path': '^/qps/', 'template':'/{}/qps/'} if vproxy else None
        
        self.driver=_Controller(schema, proxy, port, p_vproxy, certificate, verify, user, verbosity, logger)

        

    def GetUser(self, directory, user):
        '''
        @Function: This returns all proxy sessions that a user (identified by {directory} and {user}) has.
        '''
        apipath='/qps/user/{directory}/{id}'.format(directory=directory, id=user)
        return self.driver.get(apipath)

    
    
    def DeleteUser(self, directory, user):
        '''
        @Function: This is part of the Logout API. The directory and ID are the same UserDirectory and UserId as those that were sent in POST /qps/{virtual proxy/}ticket.
                    A list of all proxy sessions that were connected to the deleted user is returned. 
        '''
        apipath='/qps/user/{directory}/{id}'.format(directory=directory, id=user)
        return self.driver.delete(apipath)
    

    
    def GetSession(self, pId):
        '''
        @Function: This returns the proxy session identified by {id}.
        '''
        apipath='/qps/session/{id}'.format(id=pId)
        return self.driver.get(apipath)
    
    
    def DeleteSession(self, pId):
        '''
        @Function: Delete the proxy session identified by {id}.
        '''
        apipath='/qps/session/{id}'.format(virtual_proxy=self.driver.preffix, id=pId)
        return self.driver.delete(apipath)



class QRS(object):
    '''Qlik Sense Repository Service REST API'''
    
    VERSION_API= _lv(_minServerAPIversion)
    
    
    def __init__(self, schema='https', proxy='localhost', port=4242, vproxy=None, certificate=None, verify=False, \
                 user={'userDirectory':'internal', 'userID':'sa_repository', 'password': None}, \
                 verbosity='INFO', logger='qsapi'):
        
        schema, proxy, port=_Controller.normalize(schema, proxy, port, certificate)
        p_vproxy={'preffix': vproxy, 'path': '^/qrs/', 'template':'/{}/qrs/'} if vproxy else None
            
        self.driver=_Controller(schema, proxy, port, p_vproxy, certificate, verify, user, verbosity, logger)
        
        self.VERSION_SERVER=self.getServerVersion()
        if self.VERSION_API > self.VERSION_SERVER:
            raise Exception('<server version mismatch, API:{0} > Server:{1}'.format(self.VERSION_API, self.VERSION_SERVER))
        else:
            self.driver.log.info('Server version: {0}'.format(self.VERSION_SERVER))


    
    def _toDict(self, response, uid='full', key='name', attr='id'):
        r={}
        if response.ok:
            j=response.json()
            if uid != "full":
                if isinstance(attr, str):
                    r[j.get(key)]=j.get(attr)
                elif isinstance(attr, list):
                    ra={}
                    for a in attr:
                        ra[a]=(j.get(a))
                    r[j.get(key)]=ra
                else:
                    raise TypeError('attr argument must be a str or list')
            else:               
                for x in j:
                    if isinstance(attr, str):
                        r[x.get(key)]=x.get(attr)
                    elif isinstance(attr, list):
                        ra={}
                        for a in attr:
                            ra[a]=(x.get(a))
                        r[x.get(key)]=ra
                    else:
                        raise TypeError('attr argument must be a str or list')
        
        return(r)
    


    def ping(self):
        '''
        @return: "Ping successful", if there are no problems contacting the Qlik Sense Repository Service (QRS).
        '''
        return self.driver.call('GET', '/qrs/ssl/ping')



        
    def getServerVersion(self):
        '''
        @Function: retrieve the server version
        '''
        return _lv(self.driver.call('GET', '/qrs/about').json().get('buildVersion'))

 
 
    
    def getAbout(self):
        '''
        @Function: Get information on the Qlik Sense repository, including version, database provider, and whether the node is the central node of the site or not.
        '''
        return self.driver.get('/qrs/about').json()
    
 
    
    def count(self, pType, pFilter=None):
        '''
        @Function: generic purpose call
        @param pType: entity to count
        @param pFilter: filter the entities before calculating the number of entities. 
        @return : integer from json response
        '''
        return self.driver.get('/qrs/{0}/count'.format(pType), param={'filter':pFilter}).json()['value']
 
    
    
    def getDescription(self, extended='False', method=None, outformat='JSON'):
        '''@Function : List all paths available in the Qlik Sense Repository Service (QRS) API. Optionally, return extended information, endpoints that use a specific HTTP verb, or the return values in JSON format.
           @param extended: If true, returns the following:
                The type (if any) that needs to be included in the body.
                The type of return value (if any).
                If the endpoint is automatically generated or not.
           @param method:  If set to an HTTP verb (GET, PUT, POST, or DELETE), only endpoints that use the verb are returned.
           @param outformat:  If set to "JSON", the return value is given in JSON format. 
        '''
            
        param={'extended': extended in ('True', 'true', True),
               'method'  : method,
               'format'  : outformat}
        
        return self.driver.get('/qrs/about/api/description', param).json()



    def getEnum(self):
        '''@Function: Get all enums that are used by the public part of the Qlik Sense Repository Service (QRS) API.
        '''
        return self.driver.get('/qrs/about/api/enums').json()



    #=========================================================================================

    
    
    def AppDictAttributes(self, puid='full', pFilter=None, key='name', attr='id'):
        '''@Function: retrieve a mapping of apps attributes
           @param pId: limmit the scope to the App {UUID}
           @param pFilter: filter the entities before calculating the number of entities.
           @param key: the attribute to be the key
           @param attr: the attribute value to retrieve (single value or list)
           @return: dict(key:attr)
        '''
        apipath='/qrs/app/{puid}'.format(puid=puid)
        return self._toDict(self.driver.get(apipath, param={'filter':pFilter}), puid, key, attr)    
        
    

    def AppCopy(self, pId, name=None):
        '''
        @Function: Copy an existing app, identified by {id}. Optionally, provide a name for the copy.
        @param pId: app identifier
        @param name: Name of the app
        '''
        param={'name':name}
        return self.driver.post('/qrs/app/{id}/copy'.format(id=pId), param).json()


    
    def AppExport(self, pId, filename=None, skipdata='true'):
        '''
        @Function: Get an export qvf for an existing app, identified by {id}.
        @param pId: app GUI
        @param filename: target path filename
        @param skipData: if True App will be emptied of data
        @return : stored application
        '''
        file= filename if filename else pId+'.qvf'
        if self.VERSION_SERVER < "17.0":
            #DEPRECATED API since November-2017
            self.driver.log.info('Server version: %s, using legacy API', self.VERSION_SERVER)
            r=self.driver.get('/qrs/app/{id}/export'.format(id=pId))
            if r.ok:
                r=self.driver.download('/qrs/download/app/{appId}/{TicketId}/{fileName}'.format(appId=pId, TicketId=r.json()['value'], fileName=file), file)
            return(r)
        
        #Current API method
        r=self.driver.post('/qrs/app/{id}/export/{token}?skipData={skipdata}'.format(id=pId, token=_uuid.uuid4(), skipdata=skipdata))
        if r.ok:
            r=self.driver.download(r.json()['downloadPath'], file)
        return(r)




    def AppUpload(self, filename, pName, keepdata=None):
        '''
        @Function: Upload a filename.qvf into Central Node.
        @param filename: target path filename
        @param name: target app name
        @param keepdata: Exclude the app data when uploading the app (when it is implemented)
        '''
        param ={'name'    :pName,
                'keepdata':keepdata}
        return self.driver.upload('/qrs/app/upload', filename, param)

    
    def AppGet(self, pId='full', pFilter=None):
        '''
        @Function: retrieve App information
        @param pId: App UUID 
        @param pFilter: filter the entities before calculating the number of entities. 
        @return : json response
        '''
        return self.driver.get('/qrs/app/{id}'.format(id=pId), param={'filter':pFilter}).json()
    
    
    
    def AppMigrate(self, pId):
        '''
        @Function: Migrate an app so that it can be used in the currently installed version of Qlik Sense.
                    Normally, this is done automatically
        @param pId: app identifier
        '''
        return self.driver.put('/qrs/app/{id}/migrate'.format(id=pId))
    
            
    
    def AppReload(self, pId):
        '''
        @Function: Reload an app
        @param pId: app identifier
        '''
        return self.driver.post('/qrs/app/{id}/reload'.format(id=pId))


    def AppPublish(self, pId, streamId, name=None):
        '''
        @Function: Publish an existing app, identified by {id}, to the stream identified by {streamid}.
        @param pId: app identifier
        @param streamId: stream identifier
        @param name: optional alternate name
        '''
        param ={'stream' :streamId,
                'name'   :name}
        return self.driver.put('/qrs/app/{id}/publish'.format(id=pId), param)
    
    
    def AppUpdate(self, pId, pData):
        '''
        @Function: update App info referenced 
        @param pId: App UUID 
        '''
        return self.driver.put('/qrs/app/{id}'.format(id=pId), data=pData)
    
    
    def AppReplace(self, pId, pAppId):
        '''
        @Function: Replace an app, identified by {appid}, with the app identified by {id}. 
        @param pId: source App UUID 
        @param pAppId: target App UUID

        If the replaced app is published, only the sheets that were originally published with the app are replaced.
        If the replaced app is not published, the entire app is replaced.
        '''
        param ={'app' :pAppId}
        return self.driver.put('/qrs/app/{id}/replace'.format(id=pId), param)
    
    
    def AppDelete(self, pId):
        '''
        @Function: delete App referenced 
        @param pId: App UUID 
        '''
        return self.driver.delete('/qrs/app/{id}'.format(id=pId))
    
    
    #=========================================================================================
    
    
    def AppObjectGet(self, pId='full', pFilter=None):
        '''
        @Function: retrieve AppObject information
        @param pId: AppObject UUID 
        @param pFilter: filter the entities before calculating the number of entities. 
        @return : json response
        '''
        return self.driver.get('/qrs/app/object/{id}'.format(id=pId), param={'filter':pFilter}).json()
    
    
    def AppObjectCount(self, pFilter=None):
        '''
        @Function: retrieve AppObject count information
        @param pFilter: filter the entities before calculating the number of entities. 
        @return : json response
        '''
        return self.driver.get('/qrs/app/object/count', param={'filter':pFilter}).json()
    
    
    def AppObjectUpdate(self, pId, pData):
        '''
        @Function: retrieve AppObject information
        @param pId: AppObject UUID  
        @param pData: AppObject attributes
        '''
        return self.driver.put('/qrs/app/object/{id}'.format(id=pId), data=pData)
    
    
    def AppObjectApprove(self, pId, pApprove=True):
        '''
        @Function: Set AppObject approve status
        @param pId: AppObject UUID  
        @param pApprove: True / False
        '''
        return self.driver.post('/qrs/app/object/{id}/{status}'.format(id=pId, status='approve' if pApprove else 'unapprove'))
    
    
    def AppObjectPublish(self, pId, pPublish=True):
        '''
        @Function: Set AppObject publish status
        @param pId: AppObject UUID  
        @param pPublish: True / False
        '''
        return self.driver.put('/qrs/app/object/{id}/{status}'.format(id=pId, status='publish' if pPublish else 'unpublish'))
    
    
    def AppObjectDelete(self, pId):
        '''
        @Function: Delete AppObject
        @param pId: AppObject UUID  
        '''
        return self.driver.delete('/qrs/app/object/{id}'.format(id=pId))
    
        
    #=========================================================================================
    
    
    def StreamCreate(self, pName, pProperties=[] , pTags=[], pUUID=None):
        '''
        @Function: create a Stream
        @param pName: Stream Name 
        @param pUID: Stream UUID
        @param pProperties: list of dict with properties definitions.
        @param pTags: list of dict with tag definitions 
        @return : json response
        '''
        param={'name': pName,
               'customProperties': pProperties,
               'tags': pTags}
        
        if pUUID is not None:
            param['id']=pUUID
                 
        return self.driver.post('/qrs/stream', data=param).json()
    
    
    
    def StreamGet(self, pId='full', pFilter=None):
        '''
        @Function: retrieve Stream information
        @param pId: Stream UUID 
        @param pFilter: filter the entities before calculating the number of entities. 
        @return : json response
        '''
        return self.driver.get('/qrs/stream/{id}'.format(id=pId), param={'filter':pFilter}).json()
    
    
    
    def StreamUpdate(self, pId, pData):
        '''
        @Function: update Stream info referenced 
        @param pId: Stream UUID 
        @param pData: stream attributes
        '''
        return self.driver.put('/qrs/stream/{id}'.format(id=pId), data=pData)
    
    
    
    def StreamDelete(self, pId):
        '''
        @Function: delete Stream referenced 
        @param pId: Stream UUID 
        @return : json response
        '''
        return self.driver.delete('/qrs/stream/{id}'.format(id=pId))
    
    
    
    def StreamDictAttributes(self, pStreamID='full', pFilter=None, key='name', attr='id'):
        '''@Function: retrieve a mapping of Stream attributes
           @param pStreamID: limmit the scope to the Stream {UID}
		   @param pFilter: filter the entities before calculating the number of entities.
           @param key: the attribute to be the key
           @param attr: the attribute value to retrieve (single value or list)
           @return: dict(key:attr)
        '''
        apipath='/qrs/stream/{uid}'.format(uid=pStreamID)            
        return self._toDict(self.driver.get(apipath, param={'filter':pFilter}), pStreamID, key, attr) 
    
    
    #=========================================================================================     
    
    
    def UserGet(self, pUserID='full', pFilter=None):
        '''
        @Function: retrieve user information
        @param pUserID: User id 
        @param pFilter: filter the entities before calculating the number of entities. 
        @return : json response
        '''
        return self.driver.get('/qrs/user/{id}'.format(id=pUserID), param={'filter':pFilter}).json()
    
    
    def UserUpdate(self, pUserID, pData):
        '''
        @Function: update user information
        @param pUserID: User id 
        @param pData: json with user information. 
        @return : json response
        '''
        return self.driver.put('/qrs/user/{id}'.format(id=pUserID), data=pData)
    
    
    def UserDelete(self, pUserID):
        '''
        @Function: retrieve user information
        @param pUserID: User id 
        @param pFilter: filter the entities before calculating the number of entities. 
        @return : json response
        '''
        return self.driver.delete('/qrs/user/{id}'.format(id=pUserID))
    
    
    def UserDictAttributes(self, pUserID='full', pFilter=None, key='name', attr='id'):
        '''@Function: retrieve a mapping of user attributes
           @param pUserID: limmit the scope to the User {UID}
		   @param pFilter: filter the entities before calculating the number of entities.
           @param key: the attribute to be the key
           @param attr: the attribute value to retrieve (single value or list)
           @return: dict(key:attr)
        '''
        apipath='/qrs/user/{uid}'.format(uid=pUserID)            
        return self._toDict(self.driver.get(apipath, param={'filter':pFilter}),pUserID,key,attr)
    
    
    #=========================================================================================

    def TaskGet(self, pFilter=None):
        '''
        @Function: retrieve Task information
        @param pFilter: filter the entities
        @return : json response
        '''
        return self.driver.get('/qrs/task/full', param={'filter': pFilter}).json()

    def TaskStart(self, taskid):
        '''
        @Function: Starts a task by id and waits until a slave starts to execute a task
        @param taskid: taskid of the task to start
        '''
        return self.driver.post('/qrs/task/{taskid}/start'.format(taskid=taskid))

    def TaskStartSynchronous(self, taskid):
        '''
        @Function: Starts a task by id and waits until a slave starts to execute a task
        @param taskid: taskid of the task to start
        '''
        return self.driver.post('/qrs/task/{taskid}/start/synchronous'.format(taskid=taskid))


    def TaskStartByName(self, taskname):
        '''
        @Function: Starts a task by name
        @param taskname: Name of the task to start
        '''
        return self.driver.post('/qrs/task/start', param={'name': taskname})

    def TaskStartMany(self, taskids):
        '''
        @Function: Starts multiple tasks
        @param taskids: list of id's of the task to start
            Sample list: ["6ca1c5f2-2742-44d5-8adf-d6cba3701a4e","965ca0cf-952f-4502-a65e-2a82e3de4803"]
        '''
        return self.driver.post('/qrs/task/start/many', data=taskids)

    def TaskStartByNameSynchronous(self, taskname):
        '''
        @Function: Starts a task and waits until a slave starts to execute a task
        @param taskname: Name of the task to start
        '''
        return self.driver.post('/qrs/task/start/synchronous', param={'name': taskname})

    def TaskStop(self, taskid):
        '''
        @Function: Stops a task
        @param taskid: id of the task to stop
        '''
        return self.driver.post('/qrs/task/{taskid}/stop'.format(taskid=taskid))

    def TaskStopMany(self, taskids):
        '''
        @Function: Stops multiple tasks
        @param taskname: list of id's of the task to stop
            Sample list: ["6ca1c5f2-2742-44d5-8adf-d6cba3701a4e","965ca0cf-952f-4502-a65e-2a82e3de4803"]
        '''
        return self.driver.post('/qrs/task/stop/many', data=taskids)

    #=========================================================================================
        
   
    def SystemRulesGet(self, pFilter=None):
        '''
        @Function: Get the system rules
        '''
        return self.driver.get('/qrs/systemrule/full', {'filter':pFilter}).json()
    
    
    def SystemRulesCreate(self, param):
        '''
        @Function: create a SystemRule
        @return : json response
        ''' 
        return self.driver.post('/qrs/systemrule', data=param).json()
    
    
    def SystemRulesDictAttributes(self, pRuleID='full', pFilter=None, key='name', attr='id'):
        '''@Function: retrieve a mapping of rules attributes
           @param pRuleID: limmit the scope to the Rule {UID}
		   @param pFilter: filter the entities before calculating the number of entities.
           @param key: the attribute to be the key
           @param attr: the attribute value to retrieve (single value or list)
           @return: dict(key:attr)
        '''
        apipath='/qrs/systemrule/{uid}'.format(uid=pRuleID)            
        return self._toDict(self.driver.get(apipath, param={'filter':pFilter}),pRuleID,key,attr)
    
    
    #=========================================================================================
    
    
    
    def ReloadTaskGet(self, pId='full', pFilter=None):
        '''
        @Function: retrieve ReloadTask information
        @param pId: ReloadTask UID 
        @param pFilter: filter the entities before calculating the number of entities. 
        @return : json response
        '''
        return self.driver.get('/qrs/reloadtask/{id}'.format(id=pId), param={'filter':pFilter}).json()
    
    
    
    #=========================================================================================
     
    
    def PropertiesGet(self, pFilter=None):
        '''
        @Function: Get the system rules
        '''
        return self.driver.get('/qrs/custompropertydefinition/full', {'filter':pFilter}).json()


    #=========================================================================================
    
    
    def TagsDictAttributes(self, pTagID='full', pFilter=None, key='name', attr='id'):
        '''@Function: retrieve a mapping of tags attributes
           @param pRuleID: limmit the scope to the Tag {UID}
		   @param pFilter: filter the entities before calculating the number of entities.
           @param key: the attribute to be the key
           @param attr: the attribute value to retrieve (single value or list)
           @return: dict(key:attr)
        '''
        apipath='/qrs/tag/{uid}'.format(uid=pTagID)            
        return self._toDict(self.driver.get(apipath, param={'filter':pFilter}),pTagID,key,attr)

    
    #=========================================================================================
    
    
    class LicenseType:
        UserAccess='useraccesstype'
        LoginAccess='loginaccesstype'
        ProfessionalAccess='professionalaccesstype'
        AnalyzerAccess='analyzeraccesstype'
    
    
    def LicenseUsageSummary(self):
        '''
        @Function: Get the license summary
        '''
        return self.driver.get('qrs/license/accesstypeinfo').json()
    
    
    def LicenseAccessGet(self, licenseType):
        '''
        @Function: Get a user access licenses
        @param licenseType: LicenseType***Access enumeration
        '''
        return self.driver.get('qrs/license/{}/full'.format(licenseType)).json()
    
    
    def LicenseAccessDelete(self, licenseType, pLicID):
        '''
        @Function: Delete a user access license
        @param licenseType: LicenseType***Access enumeration
        @param pLicID: key of license
        '''
        return self.driver.delete('qrs/license/{}/{}'.format(licenseType, pLicID))
    
    
    def LicenseAccessCount(self, licenseType):
        '''
        @Function: Retrieve the number of assigned access license
        @param licenseType: LicenseType***Access enumeration
        @param pLicID: key of licens
        '''
        return self.driver.get('/qrs/license/{}/count'.format(licenseType)).json()['value']


        
