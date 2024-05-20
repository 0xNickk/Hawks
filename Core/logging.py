import readline


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
