#!/usr/bin/env python

#Basic imports
import sensMonitoring as sm
from datetime import datetime

#Phidget specific imports
from Phidgets.PhidgetException import PhidgetException
from Phidgets.Devices.InterfaceKit import InterfaceKit

Wheatstone = True 
V1 = 0.0
V2 = 0.0

#Create an interfacekit object
try:
    interfaceKit = InterfaceKit()
    monitoring = sm.SensorMonitoring() #tabella dove sono memorizzati i valori dei sensori collegati
    monitoring.open()
    monitoring.create()
except RuntimeError as e:
    print("Runtime Exception: %s" % e.details)
    print("Exiting....")
    exit(1)

#Information Display Function
def displayDeviceInfo():
    pass
#     print("|------------|----------------------------------|--------------|------------|")
#     print("|- Attached -|-              Type              -|- Serial No. -|-  Version -|")
#     print("|------------|----------------------------------|--------------|------------|")
#     print("|- %8s -|- %30s -|- %10d -|- %8d -|" % (interfaceKit.isAttached(), interfaceKit.getDeviceName(), interfaceKit.getSerialNum(), interfaceKit.getDeviceVersion()))
#     print("|------------|----------------------------------|--------------|------------|")
#     print("Number of Digital Inputs: %i" % (interfaceKit.getInputCount()))
#     print("Number of Digital Outputs: %i" % (interfaceKit.getOutputCount()))
#     print("Number of Sensor Inputs: %i" % (interfaceKit.getSensorCount()))

#Event Handler Callback Functions
def interfaceKitAttached(e):
    attached = e.device
    #print("InterfaceKit %i Attached!" % (attached.getSerialNum()))

def interfaceKitDetached(e):
    detached = e.device
    #print("InterfaceKit %i Detached!" % (detached.getSerialNum()))

def interfaceKitError(e):
    try:
        source = e.device
        print("InterfaceKit %i: Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))

def interfaceKitInputChanged(e):
    source = e.device
    #print("InterfaceKit %i: Input %i: %s" % (source.getSerialNum(), e.index, e.state))

def ponteDiWheatstone(pos):
    global V1
    global V2
    R1 = 1000.0
    R2 = 1000.0
    R3 = 1000.0
    Vs = 5.0
    Vm = V2-V1
    print Vm
    p1 = R3/(R1+R3) + (Vm/Vs)
    p2= 1 - p1
    Rx = R2*(p1/p2);
    
    #
    date = datetime.now().strftime('%Y-%m-%d')
    time = datetime.now().strftime('%H:%M:%S')
    monitoring.insertValueByPos(Rx, pos,date,time)
    #
    print ("la resistenza vale %f: " % Rx)

def partitoreDiTensione(val):
    if val != 1:
        r1 = 1000
        Vref = 12 #5V tensione applicata al partitore
        V2 = (5.0/1024.0)*val #tensione letta ai capi della resistenza
        r2 =  r1*V2/(Vref-V2)
        print ("la resistenza vale %f: " % r2)
    
def interfaceKitSensorChanged(e):
    source = e.device
    global V1
    global V2
    if e.index == 4:
        V1 = (5.0/1024.0)*e.value 
        print V1
    elif e.index == 5:
        V2 = (5.0/1024.0)*e.value
        print V2
    if V1 != 0.0 and V2 != 0.0:
        ponteDiWheatstone(e.index)
        
    if e.value != 1:
        monitoring.insertPos(e.index)
    #print("InterfaceKit %i: Sensor %i: %i" % (source.getSerialNum(), e.index, e.value))

def interfaceKitOutputChanged(e):
    source = e.device
    #print("InterfaceKit %i: Output %i: %s" % (source.getSerialNum(), e.index, e.state))

#Main Program Code
try:
    #logging example, uncomment to generate a log file
    #interfaceKit.enableLogging(PhidgetLogLevel.PHIDGET_LOG_VERBOSE, "phidgetlog.log")
    
    interfaceKit.setOnAttachHandler(interfaceKitAttached)
    interfaceKit.setOnDetachHandler(interfaceKitDetached)
    interfaceKit.setOnErrorhandler(interfaceKitError)
    interfaceKit.setOnInputChangeHandler(interfaceKitInputChanged)
    interfaceKit.setOnOutputChangeHandler(interfaceKitOutputChanged)
    interfaceKit.setOnSensorChangeHandler(interfaceKitSensorChanged)
    
except PhidgetException as e:
   # print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    exit(1)

#print("Opening phidget object....")

try:
    interfaceKit.openPhidget()
except PhidgetException as e:
    #print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    exit(1)

#print("Waiting for attach....")

try:
    interfaceKit.waitForAttach(10000)
except PhidgetException as e:
   # print("Phidget Exception %i: %s" % (e.code, e.details))
    try:
        interfaceKit.closePhidget()
    except PhidgetException as e:
     #   print("Phidget Exception %i: %s" % (e.code, e.details))
     #   print("Exiting....")
        exit(1)
    print("Exiting....")
    exit(1)
else:
    displayDeviceInfo()

interfaceKit.setOutputState(7, 1)
val = interfaceKit.getSensorValue(5)
print(val)


#print("Setting the data rate for each sensor index to 4ms....")
for i in range(interfaceKit.getSensorCount()):
    try:
        
        interfaceKit.setDataRate(i, 4)
    except PhidgetException as e:
        pass
        #print("Phidget Exception %i: %s" % (e.code, e.details))


print("Closing...")
interfaceKit.setOutputState(7, 0)
try:
    interfaceKit.closePhidget()
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    exit(1)

print("Done.")
exit(0)



