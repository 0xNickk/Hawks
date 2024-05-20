from Core.common import *
from Core.settings import TCPServerSettings, HTTPFileServerSettings, SSLSettings
from Core.listener import TCPServer, HttpFileServer
from Core.menu import Menu
from Core.database import AgentsDB, ListenersDB
from Core.ssl_keys import generate_keys
import os



def main():

    if not os.path.exists("Loots"):
        os.mkdir("Loots")
        
    print_banner()
    
    print(f"{c.info} Initializing services:")
    
    agents_db = AgentsDB()
    agents_db.create_table()
    
    listeners_db = ListenersDB()
    listeners_db.create_table()


    if TCPServerSettings.SSL:
        SSLConfig()
      
    tcp_server = TCPServer(TCPServerSettings.bind_address, TCPServerSettings.bind_port, TCPServerSettings.buffer_size, TCPServerSettings.ngrok_tunnel, TCPServerSettings.SSL)
    tcp_server.start()
    
    if HTTPFileServerSettings.SSL:
        SSLConfig()
      
    http_server = HttpFileServer(HTTPFileServerSettings.bind_address, HTTPFileServerSettings.bind_port, HTTPFileServerSettings.SSL)
    http_server.start()
    
    print(f"\n{c.info} Welcome! Type 'help' to see available commands{c.RS}")
    
    Menu()
    

def SSLConfig():
    
    ssl_dir = SSLSettings.ssl_dir
    key_file = SSLSettings.key_file
    cert_file = SSLSettings.cert_file
    
    if not os.path.exists(ssl_dir):
        os.mkdir(ssl_dir)
    
    if not os.path.exists(ssl_dir + key_file) or not os.path.exists(ssl_dir + cert_file):
        generate_keys()


    
if __name__ == "__main__":
    main()
