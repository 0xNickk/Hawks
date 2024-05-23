from .common import *
from .logging import AutoComplete
from .database import AgentsDB
import binascii
import os


class SessionManager:

    current_session = {}  #sessionId: socket, user, computerName
    agents_connections = {}  #sessionId: socket
    sessions_alias = {}  #alias: sessionId
    loots_paths = {}  #sessionId: lootPath

    def __init__(self):
        self.killAll = False

    @staticmethod
    def createSessionId():

        seed = binascii.b2a_hex(os.urandom(9)).decode('utf-8')
        session_id = '-'.join([seed[i:i + 6] for i in range(0, len(seed), 6)])

        return session_id

    @staticmethod
    def view_sessions():

        agents_db = AgentsDB()
        agents = agents_db.get_agents()

        if not agents:
            print(f"\n{ALERT} No active sessions")
            return

        fields = ['session_id', 'agent_ip', 'os', 'user', 'status']
        field_names = ['Session ID', 'IP Address', 'OS', 'User', 'Status']

        max_lengths = {field: max(max(len(agent[field]), len(field_name)) for agent in agents) + 1 for field, field_name
                       in zip(fields, field_names)}

        print("\n" + " ".join(f"{field_name:<{max_lengths[field]}}" for field, field_name in zip(fields, field_names)))
        print(" ".join(f"{'-' * max_lengths[field]:<{max_lengths[field]}}" for field in fields))

        for agent in agents:
            status_color = GREEN if agent['status'] == 'Active' else ORANGE
            print(" ".join(
                f"{agent[field] if field != 'status' else status_color + agent[field] + RST:<{max_lengths[field]}}" for
                field in fields))


    def valid_session_id(self, session_id):

        agents_db = AgentsDB()

        if session_id == "all":
            self.killAll = True
            return True

        elif not agents_db.valid_session_id(session_id):
            print(f"\n{ALERT} Invalid session id")
            return False

        else:
            return True

    def interact_session(self, session_id):

        agents_db = AgentsDB()

        if self.valid_session_id(session_id):

            if self.current_session:
                self.current_session.clear()

            socket = self.agents_connections[session_id]
            user = agents_db.get_agent_user(session_id)
            self.current_session[session_id] = socket, user

            print(f"\n{INFO} Interactive session with {GREEN}{user}{RST} as started")

        else:
            return

    def killSession(self, session_id):
        agents_db = AgentsDB()

        if self.valid_session_id(session_id):

            if self.killAll:
                self.killAllSessions()

            else:

                user = agents_db.get_agent_user(session_id)
                confirm = input(f"\n{ADD} Are you sure you want kill this session ({GREEN}{user}{RST}) [y/n]: ")

                if confirm.lower().strip() in ["y", "yes"]:
                    agents_db.delete_agent(session_id)
                    conn = self.agents_connections[session_id]

                    conn.close()
                    self.clearSession(session_id)

                    print(f"{INFO} Session terminated")

            return

    def clearSession(self, session_id, agents_db=AgentsDB()):

        if self.sessions_alias.get(session_id):
            del self.sessions_alias[session_id]

        del self.agents_connections[session_id]
        del self.loots_paths[session_id]

        AutoComplete.defaultCommands.remove(session_id)
        self.current_session.clear()

        agents_db.delete_agent(session_id)

    def killAllSessions(self):

        agents_db = AgentsDB()
        agents = agents_db.get_agents()

        if agents:

            for agent in agents:

                session_id = agent['session_id']
                conn = self.agents_connections[session_id]

                try:

                    conn.close()
                    self.clearSession(session_id)

                except ConnectionError:
                    pass

            agents_db.clear_table()
            print(f"\n{INFO} All sessions terminated")

        else:
            print(f"\n{ALERT} No active sessions")

    def setAlias(self, session_id, alias):
        agents_db = AgentsDB()

        if self.valid_session_id(session_id):

            if self.sessions_alias.get(alias):
                print(f"\n{ALERT} Alias name {alias} already in use")
                return

            else:

                if self.agents_connections.get(session_id):
                    socket = self.agents_connections.pop(session_id)
                    self.agents_connections[alias] = socket

                if session_id in AutoComplete.defaultCommands:
                    AutoComplete.defaultCommands.remove(session_id)
                    AutoComplete.defaultCommands.append(alias)

                if session_id in self.loots_paths:
                    loot_path = self.loots_paths.pop(session_id)
                    self.loots_paths[alias] = loot_path

                agents_db.set_alias(session_id, alias)
                self.sessions_alias[alias] = session_id

                print(f"\n{INFO} Alias ({alias}) set for session: {RST}{agents_db.get_agent_user(alias)}{RST}")


