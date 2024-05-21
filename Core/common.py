from os import system


class c:
    O = '\033[93m'  # orange
    Y = '\u001b[33m'  # yellow
    R = '\033[1;31m'  # red
    G = '\033[38;5;82m'  # green
    RS = '\033[0m'  # default color
    UND = "\033[4m"  # underline
    bold = '\033[1m'
    alt = "[*]"
    add = "[+]"
    load = "[~]"
    error = f"{O}error{RS}"
    info = f"[{G}info{RS}]"


class Message:
    missSessionId = f"\n{c.alt} Missing <session id> argument"
    shellClosed = "\n[*] Shell deactivated"


def print_banner():
    print(f'''

{c.R}

    ╦ ╦ ┌─┐┬ ┬┬┌─┌─┐
    ╠═╣ ├─┤│││├┴┐└─┐
    ╩ ╩ ┴ ┴└┴┘┴ ┴└─┘ {c.RS}v2
    {c.R}────────────────{c.O}  C2{c.RS}                
''')


def help():
    print(f'''
  {c.O}Command          {c.O}Description{c.RS}
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
  For use details: {c.O} help <COMMAND> {c.RS}''')


def thanks():
    print(f"\n\nCreated by: {c.O}@0xNick{c.RS}\nThank you for using Hawks!")


def help_kill():
    print(f"\nTerminate a backdoor session\n{c.O}Usage{c.RS}: kill <session id> or all")


def help_sessions():
    print(f"\nPrint established backdoor sessions")


def help_alias():
    print(f"\nSet an alias for a session\n{c.O}Usage{c.RS}: alias <session id> <alias name>")


def help_interact():
    print(f"\nInteract with an agent\n{c.O}Usage{c.RS}: interact <session id>")


def help_shell():
    print(f"\nEnable interactive shell with an agent")


def help_generate():
    print(f"\nGenerate payloads\n{c.O}Usage{c.RS}: generate <payload_template> <lhost> <options>\n'ngrok' as lhost if ngrok tunneling enabled")


def help_powershell_payload():
    print(f"\nWindows PowerShell Reverse TCP\n{c.O}Required arguments{c.RS}: <lhost>\nSupported utilities: obfuscate")


def help_powershell_ssl_payload():
    print(f"\nWindows PowerShell Reverse TCP SSL\n{c.O}Required arguments{c.RS}: <lhost>\nSupported utilities: obfuscate")


def help_download():
    print(f"\nDownload a file from agent\n{c.O}Usage{c.RS}: download <file path>")


def help_upload():
    print(f"\nUpload a file to agent\n{c.O}Usage{c.RS}: upload <local file path> <upload file path>")


def clear_screen():
    system("clear")
