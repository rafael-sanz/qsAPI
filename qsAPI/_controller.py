# -*- coding: UTF-8 -*-

'''
@author:     Rafael Sanz
@contact:    rafael.sanz@selab.es
@Copyright:  2016 <Rafael Sanz - (R)SELAB>

# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
'''

import sys, os.path
import requests as req
import urllib.parse as up
import random, string, json, re
import logging



class _Controller(object):
    """ Handler REST-API QRS"""
       
    _referer='Mozilla/5.0 (Windows NT 6.3; Win64; x64) qsAPI APIREST (QSense)'
    
    try:
        from requests_ntlm import HttpNtlmAuth as _ntlm
    except ImportError:
        _ntlm=None  
    
    def __init__(self, schema, proxy, port, vproxy, certificate, verify, user, verbosity, logName):
        ''' 
            @Function setup: Setup the connection and initialize handlers
            @param schema: http/https
            @param proxy: hostname to connect
            @param port: port number
            @param vproxy: virtual proxy conf. {preffix:'proxy', path: '^/qrs/', template:'/{}/qrs/'})
            @param certificate: path to .pem client certificate
            @param verify: false to trust in self-signed certificates
            @param user: dict with keys {userDirectory:, userID:, password:} or tuple
            @param verbosity: debug level
            @param logger: logger instance name
        '''
        self.proxy    = proxy
        self.port     = str(port)
        self.proxy    = proxy;
        self.vproxy   = None;
        self.baseurl  = None
        self.request  = None
        self.response = None
        self.session  = None
        
        if vproxy:
            self.setVProxy(**vproxy)
        
        self.setUser(**user) if isinstance(user, dict) else self.setUser(*user)
          
        self.chunk_size = 512 #Kb
        
        self.log=logging.getLogger(logName)
        if not self.log.hasHandlers():
            self.log.addHandler(logging.StreamHandler(sys.stdout))
        self.log.setLevel(verbosity)
        
        self.baseurl= '{schema}://{host}:{port}'.format(schema=schema, host=proxy, port=str(port))
        
        if isinstance(certificate, str):
            (base,ext)=os.path.splitext(certificate)
            self.cafile=(base+ext, base+'_key'+ext)
            self.log.debug('CERTKEY: %s%s', base, ext)
        elif isinstance(certificate, tuple):
            self.cafile=certificate
            self.log.debug('CERT: %s',certificate)
        else:
            self.cafile=False
            
        self._verify=bool(verify)
        
        if not self._verify:
            req.packages.urllib3.disable_warnings()
        
        self.session=req.Session()
        
        if self._ntlm and not self.cafile:
            self.log.debug('NTLM authentication enabled')
            self.session.auth = self._ntlm('{domain}\\{user}'.format(domain=self.UserDirectory, user=self.UserId), self.Password)
        
        
    def setVProxy(self, preffix, path, template):
        self.vproxy={}
        self.vproxy['preffix'] =preffix               # proxy
        self.vproxy['path']    =re.compile(path)      # ^/qrs/
        self.vproxy['template']=template              # /{}/qrs/
        self.vproxy['pxpath']  =template.format(preffix)    
 
        
    def setUser(self, userDirectory, userID, password=None):
        self.UserDirectory=userDirectory
        self.UserId = userID
        self.Password=password
            
    
    @staticmethod
    def normalize(schema, proxy, port, certificate):
        
        if '://' in proxy:
            schema, proxy = proxy.split('://')
        if not certificate and isinstance(port, int):
            port=443
        if ':' in proxy:
            proxy, port = proxy.split(':')
        
        return(schema, proxy, port)
    
        
    def _params_prepare(self, param, xhd={}):
                
        par=dict({'Xrfkey': ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))})
        if isinstance(param, dict):
            for p,v in param.items():
                if v is not None:
                    if isinstance(v, bool):
                        par[p]=str(v).lower()
                    else:
                        par[p]=str(v)
                    self.log.debug(" >> %s=>%s",p , par[p])
                else:
                    self.log.debug(" >> %s=>(default)", p)
            
        hd= { 'User-agent': self._referer,
              'Pragma': 'no-cache',
              'X-Qlik-User': 'UserDirectory={directory}; UserId={user}'.format(directory=self.UserDirectory, user=self.UserId),
              'x-Qlik-Xrfkey': par.get('Xrfkey'),
              'Accept': 'application/json',
              'Content-Type': 'application/json'}
        
        if self.vproxy:
            hd['X-Qlik-Virtual-Proxy-Prefix']=self.vproxy['preffix']
                
        hd.update(xhd)
        return(par, hd)  
    
    
    
    def _params_update(self, url, par):
        scheme, netloc, path, query, fragment=up.urlsplit(url)
        if self.vproxy:
            path= self.vproxy['path'].sub(self.vproxy['pxpath'], path)
        p=up.parse_qs(query)
        p.update(par)
        query=up.urlencode(p,doseq=True,quote_via=up.quote)
        return up.urlunsplit((scheme, netloc, path, query, fragment))
        
        
    
       
    def call(self, method, apipath, param=None, data=None, files=None):
        """ initialize control structure """
               
        if str(method).upper() not in ('GET', 'POST', 'PUT', 'DELETE'):
            raise ValueError('invalid method <{0}>'.format(method))
       
        self.log.info('API %s <%s>', method[:3], apipath)
        
        (par,hd)=self._params_prepare(param, {} if files is None else {'Content-Type': 'application/vnd.qlik.sense.app'})
        
        # Build the request        
        self.response= None
            
        url=self._params_update(up.urljoin(self.baseurl,apipath), par)
        self.request=req.Request(method, url, headers=hd, data=data, files=files, auth=self.session.auth)
        pr=self.session.prepare_request(self.request)
                
        self.log.debug('SEND: %s', self.request.url)
                
        # Execute the HTTP request
        self.response = self.session.send(pr, cert=self.cafile, verify=self._verify, allow_redirects=False)
        rc=0
        while self.response.is_redirect:
            rc+=1
            if rc > self.session.max_redirects:
                raise req.HTTPError('Too many redirections')
            self.session.rebuild_auth(self.response.next, self.response)
            self.response.next.prepare_headers(hd)
            self.response.next.prepare_cookies(self.response.cookies)
            self.response.next.url=self._params_update(self.response.next.url, par)
            self.log.debug('REDIR: %s', self.response.next.url)
            self.response = self.session.send(self.response.next, verify=self._verify, allow_redirects=False)
            
        self.log.debug('RECV: %s',self.response.text)
        
        return(self.response)



    def download(self, apipath, filename, param=None):
        """ initialize control structure """
                   
        self.log.info('API DOWN <%s>', apipath)

        (par,hd)=self._params_prepare(param)
        
        # Build the request        
        self.response= None
        
        url=self._params_update(up.urljoin(self.baseurl,apipath), par)
     
        self.log.debug('__SEND: %s',url)
                
        # Execute the HTTP request 
        self.request = self.session.get(url, headers=hd, cert=self.cafile, verify=self._verify, stream=True, auth=self.session.auth)
            
        with open(filename, 'wb') as f:
            self.log.info('__Downloading (in %sKb blocks): ', str(self.chunk_size))
            
            #download in 512Kb blocks
            for chunk in self.request.iter_content(chunk_size=self.chunk_size << 10): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                        
            self.log.info('__Saved: %s', os.path.abspath(filename))
        
        return(self.request)

    
    
    def upload(self, apipath, filename, param=None):
        """ initialize control structure """
        
        class upload_in_chunks(object):
            def __init__(self, filename, chunksize=512):
                self.filename = filename
                self.chunksize = chunksize << 10
                self.totalsize = os.path.getsize(filename)
                self.readsofar = 0
        
            def __iter__(self):
                with open(self.filename, 'rb') as file:
                    while True:
                        data = file.read(self.chunksize)
                        if not data:
                            break
                        self.readsofar += len(data)
                        yield data
        
            def __len__(self):
                return self.totalsize
                       
        self.log.info('API UPLO <%s>', apipath)

        (par,hd)=self._params_prepare(param, {'Content-Type': 'application/vnd.qlik.sense.app'})
           
        # Build the request        
        self.response= None
        url=self._params_update(up.urljoin(self.baseurl,apipath), par)
        self.log.debug('__SEND: %s', url)

        # Execute the HTTP request 
        self.log.info('__Uploading {:,} bytes'.format(os.path.getsize(filename)))
        self.request = self.session.post(url, headers=hd, cert=self.cafile, verify=self._verify, \
                                data=upload_in_chunks(filename, self.chunk_size), auth=self.session.auth)
            
        self.log.info('__Done.')                
            
        return(self.request)


    
    
    def get(self, apipath, param=None):
        '''
        @Function get: generic purpose call
        @param apipath: uri REST path
        @param param : whatever other param needed in form a dict
                      (example: {'filter': "name eq 'myApp'} )
        '''
        return self.call('GET', apipath, param)
    
    
    
    def post(self, apipath, param=None, data=None, files=None):
        '''
        @Function post: generic purpose call
        @param apipath: uri REST path
        @param param : whatever other param needed in form a dict
                      (example: {'filter': "name eq 'myApp'} )
        @param data : stream data input (native dict/list structures are json formated)
        @param files : metafile input 
        '''
        if isinstance(data,dict) or isinstance(data,list):
            data=json.dumps(data)
        return self.call('POST', apipath, param, data, files)
    
    
    
    def put(self, apipath, param=None, data=None):
        '''
        @Function put: generic purpose call
        @param apipath: uri REST path
        @param param : whatever other param needed in form a dict
                      (example: {'filter': "name eq 'myApp'} )
        @param data : stream data input (native dict/list structures are json formated)
        '''
        if isinstance(data,dict) or isinstance(data,list):
            data=json.dumps(data)
        return self.call('PUT', apipath, param, data)
    
    
    
    def delete(self, apipath, param=None):
        '''
        @Function delete: generic purpose call
        @param apipath: uri REST path
        @param param : whatever other param needed in form a dict
                      (example: {'filter': "name eq 'myApp'} )
        '''
        return self.call('DELETE', apipath, param)

