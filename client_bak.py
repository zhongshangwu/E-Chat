import enum
import sys
import struct
import select
import traceback
from pprint import pprint
from secure_channel import establish_secure_channel
from commands import Command
from commands import commands


class Mode(enum.IntEnum):
    ''' 模式 '''

    CHAT = 1
    COMMAND = 2
    GAME = 3
    MUSIC = 4
    QUERY = 5


# SERVER_ADDR = ('', 1024)

# client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client_sock.connect(SERVER_ADDR)

secure_channel = establish_secure_channel()

inputs = [sys.stdin, secure_channel.socket]

current_mode = Mode.COMMAND  # 输入模式、命令模式
current_output = 'command> '
current_chat_room = 'default'  # 当期聊天室

bytes_to_receive = 0
bytes_received = 0
data_buffer = bytes()

CLOSED = False


def socket_listener():
    ''' 监听socket连接 '''
    pass


def _process_request(secure_channel, request):
    ''' 处理请求 '''
    command = request['command']
    func = commands[command]
    print('Command:', command)
    func(secure_channel=secure_channel, request=request['params'])


def loop_forever():
    print('Connected to remote host. Start sending messages...\ncommand> ', end='')
    global bytes_to_receive
    global bytes_received
    global data_buffer
    while not CLOSED:
        infds, outfds, errfds = select.select(inputs, [], [])
        for fds in infds:
            if fds == secure_channel.socket:
                if bytes_to_receive == 0 and\
                        bytes_received == 0:  # 一次新的接收
                    conn_ok = True
                    first_4_bytes = ''
                    try:
                        first_4_bytes = secure_channel.socket.recv(4)
                    except ConnectionError as e:
                        conn_ok = False

                    if first_4_bytes == '' or len(first_4_bytes) < 4:
                        conn_ok = False

                    if not conn_ok:  # 连接异常
                        secure_channel.close()  # 关闭通道
                    else:
                        data_buffer = bytes()
                        bytes_to_receive = struct.unpack(
                            '!L', first_4_bytes)[0] + 16 + 1
                else:
                    # 接收数据、拼成块
                    buffer = secure_channel.socket.\
                        recv(bytes_to_receive - bytes_received)
                    data_buffer += buffer
                    bytes_received += len(buffer)
                
                if bytes_received == bytes_to_receive:
                    # 当一个数据包接收完毕
                    bytes_to_receive = 0
                    bytes_received = 0

                    try:
                        request = secure_channel.on_data(data_buffer)
                        _process_request(secure_channel, request)
                        # print('\nReceived:', data, '\n%s' % current_output, end='')
                    except Exception:
                        pprint(sys.exc_info())
                        traceback.print_exc(file=sys.stdout)
            else:
                str_input = fds.readline()
                process_input(str_input.strip('\n'))
                # secure_channel.send(Command.SERVER_ECHO, command)


def process_input(str_input):
    ''' 处理用户输入 '''
    if current_mode == Mode.COMMAND:  # 命令模式
        if str_input == 'quit':
            quit()
        elif str_input == 'help':
            help()
        elif str_input == 'query':
            query_mode()
        elif str_input == 'chat':
            chat_mode()
        elif str_input == 'server time':
            query_server_time()
        else:
            unkown()
        # input_slice=str_input.split(':', 1)
        # if not input_slice or len(input_slice) < 2:
        #     pass      
    elif current_mode == Mode.CHAT:  # 聊天模式
        pass
    elif current_mode == Mode.QUERY:  # 查询模式
        if str_input == 'server time':
            query_server_time()



def quit():
    ''' 退出 '''
    global CLOSED
    CLOSED = True


def help():
    ''' 帮助 '''
    print("Chat client commads and syntax:")
    print("-   @<user/group> \"<message>\" : Send message to user or group")
    print("-   ? : Get number of unread messages")
    print("-   read : Read all unread messages")
    print("-   +<user> \"<keyword>\" : Add mapping to contacts list")
    print("-   <group>=<user1>+<user2>+... : Create multicast group")
    print("-   <group>+=<user> : Add user to existing group")
    print("-   find <keyword> : Find contact using keyword")
    print("-   help : Print(this help message")
    print("-   quit : Quit from chat")
    _print_prefix()


def unkown():
    ''' 错误输入 '''
    print('Type "help" for more information.')
    _print_prefix()


def query_mode():
    ''' 查询模式 '''
    global current_mode
    current_mode = Mode.QUERY
    _print_prefix()


def chat_mode():
    ''' 聊天模式 '''
    global current_mode
    current_mode = Mode.CHAT
    _print_prefix()


def query_server_time():
    ''' 服务器输出 '''
    secure_channel.send(Command.QUERY_SERVER_TIME, None)


def _print_prefix():
    if current_mode == Mode.COMMAND:
        print('command> ', end='', flush=True)
    elif current_mode == Mode.CHAT:
        print('[%s]> ' % current_chat_room, end='', flush=True)
    elif current_mode == Mode.QUERY:
        print('query> ', end='', flush=True)


def process_request(request):
    ''' 处理服务器请求 '''
    pass


def receive():
    import time
    while True:
        time.sleep(3)
        print("server info:.....")
        print('chat> ', end='')


if __name__ == '__main__':
    loop_forever()
    # import threading
    # thread = threading.Thread(target=receive)
    # thread.start()
    # while True:
    #     # command = input('chat> ')
    #     infds, outfds, errfds = select.select([sys.stdin], [], [])
    #     for fds in infds:
    #         command = fds.readline()
            # print('chat> ', end='s')
            # if fds.readline():
            #     print('chat> ', end='')
            
    # while True:
    #     data = input('chat> ')
    #     if not data:
    #         continue
    #     else:
    #         print("data:", data)


