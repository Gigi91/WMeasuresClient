'''
Created on 16 mag 2016

@author: Luigi
Implementa il client per il dialogo con il web server vero e proprio
'''
import httplib

class WebClient:
    url = 'localhost:80'
    headers = {"Content-type": "application/x-www-form-urlencoded",
           "Accept": "text/plain"}
     
    def sendRequest(self, resource, params):    
        conn = httplib.HTTPConnection(self.url)
        conn.request("POST", resource, params, self.headers)
        response = conn.getresponse()
        print response.status, response.reason
        data = response.read()
        conn.close()
        return data
        