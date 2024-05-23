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


    @staticmethod
    def main_prompt():

        if SessionManager.current_session:

            for session_id, (socket, user) in SessionManager.current_session.items():
                computer_name = user.split("/")[0]
                return f"\n{UNDERLINE}Hawks{RST}({BOLD}{computer_name}){RST}> "
        else:
            return f"\n{UNDERLINE}Hawks{RST}> "

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
                            print(Helper.help_kill)
                            
                        elif second_arg == "sessions":
                            print(Helper.help_sessions)
                            
                        elif second_arg == "alias":
                            print(Helper.help_alias)
                        
                        elif second_arg == "interact":
                            print(Helper.help_interact)
                            
                        elif second_arg == "generate":
                            print(Helper.help_generate)

                        elif second_arg == "shell":
                            print(Helper.help_shell)

                        elif second_arg == "upload":
                            print(Helper.help_upload)
                            
                        elif second_arg == "download":
                            print(Helper.help_download)
                            
                        else:
                            print(f"\n{ALERT} No help available for {second_arg} command")
                            
                    
                elif main_arg  == "clear":
                    clear_screen()
                    
                elif main_arg  == "exit":
                    self.quit_hawks()
                    
                elif main_arg  == "sessions":
                    
                    if len(args) == 1:
                        session.view_sessions()
                    else:
                        print(f"\n{ALERT} Invalid argument")
                        
                        
                elif main_arg  == "alias":
                    
                    if len(args) < 3:
                        print(f"\n{ALERT} Missing <session id> or <alias name> argument")
                            
                    else:
                        session_id = second_arg.strip()
                        alias = args[2].strip()
                            
                        session.setAlias(session_id, alias)
                        
                        
                elif main_arg  == "kill":
                    
                    if len(args) < 2:
                        print(f"{ALERT} Missing <session id> argument")

                    else:
                        session_id = second_arg.strip()
                        
                        if session_id == "all":
                            session.killAllSessions()
                            
                        else:
                            session.killSession(session_id)
                    
                elif main_arg  == "interact":
                    
                    if len(args) < 2:
                        print(f"{ALERT}  Missing <session id> argument")
                        
                    else:
                        session_id = second_arg.strip()
                        session.interact_session(session_id)
                        
                    
                elif main_arg  == "shell":
                    
                    if not SessionManager.current_session:
                        print(f"\n{ALERT} No session selected")
                        
                    else:
                        socket = self.get_current_session_value()
                        agent = Agent(socket)
                        agent.shell()
                            
                            
                elif main_arg == "generate":
                    
                    if len(args) < 2:
                        print(f"\n{ALERT} Missing <payload_template> argument")
                        
                    else:
                        payload_template = args[1].strip()
                        
                        if len(args) < 3:  
                            
                            if payload_template == "windows/powershell_reverse_tcp":
                                print(Payload_Helper.help_powershell)
                                
                            elif payload_template == "windows/powershell_reverse_tcp_ssl":
                                print(Payload_Helper.help_powershell_ssl)
                                
                            else:
                                print(f"\n{ALERT} Payload template not found")
                                
                        else:

                            lhost = args[2].strip()     
                            port = TCPServerSettings.bind_port
                                
                            if "." not in lhost:
                                interface = psutil.net_if_addrs()
                                    
                                if lhost in interface:
                                    lhost  = interface[lhost][0].address

                                elif lhost == "ngrok":
                                    
                                    if not TCPServerSettings.ngrok_tunnel:
                                        print(f"\n{ALERT} Ngrok tunnel not active")
                                        continue
                                    
                                    lhost = TCPServerSettings.ngrok_addr
                                    port = TCPServerSettings.ngrok_port
                                    

                                else: 
                                    print(f"\n{ALERT} Network interface not found")
                                    continue
                                    
                            if len(args) > 3:
                                obfuscate = args[3].strip() 
                                
                                if obfuscate == "obfuscate":
                                    obfuscate = True  
                                else:
                                    print(f"\n{ALERT} Invalid argument")
                                    continue
                            else:
                                obfuscate = False
                            
                            payload = PayloadGenerator(payload_template, lhost, port, obfuscate)
                            payload.generatePayload()
                            
                            
                elif main_arg == "upload":
                    
                    if not SessionManager.current_session:
                        
                        print(f"\n{ALERT} No session selected")
                        
                    else:
                        
                        if len(args) < 3:
                            print(f"\n{ALERT} Missing <file path> <target path> arguments")
                            
                        else: 
                            local_path = args[1].strip()
                            upload_path = args[2].strip()

                            socket = self.get_current_session_value()
                            agent = Agent(socket)
                            agent.upload_file(local_path, upload_path)
                        
                                
                elif main_arg == "download":
                        
                    if not SessionManager.current_session:
                        print(f"\n{ALERT} No session selected")

                    else:
                        if len(args) < 2:
                            print(f"\n{ALERT} Missing <file path> argument")

                        else:
                            download_path = args[1].strip()

                            socket = self.get_current_session_value()
                            agent = Agent(socket)
                            agent.downloadFile(download_path)
                    
                else:
                    print(f"\n{ALERT} Invalid command")
                    
        except KeyboardInterrupt:
            self.quit_hawks()

    @staticmethod
    def get_current_session_value():
        for session_id, (socket, user) in SessionManager.current_session.items():
            return socket

    @staticmethod
    def quit_hawks():

        if SessionManager.agents_connections:

            confirm = input(f"\n\n{ALERT} Are you sure you want exit? All your connection/sessions will be {ORANGE}lost{RST} [y/n]: ")

            if confirm.lower().strip() in ["y", "yes"]:

                agents_db = AgentsDB()
                session = SessionManager()

                session.killAllSessions()
                agents_db.clear_table()

            else:
                return


        print_thanks_message()
        exit(0)

        