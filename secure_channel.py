import os
import math
import struct
import socket

import hashlib
from Crypto.Cipher import AES

from messages import serialize_message, deserialize_message
from messages import ByteArrayReader, long_to_bytes


class SecureChannel:
    '''
    数据格式：
    |--Length of Message Body(4Bytes)--|--Length of AES padding (1Byte)--|--AES IV (16Bytes)--|--Message Body (CSON)--|
    '''
    def __init__(self, socket, addr, shared_secret):
        socket.setblocking(0)
        self.socket = socket
        self.addr = addr
        self.shared_secret = shared_secret

    def send(self, message_type, parameters=None):
        iv = bytes(os.urandom(16))

        # 明文消息
        plain_data = serialize_message(message_type, parameters)
        length_of_plain = len(plain_data)

        # AES分组对齐
        padding_count = math.\
            ceil(length_of_plain / 16) * 16 - length_of_plain
        
        for i in range(0, padding_count):
            plain_data += b'\0'

        # AES加密
        cryptor = AES.new(self.shared_secret, AES.MODE_CBC, iv)
        # 暗文
        cipher_data = cryptor.encrypt(plain_data)
        length_of_cipher = len(cipher_data)

        # 包装
        self.socket.send(
            struct.pack('!L', length_of_cipher) +
            bytes([padding_count]) + iv + cipher_data)
        return None

    def on_data(self, data_array):
        # 用select循环socket.recv，当收到一个完整的数据块后（收到后length_of_encrypted_message+1+16个字节后），
        br = ByteArrayReader(data_array)

        padding_count = br.read(1)[0]

        iv = br.read(16)

        data = br.read_to_end()

        cryptor = AES.new(self.shared_secret, AES.MODE_CBC, iv)
        plain_data = cryptor.decrypt(data)

        if padding_count != 0:
            plain_data = plain_data[0:-padding_count]

        return deserialize_message(plain_data)

    def close(self):
        self.socket.close()


# 迪菲-赫尔曼密钥交换算法
# base = config['security']['base']  # 2 or 5
# prime = config['security']['prime']  # enough big
base = 5
prime = 23
server_private_secret = 6
client_private_secret = 15


def _get_share_secret(my_private_secret, their_secret):
    return hashlib.sha256(
        long_to_bytes(their_secret ** my_private_secret % prime)).digest()


def _get_client_secret():
    return base ** client_private_secret % prime


def _get_server_secret():
    return base ** server_private_secret % prime


def establish_secure_channel():
    ''' 客户端发起连接，并创建安全通道 '''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect(('', 1024))

    # 首次连接，用diffle hellman交换密钥
    s.send(long_to_bytes(_get_client_secret()))

    # 首次连接，收到服务器diffle hellman交换密钥
    data = s.recv(1024)
    their_secret = int.from_bytes(data, byteorder='big')

    # 计算出共同密钥
    shared_secret = _get_share_secret(client_private_secret, their_secret)

    sc = SecureChannel(s, ('', 1024), shared_secret)
    
    return sc


def accept_secure_channel(socket):
    ''' 服务器接收一个连接，并创建安全通道 '''
    conn, addr = socket.accept()

    # 首次连接，客户端会发送diffle hellman密钥
    data = conn.recv(1024)
    their_secret = int.from_bytes(data, byteorder='big')

    # 把服务器的diffle hellman密钥发送给客户端
    conn.send(long_to_bytes(_get_server_secret()))

    # 计算出共同密钥
    shared_secert = _get_share_secret(server_private_secret, their_secret)
    sc = SecureChannel(conn, addr, shared_secert)
    print("connected from[%s:%s]" % addr)
    return sc


if __name__ == '__main__':
    A = _get_client_secret()
    B = _get_server_secret()

    K1 = _get_share_secret(server_private_secret, A)
    K2 = _get_share_secret(client_private_secret, B)
    print(K1, len(K1))
    print(K2, len(K2))
