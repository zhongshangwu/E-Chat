import sys
import struct
import select
import traceback
from pprint import pprint
from secure_channel import establish_secure_channel
from client.modes import modes
from client.modes.base import Mode


class Client:

    def __init__(self, mode=Mode.COMMAND, *args, **kwargs):
        self.mode = mode
        self.chat_room = 'default'
        self.chat_rooms = []
        self.friends = []
        self.pending_requests = []
        self.unread_messages = {0: {}, 1: {}}
        self.chat_history = {0: {}, 1: {}}
        self.secure_channel = establish_secure_channel()
        self.inputs = [sys.stdin, self.secure_channel.socket]
        self.closed = False
        self.bytes_to_receive = 0
        self.bytes_received = 0
        self.data_buffer = bytes()
        self.handler = modes[self.mode](self)

    def run(self):
        while not self.closed:
            infds, outfds, errfds = select.select(self.inputs, [], [])
            for fds in infds:
                if fds == self.secure_channel.socket:
                    if self.bytes_to_receive == 0 and\
                            self.bytes_received == 0:  # 一次新的接收
                        conn_ok = True
                        first_4_bytes = ''
                        try:
                            first_4_bytes = self.secure_channel.socket.recv(4)
                        except ConnectionError as e:
                            conn_ok = False

                        if first_4_bytes == '' or len(first_4_bytes) < 4:
                            conn_ok = False

                        if not conn_ok:  # 连接异常
                            self.secure_channel.close()  # 关闭通道
                        else:
                            self.data_buffer = bytes()
                            self.bytes_to_receive = struct.unpack(
                                '!L', first_4_bytes)[0] + 16 + 1
                    else:
                        # 接收数据、拼成块
                        buffer = self.secure_channel.socket.\
                            recv(self.bytes_to_receive - self.bytes_received)
                        self.data_buffer += buffer
                        self.bytes_received += len(buffer)

                    if self.bytes_received == self.bytes_to_receive:
                        # 当一个数据包接收完毕
                        self.bytes_to_receive = 0
                        self.bytes_received = 0

                        try:
                            request = self.secure_channel.\
                                on_data(self.data_buffer)
                            self.handler.process_request(request)
                        except Exception:
                            pprint(sys.exc_info())
                            traceback.print_exc(file=sys.stdout)
                else:
                    str_input = fds.readline()
                    self.handler.process_statement(str_input.strip('\n'))


if __name__ == '__main__':
    client = Client(mode=Mode.COMMAND)
    client.run()
