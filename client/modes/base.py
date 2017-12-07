import enum
from commands import Command


class Mode(enum.Enum):
    COMMAND = 'command'
    CHAT = 'chat'
    QUERY = 'query'
    Login = 'login'
    REGISTER = 'register'
    CONTACT = 'contact'


class BaseHandler:

    def __init__(self, client, *args, **kwargs):
        self.client = client
        self._print_prefix()

    def _print_prefix(self):
        mode = self.client.mode
        chat_room = self.client.chat_room
        if mode == Mode.COMMAND:
            print('command> ', end='', flush=True)
        elif mode == Mode.CHAT:
            print('[%s]> ' % chat_room, end='', flush=True)
        elif mode == Mode.QUERY:
            print('query> ', end='', flush=True)

    def _wrong_command(self):
        print('Type "help" for more information.')
        self._print_prefix()

    def _print_help(self):
        ''' 打印帮助 '''
        print("Chat client commads and syntax:")
        print("-   @<user/group> \"<message>\" : Send message to user or group")
        print("-   ? : Get number of unread messages")
        print("-   read : Read all unread messages")
        print("-   +<user> \"<keyword>\" : Add mapping to contacts list")
        print("-   <group>=<user1>+<user2>+... : Create multicast group")
        print("-   <group>+=<user> : Add user to existing group")
        print("-   find <keyword> : Find contact using keyword")
        print("-   help : Print(this help message")
        print("-   quit : Quit chat")
        self._print_prefix()
    
    def _command_mode(self):
        from client.modes.command import CommandHandler
        self.client.mode = Mode.COMMAND
        self.client.handler = CommandHandler(self.client)

    def _hook_statement(self, statement):
        ''' 子类实现 '''
        pass

    def process_statement(self, statement):
        if statement == 'help':
            self._print_help()
        elif statement == '\d':
            self.destroy()
        elif statement == '\c':
            self._command_mode()
        else:
            self._hook_statement(statement)
    
    def _hook_request(self, command, request):
        pass

    def process_request(self, request):
        command = request['command']
        request = request['params']
        if command == Command.LOGIN_BUNDLE:
            self.client.chat_rooms = request['chat_rooms']
            self.client.friends = request['friends']
            self.client.pending_requests = request['pending_requests']
            # self.client.messages = request['messages']
            for message in request['messages']:
                sent = message['sent']
                self._handle_messages(message, not sent)
        if command == Command.INCOMMING_FRIEND_REQUEST:
            self.client.pending_requests.append(request)
        if command == Command.ON_NEW_MESSAGE:
            self._handle_messages(request, unread=True)
        if command == Command.ON_NEW_ROOM:
            self.client.chat_rooms.append(request)
        self._hook_request(command, request)

    def _handle_messages(self, message, unread=True):
        # 更新聊天记录
        self.client.chat_history[message['target_type']].\
            setdefault(message['target'], [])
        self.client.\
            chat_history[message['target_type']][message['target']].\
            append(message)
        
        if not unread:
            return

        # 更新未读消息
        self.client.unread_messages[message['target_type']].\
            setdefault(message['target'], {'count': 0, 'content': []})
        self.client.\
            unread_messages[message['target_type']][message['target']]['count'] +=1
        self.client.\
            unread_messages[message['target_type']][message['target']]['content'].append(message)
        
