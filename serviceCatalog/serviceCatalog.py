# -*- coding: utf-8 -*-
"""
Created on Sun Nov 10 04:01:43 2019

@author: cyril
"""
import json
from datetime import datetime
import cherrypy_cors
import cherrypy
import socket,struct,platform,ifaddr


class Services():

    def __init__(self):
        self.servicefile = open("services.json")
        self.services = json.loads(self.servicefile.read())
        self.servicefile.close()    
    
    def get_ip_address(self,curOS):
        if curOS == "Linux":
            import fcntl
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            return socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
              0x8915,  # SIOCGIFADDR
             struct.pack('256s', "wlan0")
            )[20:24])
        elif curOS == "Windows":
            adapters = ifaddr.get_adapters()
            for adapter in adapters:
                if "VirtualBox Host-Only Ethernet Adapter" in adapter.nice_name:
                    for ip in adapter.ips:
                        if ip.network_prefix==24:                
                            hstip = ip.ip
                            break
                    break
#            return("192.168.21.238")
            return(socket.gethostbyname(socket.gethostname()))
#            return(hstip)
        else:
            return("127.0.0.1")
    
    def getService(self,houseID,deviceID,filterType):
        
        res = None
        col = {}
        try:
            if "str" in str(type(filterType)):
                if filterType == 'all':
                    res = self.services[houseID][deviceID]
                    res["sensorStatusAPI"]["API"]\
                            = res["sensorStatusAPI"]["API"].format(self.get_ip_address(platform.system()))
                    res["DataCollection"]["DataInsertAPI"]\
                            =  res["DataCollection"]["DataInsertAPI"].format(self.get_ip_address(platform.system()))
                else:
                    print(filterType)
                    res = self.services[houseID][deviceID][filterType]
                    print(res)
                    if filterType == "sensorStatusAPI":
                        res["API"]\
                            = res["API"].format(self.get_ip_address(platform.system()))
                    elif filterType == "DataCollection":
                        res["DataInsertAPI"]\
                            = res["DataInsertAPI"].format(self.get_ip_address(platform.system()))
                            
            elif "list" in str(type(filterType)):
                for i in filterType:
                    col[i] = self.services[houseID][deviceID][i]
                    if i == "sensorStatusAPI":
                        col[i]["API"]\
                            = col[i]["API"].format(self.get_ip_address(platform.system()))
                    elif i == "DataCollection":
                        col[i]["DataInsertAPI"]\
                            = col[i]["DataInsertAPI"].format(self.get_ip_address(platform.system()))
                res = col
        except:
            res = None
                     
        if res:
            return(self._formJson("success",res))
        else:
            return(self._formJson("success","device not found"))
            
    
    def addService(self,houseID,deviceID,data):
        
        try:
            serviceType = data["service"]
            serviceInfo = data["properties"]
            
            res = self.services[houseID][deviceID].keys()
            
            allow = [1 for i in res if (i != serviceType)]
            
            if len(res) == sum(allow):
            
                self.services[houseID][deviceID][serviceType] = serviceInfo
                updateTime = str(datetime.now()).rsplit(':', 1)[0]
                self.services[houseID][deviceID]["last_update"] = updateTime
                
                with open('services.json', 'w') as f:
                    f.write(json.dumps(self.services))
                    f.close()
            else:
                return(self._formJson("Failed","Same Service Key exists"))
                    
            return(self._formJson("success","Service Added"))
            
        except:
            return(self._formJson("failed","Failed to Add"))
        

    def updateService(self,houseID,deviceID,data):
        
        try:
            serviceType = data["service"]
            serviceInfo = data["properties"]
            
            res = self.services[houseID][deviceID][serviceType].keys()
                                     
            allow = [1 for i in list(serviceInfo.keys())
                         if (i in res)]
           
            if len(serviceInfo.keys()) == sum(allow):
                for j in serviceInfo.keys(): 
                    self.services[houseID][deviceID][serviceType][j] = serviceInfo[j]
                    output = "service updated"
                    updateTime = str(datetime.now()).rsplit(':', 1)[0]
                    self.services[houseID][deviceID]["last_update"] = updateTime                        
                    
            else:
                return(self._formJson("Failed","Keys didnt match"))
                                
            with open('services.json', 'w') as f:
                    f.write(json.dumps(self.services))
                    f.close()
            return(self._formJson("success",output))
            
        except:
            return(self._formJson("failed","Failed to Add"))
    
    def deleteService(self,houseID,deviceID,data):
        
        try:
            serviceType = data["service"]
            serviceInfo = data["properties"]      
            
            res = self.services[houseID][deviceID].keys()
            
            if serviceType in res:      
                self.services[houseID][deviceID].pop([serviceInfo],None)
                updateTime = str(datetime.now()).rsplit(':', 1)[0]
                self.services[houseID][deviceID]["last_update"] = updateTime
                with open('services.json', 'w') as f:
                    f.write(json.dumps(self.services))        
                    f.close()
                return(self._formJson("success","Service deleted"))
                    
            return(self._formJson("Failed","No such Service "))
            
        except:
            return(self._formJson("failed","Failed to delete"))
        
    
    def _formJson(self,status,val):
        return(json.dumps({'Result':status,'Output':val}))

class ServiceCatalogWebService(object): 


    exposed = True 
    
    def GET (self, *uri, **params):
#        return (str(len(params)))
        ser=Services()
        try:
            houseID = uri[0]
            deviceID = uri[1]
            filtertype = uri[2]
            response = ser.getService(houseID,deviceID,filtertype)            
            return (response)
        except:
            return(ser._formJson("failed","exception occured"))
        
            
            
    def POST (self, *uri, **params): 
        
        ser = Services()
        res = None
        inputtext=json.loads(cherrypy.request.body.read())
        method = inputtext["call"]
        houseID = inputtext["houseID"]
        deviceID = inputtext["deviceID"]
        
        if method == "addService":
            res = ser.addService(houseID,deviceID,inputtext["data"])
            
        elif method == "updateService":
            res = ser.updateService(houseID,deviceID,inputtext["data"])
            
        elif method == "removeService":
            res = ser.deleteService(houseID,deviceID,inputtext["data"])
        
        elif method == "getService":
            res = ser.getService(houseID,deviceID,inputtext["data"])
        
        else:
            return ser._formJson("Failed","Wrong request")       
        
        return(res)
    
    
    def PUT (self, *uri, **params): 
        pass
    
    def DELETE (self): 
    	pass
          
def CORS():
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    
if __name__ == '__main__':
    cherrypy_cors.install()
    conf = {
		'/': {
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.CORS.on': True,
            'cors.expose.on': True,
            'tools.response_headers.headers':
            [('Content-Type', 'application/json'),]
#              , ('Access-Control-Allow-Origin', '*'),("Access-Control-Allow-Methods", "POST, GET, OPTIONS, DELETE"))]
		}
	}
    cherrypy.config.update({
    'server.socket_host' : '0.0.0.0',
    'server.socket_port' : 8283,
    })
    cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS)
    cherrypy.tree.mount(ServiceCatalogWebService(), '/servicecatalog', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()