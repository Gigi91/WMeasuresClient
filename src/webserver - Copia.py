'''
Created on 16 mag 2016

@author: Luigi
Implementa il web server utilizzato per avere come interfaccia lato client una pagina web
'''

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import webclient
import phidgets
import cgi
import shutil
import os
import urllib
import sensMonitoring as sm
import json
from operator import pos
from datetime import datetime
import time
import socket

PORT_NUMBER = 8080

#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
    def handle(self):
        try:
            return BaseHTTPRequestHandler.handle(self)
        except (socket.error, socket.timeout) as e:
            self.connection_dropped(e)
            
    def connection_dropped(self, error, environ=None):
        print "Connessione chiusa dal client"
        if os.path.isfile("username"): 
                os.remove("username")
        
        
    
    def do_GET(self):
        print self.path
        if self.path=="/":
            if os.path.isfile("username"): 
                os.remove("username")
            self.path="/index.htm"
            self.sendPage(200)
            return
        
        if self.path.endswith(".png"):
            self.send_response(200)
            self.send_header('Content-type','image/png')
            self.end_headers()
            #with open("Img\\red.png", 'rb') as content:
            with open(os.path.abspath(curdir + "/"+self.path), 'rb') as content:
                shutil.copyfileobj(content, self.wfile)
            return
        
        if self.path.endswith(".jpg"):
            self.send_response(200)
            self.send_header('Content-type','image/jpeg')
            self.end_headers()
            with open(os.path.abspath(curdir + "/"+self.path), 'rb') as content:
                shutil.copyfileobj(content, self.wfile)
            return
            
        if self.path =="/favicon.ico":
            self.send_response(200)
            self.send_header('Content-type','image/x-icon')
            self.end_headers()
            with open("favicon.ico", 'rb') as content:
                shutil.copyfileobj(content, self.wfile)
            return
        
        if self.path.endswith(".js"):
            self.sendPage(200)
            return
        
        if self.path=="/monitoring.htm":
            if os.path.isfile("username"): 
                self.sendPage(200)
            else:
                self.path="/"
                #self.sendPage(200)
                self.send_response(302)
                self.send_header('Location', 'http://localhost:8080')
                self.end_headers()
            return
        
        self.path ="errore.htm"
        self.sendPage(400)
        
    #Handler for the POST requests
    def do_POST(self):
        
        if self.path!="/storyboard" and self.path!="/registrazione":
            length = int(self.headers['content-length'])
            params = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        
        if self.path=="/":
            self.path="/index.htm"
            
        #registrazione dell'utente al sistema
        elif self.path=="/registrazione":
            length = int(self.headers['content-length'])
            params = self.rfile.read(length)
            print params
            client = webclient.WebClient()
            data = client.sendRequest("/wmeasure/wmeasuresSrv/src/controller/utentecontroller.php", params)
            self.send_response(200)
            self.send_header('Content-type','text/xml')
            self.send_header('Content-length',str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
            
        #lista sensori presenti nel sistema
        elif self.path.endswith("userSensorList"):
            client = webclient.WebClient()
            data = client.sendRequest("/wmeasure/wmeasuresSrv/src/controller/sensorecontroller.php", "op=get&u="+self.readUsername())
            print data
            self.send_response(200)
            self.send_header('Content-type','text/xml')
            self.send_header('Content-length',str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        
        #aggiunge un nuovo sensore non presente nel sistema
        elif self.path=="/addSensor":
            params['descr'] = str(params['descr']).replace("[", "")
            params['descr'] = str(params['descr']).replace("]", "")
            params['descr'] = str(params['descr']).replace("'", "")
            descr = urllib.urlencode(params)
            client = webclient.WebClient()
            data = client.sendRequest("/wmeasure/wmeasuresSrv/src/controller/sensorecontroller.php", "op=add&u="+self.readUsername()+"&"+descr)
            
            self.send_response(200)
            self.send_header('Content-type','text/xml')
            self.send_header('Content-length',str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        
        #associa un ingresso analogico ad un sensore presente nel sistema
        elif self.path =="/associa":
            pos = str(params['pos']).replace("[", "")
            pos = pos.replace("]", "")
            pos = pos.replace("'", "")
            
            descr = str(params['descr']).replace("[", "")
            descr = descr.replace("]", "")
            descr = descr.replace("'", "")
            print pos
            print descr
            monitoring = sm.SensorMonitoring()
            monitoring.insertDescByPos(descr, pos)
            monitoring.close()
            return
            
        #avvia monitoraggio: invio dei dati dei sensori al server
        elif self.path=="/monitoring":
            #global ph
            #ph.ponteDiWheatstone()
            monitoring = sm.SensorMonitoring()
            s = monitoring.getSensorValue()
            monitoring.close()
            
            u = self.readUsername()
            s = {'u':u,'op':'write', 'sensorsValue':s}
            
            data = json.dumps(s)
            client = webclient.WebClient()
            data = client.sendRequest("/wmeasure/wmeasuresSrv/src/controller/misuracontroller.php", data)
            print data
            return
        
        elif self.path=="/logout":
            os.remove("username")
            return

        #visualizza grafico andamento dei valori di particolari sensori
        elif self.path=="/storyboard":
            length = int(self.headers['content-length'])
            params = self.rfile.read(length)
            data = json.loads(params)
            print data
            start = data["start"]
            end = data["end"]
            print start
            print end
            for s in data["desc"]:
                print str(s)
                
            opdata = {'u': self.readUsername(), 'op': 'read'}
           
            par = {key: value for (key,value) in (data.items()+opdata.items())}
            
            print json.dumps(par)
             
            client = webclient.WebClient()
            data = client.sendRequest("/wmeasure/wmeasuresSrv/src/controller/misuracontroller.php", json.dumps(par))
            
            print data
            self.send_response(200)
            self.send_header('Content-type','text/xml')
            self.send_header('Content-length',str(len(data)))
            self.end_headers()
            self.wfile.write(data)
             
            return
        
        #ottieni stato dei sensori collegati agli ingressi analogici del sistema
        elif self.path=="/getSensorStatus":
            monitoring = sm.SensorMonitoring()
            sList = monitoring.getSensorList()
            monitoring.close()
            
            data = json.dumps(sList)
            self.send_response(200)
            self.send_header('Content-type','text/xml')
            self.send_header('Content-length',str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
            
        #login
        elif self.path == "/login":
            username = str(params['u']).replace("[","")
            username= username.replace("]", "")
            username= username.replace("'","")
            self.saveUsername(username)
            p = str(params).replace("[", "")
            p = p.replace("]", "")
            p = p.replace("'","")
            p = p.replace(":","=")
            p = p.replace(", ","&")
            p = p.replace(" ","")
            p = p.replace("{", "")
            p = p.replace("}", "")
            print p
            client = webclient.WebClient()
            data = client.sendRequest("/wmeasure/wmeasuresSrv/src/controller/utentecontroller.php", p)
            if data=="Login OK":
                
                self.wfile.write(data)

#                 self.path="/monitoring.htm"
#                 self.send_response(302)
#                 self.send_header('Location', self.path)
#                 self.end_headers()
                return
            else:
                print data
                self.send_response(200)
                self.send_header('Content-type','text/plain')
                self.send_header('Content-length',str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
        else:
            print self.path
            self.path ="errore.htm"
            self.sendPage(404)
            return
        self.sendPage(200)
        return
        
    def sendPage(self, code, mimetype=None):
        self.send_response(code)
        if mimetype==None:
            self.send_header('Content-type','text/html')
        else:
            self.send_header('Content-type',mimetype)
        self.end_headers()
        
        # Send the html page
        f = open(curdir + sep + self.path)
        self.wfile.write(f.read())
        f.close()
    
    def saveUsername(self, username):
        f = open("username", "w")
        f.write(username)
        f.close()
    
    def readUsername(self):
        f = open("username","r")
        username = f.read()
        return username

     def WriteCookie(self, value):
37     # Shows how to read form values from a POST request
38     # and write a cookie with a value from the form
39     self.send_response(200)
45     self.send_header('Content-type', 'text/html')
47     c = Cookie.SimpleCookie()
48     c['value'] = value
49     self.send_header('Set-Cookie', c.output(header=''))
50       self.end_headers()
51       
52     else:
53       self.end_headers()
54       self.wfile.write("No username ?")
55 
56   def ReadCookie(self):
57     if "Cookie" in self.headers:
58       c = Cookie.SimpleCookie(self.headers["Cookie"])
59       return c['value'].value
60     return None

try:

    if os.path.isfile("username"): 
        os.remove("username")

    if os.path.isfile("monitoring"): 
        os.remove("monitoring")
    #ATTENZIONE DA ELIMINARE SOLO PER PROVA!!!
    monitoring = sm.SensorMonitoring()
    monitoring.open()
    monitoring.create()
    monitoring.insertPos(4)
    date = datetime.now().strftime('%Y-%m-%d')
    time = datetime.now().strftime('%H:%M:%S')
    monitoring.insertValueByPos(152.36, 4, date, time)
    monitoring.insertDescByPos("Resistenza da 180Ohm", 4)
    monitoring.insertPos(6)
    time = datetime.now().strftime('%H:%M:%S')
    monitoring.insertValueByPos(0.32, 6, date, time)
    monitoring.insertDescByPos("Resistenza da 330Ohm", 6)
    monitoring.close()
    ##########
    
    #instanzio l'oggetto per interfacciarmi con la scheda di acquisizione phidgets
    #ph = phidgets.Phidgets()
    #ph.run()

    #Create a web server and define the handler to manage the
    #incoming request
    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print 'Started httpserver on port ' , PORT_NUMBER
    
    #Wait forever for incoming http requests
    server.serve_forever()
    try:
        pass
        #thread.start_new_thread( ph.run, ())#avvio la procedura di acquisizione
        #thread.start_new_thread( server.serve_forever, () )#avvio il web server
    except:
        print "Error: unable to start thread"

except KeyboardInterrupt:
    print '^C received, shutting down the web server'
    #ph.close()
    server.socket.close()

# while 1:
#    pass