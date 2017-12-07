from getpass import getpass
from client.modes.base import BaseHandler, Mode
from commands import Command
from client.modes.contact import ContactHandler


class LoginHandler(BaseHandler):
    
    def _print_prefix(self):
        username = input('用户名:')
        password = getpass('密码:')
        self.login(username, password)

    def login(self, username, password):
        data = {
            'username': username,
            'password': password
        }
        self.client.secure_channel.send(Command.LOGIN, data)

    def _hook_request(self, command, request):
        if command == Command.LOGIN_SUCCESS:
            print('登录成功!')
            self.client.user = request
            self.client.mode = Mode.CONTACT
            self.client.handler = ContactHandler(self.client)
        elif command == Command.LOGIN_FAILURE:
            print('登录失败!')
            self._command_mode()


