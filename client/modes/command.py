from client.modes.base import BaseHandler, modes


class CommandHandler(BaseHandler):
    
    def _hook(self, statement):
        if not statement:
            self._print_prefix()
        elif statement not in modes:
            self._wrong_command()
        elif statement == 'help':
            print("Help...")
        elif statement == 'login':
            print("Login...")
        elif statement == 'register':
            print("Register..")