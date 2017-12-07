

secure_channels = []  # 客户端安全通道
secure_channel_to_username = {}
username_to_secure_channel = {}
socket_to_secure_channel = {}


def off_line(secure_channel):
    ''' 客户端下线 '''
    if secure_channel in secure_channel_to_username:
        uid = secure_channel_to_username[secure_channel]
        del secure_channel_to_username[secure_channel]
        if uid in username_to_secure_channel:
            del username_to_secure_channel[uid]

    if secure_channel in secure_channels:
        secure_channels.remove(secure_channel)

    if secure_channel.socket in socket_to_secure_channel:
        del socket_to_secure_channel[secure_channel.socket]
    print('client[%s:%s] closed...' % secure_channel.addr)
