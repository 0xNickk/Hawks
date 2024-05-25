from os import system
import readline, sys

#Colors
ORANGE = '\033[93m'
YELLOW = '\u001b[33m'
RED = '\033[1;31m'
GREEN = '\033[38;5;82m'
RST = '\033[0m'
UNDERLINE = "\033[4m"
BOLD = '\033[1m'

ALERT = "[*]"
ADD = "[+]"
LOAD = "[~]"
ERROR = f"[{ORANGE}Error{RST}]"
INFO = f"[{GREEN}Info{RST}]"
FILESERVER = f"[{YELLOW}File-Server{RST}]"
SHELL = f"[{YELLOW}Shell{RST}]"
TCPSERVER = f"[{BOLD}TCP-Listener{RST}]"


class Helper:
    help_kill = f"\nTerminate a backdoor session\n{ORANGE}Usage{RST}: kill <session id> or all"
    help_sessions = f"\nPrint established backdoor sessions"
    help_alias = f"\nSet an alias for a session\n{ORANGE}Usage{RST}: alias <session id> <alias name>"
    help_interact = f"\nInteract with an agent\n{ORANGE}Usage{RST}: interact <session id>"
    help_shell = "\nEnable interactive shell with an agent"
    help_generate = f"\nGenerate payloads\n{ORANGE}Usage{RST}: generate <payload_template> <lhost> <options>\n'ngrok' as lhost if ngrok tunneling is enabled"
    help_download = f"\nDownload a file from agent\n{ORANGE}Usage{RST}: download <file path>"
    help_upload = f"\nUpload a file to agent\n{ORANGE}Usage{RST}: upload <local file path> <upload file path>"


class PayloadHelper:
    help_powershell = f"\nWindows PowerShell Reverse TCP\n{ORANGE}Required arguments{RST}: <lhost>\nSupported utilities: obfuscate"
    help_powershell_ssl = f"\nWindows PowerShell Reverse TCP SSL\n{ORANGE}Required arguments{RST}: <lhost>\nSupported utilities: obfuscate"


class MainPrompt:
    prompt = f"\n{UNDERLINE}Hawks{RST}> "

    @staticmethod
    def rst_prompt_menu():
        sys.stdout.write('\r' + MainPrompt.prompt + readline.get_line_buffer())

    @staticmethod
    def rst_shell_prompt(path):
        sys.stdout.write('\r' + path + readline.get_line_buffer())


class AutoComplete:
    defaultCommands = [
        "help ", "interact ", "generate ", "kill ", "clear", "shell", "screen", "upload ", "download ", "sessions ",
        "lhost=", "obfuscate", "rename ", "alias ", "windows/", "powershell_reverse_tcp", "exit", "ssl"]

    sessionsCommands = []

    def __init__(self):
        pass

    def auto_complete(self, command, state):

        options = [cmd for cmd in self.defaultCommands + self.sessionsCommands if cmd.startswith(command)]

        if state < len(options):
            return options[state]
        else:
            return None

    def parse_command(self, command):

        try:
            readline.add_history(command)

        except:

            if len(command) == 0:
                pass

        return command.split()

    def command_history(self):

        readline.set_completer(self.auto_complete)
        readline.parse_and_bind('tab: complete')

        readline.parse_and_bind('"\e[A": history-search-backward')
        readline.parse_and_bind('"\e[B": history-search-forward')


def print_banner():
    print(f'''

{RED}

    ╦ ╦ ┌─┐┬ ┬┬┌─┌─┐
    ╠═╣ ├─┤│││├┴┐└─┐
    ╩ ╩ ┴ ┴└┴┘┴ ┴└─┘ {RST}v2
    {RED}────────────────{ORANGE}  C2{RST}                
''')


def help():
    print(f'''
  {ORANGE}Command          {ORANGE}Description{RST}
  ───────          ───────────
  help       [~]   Print this message
  sessions   [+]   Print established backdoor sessions
  interact   [+]   Interact with an agent
  alias      [+]   Set an alias for a session
  generate   [+]   Generate payloads 
  download   [+]   Download a file from agent
  upload     [+]   Upload a file to agent
  kill       [+]   Terminate a session
  exit       [+]   Kill all sessions and quit
  clear      [~]   Clear screen


  shell      [+]   Enable interactive reverse shell
  screen     [~]   Get a screenshot of client screen

  Command with [+] required additional actions
  TAB for auto-completion commands
  For use details: {ORANGE} help <COMMAND> {RST}''')


def print_thanks_message():
    print(f"\n\nCreated by: {ORANGE}@0xNick{RST}\nThank you for using Hawks!")


def clear_screen():
    system("clear")
