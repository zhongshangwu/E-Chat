import enum


class Command(enum.IntEnum):
    ''' 命令类型 '''

    QUERY_SERVER_TIME = 1  # None
    REGISTER = 2  # {username:str;password:str}
    LOGIN = 3  # {username:str;password:str}
    ADD_FRIEND = 4  # username:str
    RESOLVE_FRIEND_REQUEST = 5  # {agree:boolean,user_id:int}
    SEND_MESSAGE = 6  # {target_id:int,target_type:int,content:str}
    JOIN_ROOM = 7  # roomname:str
    JOIN_ROOM_RESULT = 8
    CREATE_ROOM = 9  # {roomname:str,users:list}
    CREATE_ROOM_RESULTT = 10

    SEND_SERVER_TIME = 101  # server_time:int
    REGISTER_SUCCESS = 102  # username:str
    LOGIN_SUCCESS = 103  # username:str
    SERVER_KICK = 104  # None
    LOGIN_BUNDLE = 105  # {chat_rooms:list;friends:list,pending_requests:list}
    ADD_FRIEND_RESULT = 106  # {success:boolean;message:str}
    INCOMMING_FRIEND_REQUEST = 107  # username:str
    NEW_CONTACT = 108  # username:str
    ON_NEW_MESSAGE = 109  # message:obj
    ON_NEW_ROOM = 110  # roomname:str
    ON_FRIEND_ONLINE = 111  # username:str
    ON_FRIEND_OFFLINE = 112  # username:str
    ON_MEMBER_ONLINE = 113  # {roomname:str,membername:str}
    ON_MEMBER_OFFLINE = 114  # {roomname:str,membername:str}

    USERNAME_EXIST = 201  # None
    LOGIN_FAILURE = 202  # None
    SEND_MESSAGE_FAILURE = 203  # str

    # LOGIN = 1  # [username, password]
    # REGISTER = 2  # [username, password]
    # ADD_FRIEND = 3  # username:str
    # SOLVE_FRIEND_REQUEST = 4
    # JOIN_ROOM = 5  # id:int
    # CREATE_ROOM = 6  # name: str
    # query_room_users = 7  # id:int
    # QUERY_SERVER_TIME = 8

    # # {target_type:int(0=私聊 1=群聊),target_id:int,message:str}
    # SEND_MESSAGE = 100

    # LOGIN_SUCCESSFUL = 101
    # REGISTER_SUCCESSFUL = 102
    # INCOMING_FRIEND_REQUEST = 103
    # CONTACT_INFO = 104
    # CHAT_HISTORY = 105
    # SEND_SERVER_TIME = 106
    # ADD_FRIEND_REQUEST = 107
    # ON_FRIEND_OFF_LINE = 108
    # SHOW_CHAT_HISTORY = 109
    # ON_NEW_MESSAGE = 110
    # SERVER_KICK = 111
    # SHOW_ROOM_USERS = 112
    # ON_ROOM_USER_OFF_LINE = 113
    # LOGIN_BUNDLE = 114
    # LOGIN_FAILURE = 115
    # USERNAME_TOKEN = 116
    # FAILURE = 117
    # MSG = 118
    # BROADCASR = 119

    COMMAND_WRONG = 201  # None


_commands = set([c for c in Command.__members__.values()])


def get_command_from_value(value):
    if value not in _commands:
        return Command(201)
    return Command(value)


# @comand_register(Command.LOGIN)
# def login(username, password):
#     pass


# @comand_register(Command.REGISTER)
# def register(username, password):
#     pass


# @comand_register(Command.ADD_FRIEND)
# def add_friend():
#     pass


# @comand_register(Command.CREATE_ROOM)
# def create_room():
#     pass


# @comand_register(Command.SEND_MESSAGE)
# def send_message():
#     pass


# @comand_register(Command.JOIN_ROOM)
# def join_room():
#     pass

# @comand_register(Command.BROADCASR)
# def broadcast(secure_channel, request):
#     secure_channel.send()


# @comand_register(Command.SEND_SERVER_TIME)
# def send_server_time(secure_channel, request):
#     time_array = time.localtime(request)
#     message = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
#     print('Server time：%s' % message)

# ''' 服务器 '''

