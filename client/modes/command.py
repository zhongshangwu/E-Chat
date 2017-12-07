from client.modes.base import BaseHandler, Mode


class CommandHandler(BaseHandler):
    
    def _hook_statement(self, statement):
        from client.modes import modes as _modes
        if not statement:
            self._print_prefix()
        elif statement not in [i.value for i in _modes]:
            self._wrong_command()
        else:
            self.client.mode = Mode(statement)
            self.client.handler = _modes[self.client.mode](self.client)
