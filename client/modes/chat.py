import datetime
from client.modes.base import BaseHandler
from commands import Command


class ChatHandler(BaseHandler):

    def __init__(self, client, target_type=1, target='default'):
        print("In Chat Mode...")
        self.client = client
        self.target = target
        self.target_type = target_type
        self._display_chat_history()
        self._print_prefix()

    def _display_chat_history(self):
        if self.target in self.client.chat_history[self.target_type]:
            for msg in self.client.chat_history[self.target_type][self.target]:
                self._display_message(msg)
            print('------ 以上是历史消息 ------')
        self._clear_unread_messages()
    
    def _display_message(self, message):
        send_time = datetime.datetime.fromtimestamp(
            int(message['send_time'])
        ).strftime('%Y-%m-%d %H:%M:%S')
        if (message['sender'] == self.client.user):
            print('[{}] me says: {}'.format(send_time, message['content']))
        else:
            print('[{}] {} says: {}'.format(send_time, message['sender'], message['content']))
        
    def _clear_unread_messages(self):
        # 清除未读消息
        if self.target in self.client.unread_messages[self.target_type]:
            self.client.\
                unread_messages[self.target_type][self.target]['count'] = 0
            self.client.\
                unread_messages[self.target_type][self.target]['content'] = []

    def _print_prefix(self):
        print('%s> ' % self.target, end='', flush=True)
    
    def _hook_statement(self, statement):
        message = {
            'target_type': self.target_type,
            'target': self.target,
            'content': statement
        }
        self.client.secure_channel.send(Command.SEND_MESSAGE, message)
        # self._print_prefix()

    def _hook_request(self, command, request):
        if command == Command.ON_NEW_MESSAGE:
            self._display_message(request)
            self._clear_unread_messages()
            self._print_prefix()
        if command == Command.ON_MEMBER_ONLINE:
            if self.target_type == 1 and self.target == request['roomname']:
                print('群员：【%s】上线了！' % request['membername'])
                self._print_prefix()
        if command == Command.ON_FRIEND_ONLINE:
            print('你的好友：【%s】上线了！' % request)
            self._print_prefix()
