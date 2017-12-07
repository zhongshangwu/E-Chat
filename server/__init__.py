import sys
import socket
import struct
import select
from pprint import pprint
import traceback
from server.routes import registry
from secure_channel import accept_secure_channel
from server.memory import secure_channels, secure_channel_to_username,\
    username_to_secure_channel, socket_to_secure_channel
from server.memory import off_line


class Server:

    def __init__(self, *args, **kwargs):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.addr = ('localhost', 1024)
        self.server.bind(self.addr)
        self.server.listen(5)
        self.inputs = [self.server, sys.stdin]
        self.bytes_to_receive = {}
        self.bytes_received = {}
        self.data_buffer = {}
    
    def _process_request(self, secure_channel, request):
        command = request['command']
        func = registry[command]
        print('Command:', command)
        func(secure_channel=secure_channel, request=request['params'])

    def serve_forever(self):
        while True:
            infds, outfds, errfds = select.\
                select(list(map(lambda x: x.socket, secure_channels))
                       + self.inputs, [], [])
            for fds in infds:
                if fds is self.server:  # 有新的客户端接入
                    sc = accept_secure_channel(fds)
                    secure_channels.append(sc)
                    socket_to_secure_channel[sc.socket] =\
                        sc
                    self.bytes_to_receive[sc] = 0
                    self.bytes_received[sc] = 0
                    self.data_buffer[sc] = bytes()
                    continue
                elif fds is sys.stdin:  # 终端输入
                    pass
                else:
                    sc = socket_to_secure_channel[fds]
                    if self.bytes_to_receive[sc] == 0 and\
                            self.bytes_received[sc] == 0:  # 一次新的接收
                        conn_ok = True
                        first_4_bytes = ''
                        try:
                            first_4_bytes = sc.socket.recv(4)
                        except ConnectionError as e:
                            conn_ok = False

                        if first_4_bytes == '' or len(first_4_bytes) < 4:
                            conn_ok = False

                        if not conn_ok:  # 连接异常
                            sc.close()  # 关闭通道

                            if sc in secure_channel_to_username:
                                # TODO 通知好友下线
                                pass

                            # TODO 下线
                            off_line(sc)
                        else:
                            self.data_buffer[sc] = bytes()
                            self.bytes_to_receive[sc] =\
                                struct.unpack('!L', first_4_bytes)[0] + 16 + 1

                    buffer = sc.socket.\
                        recv(self.bytes_to_receive[sc] -
                             self.bytes_received[sc])
                    self.bytes_received[sc] += len(buffer)
                    self.data_buffer[sc] += buffer
                    if self.bytes_received[sc] ==\
                            self.bytes_to_receive[sc]\
                            and self.bytes_received[sc] != 0:
                        # 当一个数据包接收完毕
                        try:
                            request = sc.\
                                on_data(self.data_buffer[sc])
                            self._process_request(sc, request)
                        except Exception:
                            pprint(sys.exc_info())
                            traceback.print_exc(file=sys.stdout)
                            pass
                        finally:
                            # 清空缓冲数据
                            self.bytes_to_receive[sc] = 0
                            self.bytes_received[sc] = 0
                            self.data_buffer[sc] = bytes()

