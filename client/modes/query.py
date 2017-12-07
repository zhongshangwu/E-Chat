import time
from client.modes.base import BaseHandler
from commands import Command


class QueryHandler(BaseHandler):
    
    def _hook_statement(self, statement):
        if statement == 'server time':
            self.client.secure_channel.send(Command.QUERY_SERVER_TIME, None)

    def _hook_request(self, command, request):
        if command == Command.SEND_SERVER_TIME:
            time_array = time.localtime(request)
            message = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
            print('Server time：%s' % message)
            self._print_prefix()
