import sqlite3
from .common import *
from .settings import DataBaseSettings
import os



class AgentsDB:
    def __init__(self):
        
        try:
            
            data_path = DataBaseSettings.data_path
            agents_file = DataBaseSettings.agents_file
            databases_path = DataBaseSettings.databases_path
        
            if not os.path.exists(data_path):
                os.mkdir(data_path)
                
            if not os.path.exists(databases_path):
                os.mkdir(databases_path)
                
                with open(databases_path + agents_file, "w") as agentDb:
                    pass

        except OSError:

            print(f"{c.alt} {c.O}Error{c.RS}: Could not create databases directory")

        try:
            
            self.dbPath  = databases_path + agents_file
            self.dbConn  = sqlite3.connect(self.dbPath)
            self.cursor  = self.dbConn.cursor()
            
        except sqlite3.Error:

            print(f"{c.alt} {c.O}Error{c.RS}: Could not open database file agents.db")
            
        
    def create_table(self):

        self.cursor.execute(

            '''
            CREATE TABLE IF NOT EXISTS agents
            (   
                session_id   TEXT     PRIMARY KEY,
                external_ip  TEXT,
                os          TEXT,
                user        TEXT,
                status      TEXT
            )
            '''
        )
        
        self.dbConn.commit()
        
        
    def add_agent(self, session_id, external_ip, os, user, status):

        self.cursor.execute("INSERT INTO agents (session_id, external_ip, os, user, status) VALUES (?, ?, ?, ?, ?)", (session_id, external_ip, os, user, status))
        self.dbConn.commit()

    def update_agent_status(self, session_id, status):
        
        self.cursor.execute("UPDATE agents SET status=? WHERE session_id=?",  (status, session_id))
        self.dbConn.commit()
        
    def delete_agent(self, session_id):

        self.cursor.execute("DELETE FROM agents WHERE session_id=?", (session_id,))
        self.dbConn.commit()
        
    def valid_session_id(self, session_id):

        self.cursor.execute("SELECT session_id FROM agents WHERE session_id=?", (session_id,))
        session_id = self.cursor.fetchone()
        return session_id[0] if session_id else None
        
    def get_agents(self):

        self.cursor.execute("SELECT * FROM agents")
        rows = self.cursor.fetchall()
        agents = [{"session_id": row[0], "external_ip": row[1], "os": row[2], "user": row[3], "status": row[4]} for row in rows]
        return agents
    
    def get_agent_user(self, session_id):

        self.cursor.execute("SELECT user FROM agents WHERE session_id=?", (session_id,))
        user = self.cursor.fetchone()
        return user[0] if user else None
    
    def clear_table(self):

        self.cursor.execute("DELETE FROM agents")
        self.dbConn.commit()

    def set_alias(self, session_id, alias):

        self.cursor.execute("UPDATE agents SET session_id=? WHERE session_id=?", (alias, session_id))
        self.dbConn.commit()

        
    def get_agent_status(self, session_id):

        self.cursor.execute("SELECT status FROM agents WHERE session_id=?", (session_id,))
        status = self.cursor.fetchone()
        return status[0] == "Active" if status else None
    
    

class ListenersDB:
    def __init__(self):
        
        try:
                
            data_path = DataBaseSettings.data_path
            listeners_file = DataBaseSettings.listeners_file
            databases_path = DataBaseSettings.databases_path

            if not os.path.exists(data_path):
                os.mkdir(data_path)
                
            if not os.path.exists(databases_path):
                os.mkdir(databases_path)
                
                with open(databases_path + listeners_file, "w") as listenersDb:
                    pass
            
        except OSError:

            print(f"{c.alt} {c.O}Error{c.RS}: Could not create databases directory")
        
        try:
            
            self.dbPath  = databases_path + listeners_file
            self.dbConn  = sqlite3.connect(self.dbPath)
            self.cursor  = self.dbConn.cursor()
            
        except sqlite3.Error as e:

            print(f"{c.alt} {c.O}Error{c.RS}: Could not open database file listeners.db")
            
            
    def create_table(self):

        self.cursor.execute(
            
            '''
            CREATE TABLE IF NOT EXISTS listeners
            (   
                listener_id   TEXT     PRIMARY KEY,
                bind_address  TEXT,
                bind_port     INTEGER,
                ssl          TEXT
            )
            '''
        )
        
        self.dbConn.commit()

        

    def add_listener(self, listener_id, bind_address, bind_port, ssl):

        self.cursor.execute("INSERT INTO listeners (listener_id, bind_address, bind_port, ssl) VALUES (?, ?, ?, ?)", (listener_id, bind_address, bind_port, ssl))
        self.dbConn.commit()

        
    def delete_listener(self, listener_id):

        self.cursor.execute("DELETE FROM listeners WHERE listener_id=?", (listener_id,))
        self.dbConn.commit()
        
    
    def get_listeners(self):

        self.cursor.execute("SELECT * FROM listeners")
        rows = self.cursor.fetchall()
        listeners = [{"listener_id": row[0], "bind_address": row[1], "bind_port": row[2], "ssl": row[3]} for row in rows]
        return listeners
    


