from getpass import getpass
from client.modes.base import BaseHandler
from commands import Command


class RegisterHandler(BaseHandler):
 
    def _print_prefix(self):
        username = input('用户名:')
        password = getpass('密码:')
        _password = getpass('确认密码:')
        for i in range(0, 2):
            if password != _password:
                print('两次密码输入不一致:')
                password = getpass('密码:')
                _password = getpass('确认密码:')
            else:
                data = {
                    'username': username,
                    'password': password,
                }
                self.client.secure_channel.send(Command.REGISTER, data)
                print('注册中...')
                break
        else:
            print('注册失败!')
            self._command_mode()

    def _hook_statement(self, statement):
        pass

    def _hook_request(self, command, request):
        if command == Command.REGISTER_SUCCESS:
            print('恭喜, 注册成功!')
            print('用户名:%s' % request)
            self._command_mode()
        elif command == Command.USERNAME_EXIST:
            print('用户已存在!')
            self._command_mode()
