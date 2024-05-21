from .common import *
from .settings import TCPServerSettings, SSLSettings
from .agent import Agent, FileHandler

from pyngrok import ngrok
from http.server import HTTPServer
from pyngrok.exception import PyngrokNgrokError
import socket, ssl, threading



class TCPServer:

    def __init__(self, bind_address, bind_port, buffer_size, ngrok_tunnel, ssl_enabled):

        self.bind_address = bind_address
        self.bind_port    = bind_port
        self.buffer_size  = buffer_size
        self.ngrok_tunnel = ngrok_tunnel
        self.is_listen    = False
        self.ssl_enabled  = ssl_enabled


    def create_socket(self):

        tcp_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcp_listener.bind((self.bind_address, self.bind_port))

        return tcp_listener

    def start(self):

        ssl_tcp_enabled = ""

        try:

            if self.ssl_enabled:

                context = SSLSetup.setup_ssl_context(SSLSettings.ssl_dir + SSLSettings.cert_file, SSLSettings.ssl_dir + SSLSettings.key_file)
                self.tcp_listener = self.create_socket()
                self.tcp_listener = context.wrap_socket(self.tcp_listener, server_side=True)
                ssl_tcp_enabled = "(SSL)"


            else:
                self.tcp_listener = self.create_socket()

        except socket.error:

            print(f"\n{c.alt} {c.O}Error{c.RS}: Failed to start TCP Listener, port seems already in use")
            exit(0)

        except Exception as e:

            print(f"\n{c.alt} {c.O}Error{c.RS}: Failed to start TCP Listener, {e}")
            exit(0)

        if self.ngrok_tunnel:

            try:

                ngrok_tunnel = ngrok.connect(f"{self.bind_address}:{self.bind_port}", "tcp")
                self.bind_address = ngrok_tunnel.public_url.split(":")[1].replace("//", "")
                self.bind_port = int(ngrok_tunnel.public_url.split(":")[2])

                TCPServerSettings.ngrok_addr = self.bind_address
                TCPServerSettings.ngrok_port = self.bind_port


            except PyngrokNgrokError:

                print(f"\n{c.alt} {c.O}Failed{c.RS} to start ngrok TCP tunnel, check ngrok configuration")
                return

            except Exception as e:

                print(f"\n{c.alt} {c.O}Failed{c.RS} to start ngrok TCP tunnel, {e}")
                return

        print(f"\n{c.bold}TCP Multi-Handler:: {c.RS}{c.Y}{self.bind_address}{c.RS}:{c.Y}{self.bind_port}{c.RS} {ssl_tcp_enabled}")

        self.is_listen = True
        self.tcp_listener.listen()

        threading.Thread(target=self.listen, daemon=True, name="tcpListenerThread").start()

    def listen(self):

        while self.is_listen:
            conn, agent_ip = self.tcp_listener.accept()

            agent = Agent(conn)
            agent.save_agent(agent_ip)


    def stopTCPServer(self):

        self.is_listen = False
        self.tcp_listener.close()


class HttpFileServer:

    def __init__(self, bind_address, bind_port, ssl_enabled):

        self.bind_address = bind_address
        self.bind_port    = bind_port
        self.SSL          = ssl_enabled

    def start(self):

        ssl_http_enabled = ""

        try:

            self.file_server = HTTPServer((self.bind_address, self.bind_port), FileHandler)

            if self.SSL:

                context = SSLSetup.setup_ssl_context(SSLSettings.ssl_dir + SSLSettings.cert_file,SSLSettings.ssl_dir + SSLSettings.key_file)
                self.file_server.socket = context.wrap_socket(self.file_server.socket, server_side=True)
                ssl_http_enabled = "(SSL)"

            print(f"{c.bold}HTTP File Server:: {c.RS}{c.Y}{self.bind_address}{c.RS}:{c.Y}{self.bind_port}{c.RS} {ssl_http_enabled}")
            threading.Thread(target=self.file_server.serve_forever, daemon=True, name="httpServerThread").start()

        except OSError:

            print(f"\n{c.alt} {c.O}Error{c.RS}: Failed to start HTTP File Server, unknown error occurred.")
            exit(0)


    def stopHttpServer(self):

        self.file_server.shutdown()
        self.file_server.server_close()



class SSLSetup:

    @staticmethod
    def setup_ssl_context(cert_file, key_file):

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

        try:
            context.load_cert_chain(cert_file, key_file)

        except FileNotFoundError:
            print(f"\n{c.alt} {c.O}Error{c.RS}: Failed to start SSL Server, cert.pem or key.pem not found")
            exit(0)

        return context
