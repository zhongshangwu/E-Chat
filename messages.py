from binascii import unhexlify
from hashlib import md5 as _md5
from struct import pack, unpack
from commands import get_command_from_value


''' 消息的序列化与反序列化 '''

MESSAGE_TYPE = {
    1: 'int',
    2: 'float',
    3: 'str',
    4: 'list',
    5: 'dict',
    6: 'bool',
    7: 'bytearray',
}

MESSAGE_TYPE_INVERSE = {
    'int': 1,
    'float': 2,
    'str': 3,
    'list': 4,
    'dict': 5,
    'bool': 6,
    'bytearray': 7
}


def _serialize_int(value):
    body = long_to_bytes(value)
    return bytes([MESSAGE_TYPE_INVERSE['int']]) +\
        pack('!L', len(body)) + body


def _serialize_bool(value):
    return bytes([MESSAGE_TYPE_INVERSE['bool']]) +\
        pack('!L', 1) + bytes([1 if value else 0])


def _serialize_float(float):
    body = pack('f', float)
    return bytes([MESSAGE_TYPE_INVERSE['float']]) +\
        pack('!L', len(body)) + body


def _serialize_str(str):
    body = str.encode()
    return bytes([MESSAGE_TYPE_INVERSE['str']]) +\
        pack('!L', len(body)) + body


def _serialize_bytes(body):
    return bytes([MESSAGE_TYPE_INVERSE['bytearray']]) +\
        pack('!L', len(body)) + body


def _serialize_list(list):
    '''
    |--Body (self-evident length)--|--Body (self-evident length)--|--Body (self-evident length)--|...
    '''
    body = bytearray()
    for i in range(0, len(list)):
        body += _serialize_any(list[i])
    return bytes([MESSAGE_TYPE_INVERSE['list']]) + pack('!L', len(body)) + body


def _serialize_dict(dict):
    '''
    |--Length of Key(1Byte)--|--Key--|--Body (self-evident length)--|
    |--Length of Key(1Byte)--|--Key--|--Body (self-evident length)--|
    '''
    body = bytearray()

    for item_key, value in dict.items():
        item_body = _serialize_any(value)
        key_length = len(item_key)

        body += bytes([key_length])
        body += str.encode(item_key)
        body += item_body

    return bytes([MESSAGE_TYPE_INVERSE['dict']]) + pack('!L', len(body)) + body


_serialize_by_type = [None, _serialize_int, _serialize_float, _serialize_str,
                      _serialize_list, _serialize_dict,
                      _serialize_bool, _serialize_bytes]


def _serialize_any(obj):
    if obj is None:
        return bytearray([0])
    type_byte = MESSAGE_TYPE_INVERSE[type(obj).__name__]
    return _serialize_by_type[type_byte](obj)


def serialize_message(command_type, parameters):
    result = bytes([command_type.value])
    result += _serialize_any(parameters)
    return result


def _deserialize_int(value):
    return int.from_bytes(value, 'big')


def _deserialize_bool(value):
    return True if value[0] else False


def _deserialize_float(bytes):
    return unpack('!f', bytes)[0]


def _deserialize_str(bytes):
    return bytes.decode()


def _deserialize_bytes(body):
    return bytearray(body)


def _deserialize_list(bytes):
    '''
    |--Body (self-evident length)--|--Body (self-evident length)--|--Body (self-evident length)--|...
    '''
    byte_reader = ByteArrayReader(bytes)
    ret = []
    while (not byte_reader.empty()):
        body_type = byte_reader.read(1)[0]
        body = byte_reader.read(int.from_bytes(
            byte_reader.read(4), byteorder='big'))
        body = _deserialize_by_type[body_type](body)
        ret.append(body)
    return ret


def _deserialize_dict(bytes):
    '''
    |--Length of Key(1Byte)--|--Key--|--Body (self-evident length)--|
    |--Length of Key(1Byte)--|--Key--|--Body (self-evident length)--|
    '''
    byte_reader = ByteArrayReader(bytes)
    ret = {}
    while (not byte_reader.empty()):
        len_key = byte_reader.read(1)
        key = byte_reader.read(len_key[0])

        body_type = byte_reader.read(1)[0]
        body = byte_reader.read(int.from_bytes(
            byte_reader.read(4), byteorder='big'))
        body = _deserialize_by_type[body_type](body)
        ret[key.decode()] = body
    return ret


_deserialize_by_type = [None, _deserialize_int, _deserialize_float,
                        _deserialize_str, _deserialize_list,
                        _deserialize_dict, _deserialize_bool,
                        _deserialize_bytes]


def _deserialize_any(bytes):
    byte_reader = ByteArrayReader(bytes)
    type = byte_reader.read(1)[0]

    if type == 0:
        return None

    body_len = int.from_bytes(byte_reader.read(4), 'big')
    return _deserialize_by_type[type](byte_reader.read(body_len))


def deserialize_message(data):
    payload = {}
    byte_reader = ByteArrayReader(data)
    payload['command'] = get_command_from_value(byte_reader.read(1)[0])

    payload['params'] = _deserialize_any(byte_reader.read_to_end())

    return payload


def long_to_bytes(val, endianness='big'):
    """
    Use :ref:`string formatting` and :func:`~binascii.unhexlify` to
    convert ``val``, a :func:`long`, to a byte :func:`str`.

    :param long val: The value to pack

    :param str endianness: The endianness of the result. ``'big'`` for
      big-endian, ``'little'`` for little-endian.

    If you want byte- and word-ordering to differ, you're on your own.

    Using :ref:`string formatting` lets us use Python's C innards.
    """

    # one (1) hex digit per four (4) bits
    width = val.bit_length()
    # unhexlify wants an even multiple of eight (8) bits, but we don't
    # want more digits than we need (hence the ternary-ish 'or')
    width += 8 - ((width % 8) or 8)

    # format width specifier: four (4) bits per hex digit
    fmt = '%%0%dx' % (width // 4)

    # prepend zero (0) to the width, to zero-pad the output

    # if fmt % val == '0':
    #     s = unhexlify('00')
    # else:
    #     s = unhexlify(fmt % val)

    s = b'\x00' if fmt % val == '0' else unhexlify(fmt % val)

    if endianness == 'little':
        # see http://stackoverflow.com/a/931095/309233
        s = s[::-1]
    return s


def md5(text):
    m = _md5()
    m.update(text.encode('utf-8'))
    return m.hexdigest()


class ByteArrayReader:
    def __init__(self, byte_array):
        self.byte_array = byte_array
        self.pointer = 0

    def read(self, length):
        buffer = self.byte_array[self.pointer: self.pointer + length]
        self.pointer += length
        return buffer

    def read_to_end(self):
        buffer = self.byte_array[self.pointer: len(self.byte_array)]
        self.pointer = len(self.byte_array)
        return buffer

    def empty(self):
        return len(self.byte_array) == self.pointer


if __name__ == '__main__':
    from commands import Command
    s = serialize_message(Command.LOGIN, 100000000000000000000)
    a = deserialize_message(s)
    print(a)



