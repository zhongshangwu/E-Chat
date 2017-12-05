import sys
import socket
import struct
import select
from commands import commands, Command
from secure_channel import accept_secure_channel

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ADDR = ('', 1024)
server_sock.bind(ADDR)
server_sock.listen(5)

inputs = [server_sock, sys.stdin]  # 监听socket
secure_channels = []  # 客户端安全通道
secure_channel_to_user_id = {}
user_id_to_secure_channel = {}
socket_to_secure_channel = {}

bytes_to_receive = {}  # 要接收的字节数
bytes_received = {}  # 已接收的字节数
data_buffer = {}  # 数据缓冲


user = 'Anonymous user'
room_number = 0


def _process_request(secure_channel, request):
    ''' 处理请求 '''
    command = request['command']
    func = commands[command]
    print('Command:', command)
    func(secure_channel=secure_channel, request=request['params'])


def close_client(sock):
    ''' 关闭客户端连接 '''
    pass


def off_line(secure_channel):
    ''' 客户端下线 '''
    if secure_channel in secure_channel_to_user_id:
        uid = secure_channel_to_user_id[secure_channel]
        del secure_channel_to_user_id[secure_channel]
        if uid in user_id_to_secure_channel:
            del user_id_to_secure_channel[uid]

    if secure_channel in secure_channels:
        secure_channels.remove(secure_channel)

    if secure_channel.socket in socket_to_secure_channel:
        del socket_to_secure_channel[secure_channel.socket]
    print('client[%s:%s] closed...' % secure_channel.addr)


def serve_forever():
    while True:
        infds, outfds, errfds = select.\
            select(list(map(lambda x: x.socket, secure_channels)) + inputs, [], [])
        for fds in infds:
            if fds is server_sock:  # 有新的客户端接入
                secure_channel = accept_secure_channel(fds)
                secure_channels.append(secure_channel)
                socket_to_secure_channel[secure_channel.socket] = secure_channel
                bytes_to_receive[secure_channel] = 0
                bytes_received[secure_channel] = 0
                data_buffer[secure_channel] = bytes()
                continue
            elif fds is sys.stdin:  # 终端输入
                pass
            else:
                secure_channel = socket_to_secure_channel[fds]
                if bytes_to_receive[secure_channel] == 0 and\
                        bytes_received[secure_channel] == 0:  # 一次新的接收
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

                        if secure_channel in secure_channel_to_user_id:
                            # TODO 通知好友下线
                            pass

                        # TODO 下线
                        off_line(secure_channel)
                    else:
                        data_buffer[secure_channel] = bytes()
                        bytes_to_receive[secure_channel] =\
                            struct.unpack('!L', first_4_bytes)[0] + 16 + 1

                buffer = secure_channel.socket.\
                    recv(bytes_to_receive[secure_channel] -
                         bytes_received[secure_channel])
                bytes_received[secure_channel] += len(buffer)
                data_buffer[secure_channel] += buffer
                print(data_buffer[secure_channel])
                if bytes_received[secure_channel] ==\
                        bytes_to_receive[secure_channel]\
                        and bytes_received[secure_channel] != 0:
                    # 当一个数据包接收完毕
                    try:
                        request = secure_channel.\
                            on_data(data_buffer[secure_channel])
                        _process_request(secure_channel, request)
                    except Exception:
                        # pprint(sys.exc_info())
                        # traceback.print_exc(file=sys.stdout)
                        pass
                    finally:
                        # 清空缓冲数据
                        bytes_to_receive[secure_channel] = 0
                        bytes_received[secure_channel] = 0
                        data_buffer[secure_channel] = bytes()


def login(username, password):
    ''' 登录 '''
    pass


def register(username, password, nickname):
    ''' 注册 '''
    pass


if __name__ == '__main__':
    print('Server started...')
    serve_forever()
