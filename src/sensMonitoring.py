'''
Created on 17 mag 2016

@author: Luigi
'''

import sqlite3
from _sqlite3 import Cursor

class SensorMonitoring:
    def __init__(self):
        self.open()
        
    def open(self):
        self.conn = sqlite3.connect("monitoring.db",check_same_thread=False)
        
    def close(self):
        self.conn.close()
        
    def create(self):
        self.conn.execute('''DROP TABLE IF EXISTS Sensori;''')
            
        self.conn.execute('''CREATE TABLE Sensori
       (POS INT PRIMARY KEY     NOT NULL,
       DESCRIPTION           TEXT,
       VALUE    REAL,
       DATA     TEXT,
       ORA    TEXT);''')
        self.conn.commit()
        #self.conn.close()
    
    def insertPosAndDesc(self, pos, description):
        self.conn.execute("INSERT INTO Sensori (POS,DESCRIPTION) \
      VALUES ("+str(pos)+", '"+description+"')");
        self.conn.commit()
        #self.conn.close()
        
    def insertPos(self, pos):
        self.conn.execute("INSERT INTO Sensori (POS) \
      VALUES ("+str(pos)+");")
        self.conn.commit()
        #self.conn.close()
        
    def insertValue(self, val,  pos, date,time):
        params = (str(val),date,time,str(pos))
        cursor = self.conn.execute("select count(*) from Sensori where POS=?", (str(pos)))
        
        for row in cursor:
            if row[0]>0:
                self.conn.execute("UPDATE Sensori set VALUE=?, DATA=?, ORA=? WHERE POS=?;", params)
            else:
                self.conn.execute("insert into Sensori (VALUE, DATA, ORA, POS) VALUES (?,?,?,?);", params)
        self.conn.commit()
        
    def insertDescByPos(self, desc, pos):
        params = (desc,str(pos))
        self.conn.execute("UPDATE Sensori set DESCRIPTION=? WHERE POS=?;", params)
        self.conn.commit()
        #self.conn.close()
        
    def insertValueByPos(self, val,pos, date, time):
        params = (str(val),date,time,str(pos))
        self.conn.execute("UPDATE Sensori SET VALUE=?, DATA=?,ORA=? WHERE POS=?;", params)
        self.conn.commit()
        #self.conn.close()
        
    def getValueByPos(self, pos):
        cursor = self.conn.execute("SELECT VALUE FROM Sensori WHERE POS="+str(pos)+";")
        for row in cursor:
            val = row[0]
        #self.conn.close()
        return val
    
    def getSensorList(self):
        cursor = self.conn.execute("SELECT POS,DESCRIPTION FROM Sensori;")
        sList = []
        for row in cursor:
            s = (row[0], row[1]) 
            sList.append(s)
        #self.conn.close()
        return sList
    
    def getSensorValue(self):
        cursor = self.conn.execute("SELECT DESCRIPTION, VALUE, DATA, ORA FROM Sensori;")
        sList = []
        for row in cursor:
            s = {'descr':row[0],'val':row[1],'date':row[2],'time':row[3]} 
            sList.append(s)
        #self.conn.close()
        return sList