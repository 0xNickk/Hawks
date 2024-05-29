import threading

from Core.common import *
from Core.settings import TCPServerSettings, HTTPFileServerSettings, SSLSettings, CoreSettings
from Core.listener import TCPServer, HttpFileServer
from Core.menu import Menu
from Core.database import AgentsDB, ListenersDB
from Core.ssl_keys import generate_keys
import os



def main():

    if not os.path.exists(CoreSettings.loot_path):
        os.mkdir(CoreSettings.loot_path)
        
    print_banner()
    
    print(f"{INFO} Initializing services:")
    
    agents_db = AgentsDB()
    agents_db.create_table()
    
    listeners_db = ListenersDB()
    listeners_db.create_table()

    if TCPServerSettings.SSL or HTTPFileServerSettings.SSL:
        SSLConfig()

    tcp_server = TCPServer(TCPServerSettings.bind_address, TCPServerSettings.bind_port, TCPServerSettings.buffer_size, TCPServerSettings.ngrok_tunnel, TCPServerSettings.SSL)
    http_server = HttpFileServer(HTTPFileServerSettings.bind_address, HTTPFileServerSettings.bind_port, HTTPFileServerSettings.SSL)

    tcp_server.start()
    http_server.start()

    print(f"\n{INFO} Welcome! Type 'help' to see available commands{RST}")

    Menu()
    

def SSLConfig():

    ssl_dir = SSLSettings.ssl_dir

    if not os.path.exists(ssl_dir):
        os.mkdir(ssl_dir)


    if len(os.listdir(ssl_dir)) == 2:

        try:

            prompt = input(f"{ADD} Found existing SSL keys{RST}, use them? (y/n) : ")
            if prompt.lower() == "y":
                return

        except KeyboardInterrupt:
            exit()
    else:
        if SSLSettings.auto_generate_keys:
            generate_keys()
        else:
            print(f"{ERROR} SSL keys not found, please generate them")
            exit()




if __name__ == "__main__":
    main()
