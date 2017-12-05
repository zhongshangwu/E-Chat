import enum
import time


commands = dict()


class Command(enum.IntEnum):
    ''' 命令类型 '''

    LOGIN = 1  # [username, password]
    REGISTER = 2  # [username, password, nickname]
    ADD_FRIEND = 3  # username:str
    SOLVE_FRIEND_REQUEST = 4
    JOIN_ROOM = 5  # id:int
    CREATE_ROOM = 6  # name: str
    query_room_users = 7  # id:int
    QUERY_SERVER_TIME = 8

    # {target_type:int(0=私聊 1=群聊),target_id:int,message:str}
    SEND_MESSAGE = 100

    LOGIN_SUCCESSFUL = 101
    REGISTER_SUCCESSFUL = 102
    INCOMING_FRIEND_REQUEST = 103
    CONTACT_INFO = 104
    CHAT_HISTORY = 105
    SEND_SERVER_TIME = 106
    ADD_FRIEND_REQUEST = 107
    ON_FRIEND_OFF_LINE = 108
    SHOW_CHAT_HISTORY = 109
    ON_NEW_MESSAGE = 110
    SERVER_KICK = 111
    SHOW_ROOM_USERS = 112
    ON_ROOM_USER_OFF_LINE = 113
    LOGIN_BUNDLE = 114
    LOGIN_FAILURE = 115
    USERNAME_TOKEN = 116
    FAILURE = 117
    MSG = 118
    BROADCASR = 119

    COMMAND_WRONG = 201


def get_command_from_value(value):
    if value not in commands:
        return Command(201)
    return Command(value)


# 柯里化
# partial
# 装饰器实现注册机制，类似路由


def comand_register(command=None):
    def decorate(func):
        commands[command] = func

        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorate


@comand_register(Command.LOGIN)
def login(username, password):
    pass


@comand_register(Command.REGISTER)
def register(username, password, nickname):
    pass


@comand_register(Command.ADD_FRIEND)
def add_friend():
    pass


@comand_register(Command.CREATE_ROOM)
def create_room():
    pass


@comand_register(Command.SEND_MESSAGE)
def send_message():
    pass


@comand_register(Command.JOIN_ROOM)
def join_room():
    pass

@comand_register(Command.BROADCASR)
def broadcast(secure_channel, request):
    secure_channel.send()


@comand_register(Command.SEND_SERVER_TIME)
def send_server_time(secure_channel, request):
    time_array = time.localtime(request)
    message = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    print('Server time：%s' % message)



''' 服务器 '''


@comand_register(Command.QUERY_SERVER_TIME)
def query_server_echo(secure_channel, request):
    ''' 发送服务器时间 '''
    secure_channel.send(Command.SEND_SERVER_TIME, int(time.time()))


@comand_register(Command.COMMAND_WRONG)
def command_wrong(secure_channel, request):
    secure_channel.send(Command.COMMAND_WRONG, None)


