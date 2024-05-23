import subprocess
from stem.control import Controller
import os



def torInstalled(self):
    
    result = subprocess.run(['which', 'tor'], stdout=subprocess.PIPE)
    
    if result:
        return True
    else:
        return False
    
def torConnection(self):
    
    try:
    
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            
            hiddenService = os.path.join(controller.get_conf('DataDirectory', os.getcwd()), 'hiddenService')
            result = controller.create_hidden_service(path=hiddenService, port=80, target_port=9001)
            
            if result and result.hostname:
                print(f'Service is available at {result.hostname}')
            
            else:
                print('Failed to create a hidden service. Please check Tor configuration and logs.')
                
    except Exception as e:
        print(e)slice
    
    
def torConfig(self):
    
    torrcFile = "/etc/tor/torrc"
    controlPortExists = False
    
    if not os.path.exists(torrcFile):
        print(f"{ALERT} Tor configuration file not found")
        exit(0)
        
    else:
        
        print(f"{INFO} Setting up ControlPort in torrc file ...")
        
        try:
            with open(torrcFile, "r") as file:
                lines = file.readlines()

            for line in lines:
                                
                if "ControlPort" in line:
                    controlPortExists = True

            with open(torrcFile, "w") as file:
                
                for line in lines:
                    file.write(line)
                    
                if not controlPortExists:
                    file.write("ControlPort 9051\n")
                    
            self.torConnection()


        except:
            print(f"{ALERT} Failed to write to torrc file, start Hawks using sudo")
            exit(0)
        
        