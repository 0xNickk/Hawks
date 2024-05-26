class TCPServerSettings:
    bind_address = "0.0.0.0"
    bind_port    = 9001
    buffer_size  = 4096
    ngrok_tunnel = False
    ngrok_port   = None  # Port is randomly selected by ngrok (Free plan)
    ngrok_addr   = None  # Address is randomly selected by ngrok (Free plan)
    SSL          = False


class HTTPFileServerSettings:
    bind_address = "0.0.0.0"
    bind_port    = 8001
    SSL          = False


class SSLSettings:
    ssl_dir   = "./data/ssl/"
    cert_file = "cert.pem"
    key_file  = "key.pem"


class DataBaseSettings:
    data_path      = "./data/"
    databases_path = "./data/databases/"
    agents_file    = "agents.db"
    listeners_file = "listeners.db"


class CoreSettings:
    loot_path = "./data/Loots/"