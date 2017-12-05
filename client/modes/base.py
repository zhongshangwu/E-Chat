import enum
from client.routes import registry


class Mode(enum.Enum):
    COMMAND = 'command'
    CHAT = 'chat'
    QUERY = 'query'
    Login = 'login'


modes = set({'command', 'chat', 'query', 'login'})


class BaseHandler:

    def __init__(self, client, *args, **kwargs):
        self.client = client

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

    def _hook_statement(self, statement):
        ''' 子类实现 '''
        pass

    def process_statement(self, statement):
        if statement == '\h':
            self._print_help()
        if statement == '\d':
            self.destroy()
        if statement == '\c':
            pass
        else:
            self._hook(statement)
    
    def _hook_request(self, request):
        pass

    def process_request(self, request):
        req_command = request['command']
        func = registry[req_command]
        print('Command:', req_command)
        func(self.client.secure_channel, request=request['params'])
        self._hook_request(request)

        
        
