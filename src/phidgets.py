'''
Created on 25 mag 2016

@author: Luigi
'''

from Phidgets.PhidgetException import PhidgetException
from Phidgets.Devices.InterfaceKit import InterfaceKit

import sensMonitoring as sm
from datetime import datetime

import time

class Phidgets:
    
    def __init__(self):
        self.V1 = 0.0
        self.V2list = [0,0,0,0,0,0,0] #lista dei valori associati alle porte analogiche, corrispondenza porta analogica posizione nella lista
        self.running = True
        
    def ponteDiWheatstone(self):
        R1 = 1000.0#1KOhm
        R2 = 1000.0#1KOhm
        R3 = 1000.0#1KOhm
        Vs = 5.0
        
        for pos, v in enumerate(self.V2list):
            if v==0:
                continue
            
            Vm = v-self.V1 #ingresso differenziale
            print Vm
            #formula per il calcolo della resistenza
            p1 = R3/(R1+R3) + (Vm/Vs)
            p2 = 1 - p1
            Rx = R2*(p1/p2);
            
            #
            date = datetime.now().strftime('%Y-%m-%d')
            time = datetime.now().strftime('%H:%M:%S')
            self.monitoring.insertValue(Rx, pos+1, date,time)
            #
            print ("la resistenza sull'input %d vale %f: " % (pos+1, Rx))

    def partitoreDiTensione(self, val):
        if val != 1:
            r1 = 1000
            Vref = 12 #5V tensione applicata al partitore
            V2 = (5.0/1023.0)*val #tensione letta ai capi della resistenza
            r2 =  r1*V2/(Vref-V2)
            print ("la resistenza vale %f: " % r2)
        
    def interfaceKitSensorChanged(self, e):
        source = e.device
        if e.value == 1:#1 indica che non sta nulla collegato e resetto anche il suo valore nella lista
            if e.index==0:
                self.V1=0
            else:
                self.V2list[e.index-1]=0
            return
        
        if e.index == 0:#V1 va collegato sempre sul pin 0
            self.V1 = (5.0/1023.0)*e.value 
            print self.V1
        else:
            val = (5.0/1023.0)*e.value
            self.V2list[e.index-1]=val #corrispondenza porta analogica posizione nella lista
            print str(self.V2list)
        
        self.ponteDiWheatstone()
            
        #if e.value != 1:
        #    self.monitoring.insertPos(e.index)
        #print("InterfaceKit %i: Sensor %i: %i" % (source.getSerialNum(), e.index, e.value))
    
    def run(self):
            try:
                self.interfaceKit = InterfaceKit() #instanzio la classe per interfacciarmi con la scheda di acquisizione
                self.monitoring = sm.SensorMonitoring() #tabella dove sono memorizzati i valori dei sensori collegati
                self.monitoring.open()
                self.monitoring.create()
            except RuntimeError as e:
                print("Runtime Exception: %s" % e.details)
                print("Exiting....")
                exit(1)
            
            try:
                self.interfaceKit.setOnSensorChangeHandler(self.interfaceKitSensorChanged)
            except PhidgetException as e:
                print("Exiting....")
                exit(1)
                
            try:
                self.interfaceKit.openPhidget()
            except PhidgetException as e:
                print("Exiting....")
                exit(1)
                
            try:
                self.interfaceKit.waitForAttach(10000)
            except PhidgetException as e:
                try:
                    self.interfaceKit.closePhidget()
                except PhidgetException as e:
                    exit(1)
                print("Assicurarsi di aver collegato la scheda di acquisizione Phidget 1019 al PC. Exiting....")
                exit(1)
            else:
                print "Scheda di acquisizione rilevata."
                
            for i in range(self.interfaceKit.getSensorCount()):
                try:
                    self.interfaceKit.setDataRate(i, 4)
                except PhidgetException as e:
                    pass
                
                 
    def close(self):
        self.running = False
        self.monitoring.close()
        print("Closing...")
        try:
            self.interfaceKit.closePhidget()
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            print("Exiting....")
            exit(1)
        
        print("Done.")
        exit(0)


