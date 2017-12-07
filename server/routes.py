import time
from commands import Command
from models import User, ChatRoom, Message, Friend, RoomUser
from models import Session
from server.memory import secure_channel_to_username,\
    username_to_secure_channel
from server.memory import off_line
from sqlalchemy import or_


registry = dict()

# TODO 默认所有人聊天室处理


def command_router(command=None):
    def decorate(func):
        registry[command] = func

        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorate


@command_router(Command.QUERY_SERVER_TIME)
def query_server_echo(secure_channel, request):
    ''' 查询服务器时间 '''
    secure_channel.send(Command.SEND_SERVER_TIME, int(time.time()))


@command_router(Command.REGISTER)
def register(secure_channel, request):
    ''' 注册 '''
    print(request)
    session = Session()
    exist = session.query(User).filter(User.username == request['username']).all()
    if exist:
        secure_channel.send(Command.USERNAME_EXIST, None)
    else:
        user = User(**request)
        session.add(user)
        session.commit()
        data = user.username
        secure_channel.send(Command.REGISTER_SUCCESS, data)


@command_router(Command.LOGIN)
def login(secure_channel, request):
    ''' 登录 '''
    session = Session()
    user = session.query(User).\
        filter(User.username == request['username'],
               User.password == request['password']).first()
    if not user:
        secure_channel.send(Command.LOGIN_FAILURE, None)
    else:
        data = user.username

        if user.username in username_to_secure_channel:
            sc_old = username_to_secure_channel[user.username]
            sc_old.send(Command.SERVER_KICK, None)
            sc_old.close()
            off_line(sc_old)

        secure_channel_to_username[secure_channel] = user.username
        username_to_secure_channel[user.username] = secure_channel
        secure_channel.send(Command.LOGIN_SUCCESS, data)

        # 聊天室列表
        _chat_rooms = session.query(RoomUser).\
            filter(RoomUser.username == user.username).\
            all()
        chat_rooms = [cr.roomname for cr in _chat_rooms]
        # 通知聊天室里的人他上线了
        for roomname in chat_rooms:
            members = session.query(RoomUser).\
                filter(RoomUser.roomname == roomname).all()
            for member in members:
                if member.username in username_to_secure_channel:
                    username_to_secure_channel[member.username].\
                        send(Command.ON_MEMBER_ONLINE,
                             {'roomname': roomname,
                              'membername': member.username})

        # 好友列表
        _friends = session.query(Friend).\
            filter(or_(Friend.from_user == user.username,
                       Friend.to_user == user.username),
                   Friend.accepted == True).all()
        friends = []
        for f in _friends:
            friend = None
            if f.from_user == user.username:
                friend = f.to_user
            else:
                friend = f.from_user
            friends.append(friend)
            # 通知好友他上线了
            if friend in username_to_secure_channel:
                username_to_secure_channel[friend].\
                    send(Command.ON_FRIEND_ONLINE, friend)

        # 未处理好友请求列表
        _pending_requests = session.query(Friend).\
            filter(Friend.to_user == user.username, Friend.accepted == False).\
            all()
        
        pending_requests = []
        for pr in _pending_requests:
            pending_requests.append(pr.from_user)
        
        # 聊天记录
        _messages = session.query(Message).\
            filter(Message.username == user.username).all()
        messages = []
        for message in _messages:
            messages.append({
                'username': message.username,
                'sender': message.sender,
                'send_time': message.send_time,
                'target': message.target,
                'target_type': message.target_type,
                'sent': message.sent,
                'content': message.content})
        session.query(Message).\
            filter(Message.username == user.username).update({Message.sent: True})
        
        bundle = {
            'chat_rooms': chat_rooms,
            'friends': friends,
            'pending_requests': pending_requests,
            'messages': messages
        }
        secure_channel.send(Command.LOGIN_BUNDLE, bundle)


@command_router(Command.ADD_FRIEND)
def add_friend(secure_channel, request):
    ''' 添加好友 '''
    username = secure_channel_to_username[secure_channel]
    to_username = request.strip()

    session = Session()
    from_user = session.query(User).\
        filter(User.username == username).\
        first()
    user = session.query(User).\
        filter(User.username == to_username).first()
    
    result = {
        'success': False,
        'message': ''
    }
    if not user:
        result['message'] = '用户不存在!'
        secure_channel.send(Command.ADD_FRIEND_RESULT, result)
        return
    
    if user.username == username:
        result['message'] = "无法添加自己为好友!"
        secure_channel.send(Command.ADD_FRIEND_RESULT, result)
        return

    applyed = session.query(Friend).\
        filter(Friend.from_user == username,
               Friend.to_user == user.username,
               Friend.accepted == False).count()
    if applyed:
        result['message'] = '已经申请过!'
        secure_channel.send(Command.ADD_FRIEND_RESULT, result)
        return
    
    if _is_friend(session, username, user.username):
        result['message'] = '好友已存在!'
        secure_channel.send(Command.ADD_FRIEND_RESULT, result)
        return

    requested = session.query(Friend).\
        filter(Friend.from_user == user.username,
               Friend.to_user == username,
               Friend.accepted == False).\
        first()
    if requested:
        requested.accepted = True
        session.add(requested)
        session.commit()
        contact_info = user.username
        secure_channel.send(Command.NEW_CONTACT, contact_info)
        if user.username in username_to_secure_channel:
            contact_info = from_user.username
            username_to_secure_channel[user.username].\
                send(Command.NEW_CONTACT, contact_info)
        return
    
    friend = Friend(from_user=from_user.username,
                    to_user=user.username)
    session.add(friend)
    session.commit()
    result['success'] = True
    secure_channel.send(Command.ADD_FRIEND_RESULT, result)

    if user.username in username_to_secure_channel:
        data = from_user.username
        username_to_secure_channel[user.username].\
            send(Command.INCOMMING_FRIEND_REQUEST, data)


def _is_friend(session, user_a, user_b):
    a = session.query(Friend).\
        filter(Friend.from_user == user_a,
               Friend.to_user == user_b,
               Friend.accepted == True).count()
    
    b = session.query(Friend).\
        filter(Friend.to_user == user_a,
               Friend.from_user == user_b,
               Friend.accepted == True).count()
    if a or b:
        return True
    else:
        return False


@command_router(Command.RESOLVE_FRIEND_REQUEST)
def resolve_friend_request(secure_channel, request):
    ''' 处理好友请求 '''
    to_user = secure_channel_to_username[secure_channel]
    from_user = request['username']
    accepted = request['accepted']

    session = Session()

    if _is_friend(session, from_user, to_user):
        pass
    else:
        friend = session.query(Friend).\
            filter(Friend.from_user == from_user,
                   Friend.to_user == to_user,
                   Friend.accepted == False).first()
        if accepted:
            friend.accepted = True
            session.add(friend)
            session.commit()
            secure_channel.send(Command.NEW_CONTACT, from_user)
            if from_user in username_to_secure_channel:

                username_to_secure_channel[from_user].\
                    send(Command.NEW_CONTACT, to_user)
        else:
            session.delete(friend)
            session.commit()


@command_router(Command.SEND_MESSAGE)
def send_message(secure_channel, request):
    ''' 发送消息 '''
    username = secure_channel_to_username[secure_channel]
    session = Session()
    sender = session.query(User).\
        filter(User.username == username).first()

    # 消息
    message = {
        'content': request['content'],
        'sender': sender.username,
        'target_type': request['target_type'],
        'send_time': int(time.time())
    }

    if request['target_type'] == 0:  # 私聊
        if not _is_friend(session, username, request['target']):
            secure_channel.send(Command.SEND_MESSAGE_FAILURE, '还不是好友！')
            return
        
        # 发送方回执
        message['target'] = request['target']
        secure_channel.send(Command.ON_NEW_MESSAGE, message)
        m1 = Message(username=username, target=request['target'],
                     target_type=request['target_type'],
                     sender=message['sender'],
                     content=request['content'],
                     send_time=message['send_time'], sent=True)
        session.add(m1)

        # 接收方加入聊天记录
        message['target'] = username
        sent = False
        if request['target'] in username_to_secure_channel:
            username_to_secure_channel[request['target']].\
                send(Command.ON_NEW_MESSAGE, message)
            sent = True
        m2 = Message(username=request['target'],
                     target_type=request['target_type'],
                     target=message['target'],
                     sender=message['sender'],
                     send_time=message['send_time'],
                     content=request['content'], sent=sent)
        session.add(m2)
    elif request['target_type'] == 1:  # 群聊
        message['target'] = request['target']

        if not _is_member(session, username, request['target']):
            secure_channel.send(Command.SEND_MESSAGE_FAILURE, '还没有加入聊天室')
            return
            
        members = session.query(RoomUser).\
            filter(RoomUser.roomname == request['target']).all()
        
        for member in members:
            sent = False
            if member.username in username_to_secure_channel:
                username_to_secure_channel[member.username].\
                    send(Command.ON_NEW_MESSAGE, message)
                sent = True
            
            m3 = Message(username=member.username, target=request['target'],
                         target_type=request['target_type'],
                         sender=message['sender'],
                         send_time=message['send_time'],
                         content=request['content'], sent=sent)
            session.add(m3)
    session.commit()


@command_router(Command.CREATE_ROOM)
def CREATE_ROOM(secure_channel, request):
    roomname = request['roomname'].strip()
    members = request['members']
    session = Session()
    result = {
        'success': False,
        'message': ''
    }

    room = session.query(ChatRoom).\
        filter(ChatRoom.room_name == roomname).\
        first()
    if room:
        result['message'] = '聊天室已存在！'
        secure_channel.send(Command.CREATE_ROOM_RESULTT, result)
        return
    
    room = ChatRoom(room_name=roomname)
    session.add(room)
    session.commit()

    for member_name in members:
        member = session.query(User).\
            filter(User.username == member_name).count()
        if member:
            roomuser = RoomUser(roomname=roomname, username=member_name)
            session.add(roomuser)
            session.commit()
            if member_name in username_to_secure_channel:
                username_to_secure_channel[member_name].\
                    send(Command.ON_NEW_ROOM, roomname)


@command_router(Command.JOIN_ROOM)
def join_room(secure_channel, request):
    ''' 加入聊天室 '''
    username = secure_channel_to_username[secure_channel]
    room_name = request.strip()
    result = {
        'success': False,
        'message': ''
    }
    session = Session()
    
    room = session.query(ChatRoom).\
        filter(ChatRoom.room_name == room_name).first()
    if not room:
        result['message'] = '聊天室不存在！'
        secure_channel.send(Command.JOIN_ROOM_RESULT, result)
        return
    
    roomuser = session.query(RoomUser).\
        filter(RoomUser.roomname == room_name,
               RoomUser.username == username).\
        first() 
    if roomuser:
        result['message'] = '已经在聊天室中！'
        secure_channel.send(Command.JOIN_ROOM_RESULT, result)
        return

    roomuser = RoomUser(roomname=room_name, username=username)
    session.add(roomuser)
    session.commit()
    secure_channel.send(Command.ON_NEW_ROOM, room_name)


# @command_router(Command.PUSH_TO_ROOM)
# def push_to_room(secure_channel, request):
#     ''' 添加用户到聊天室 '''
#     username = secure_channel_to_username[secure_channel]
#     room_name = request.strip()
#     result = {
#         'success': False,
#         'message': ''
#     }
#     session = Session()

#     room = session.query(ChatRoom).\
#         filter(ChatRoom.room_name == room_name).first()
#     if not room:
#         result['message'] = '聊天室不存在！'
#         secure_channel.send(Command.JOIN_ROOM_RESULT, result)
#         return

#     roomuser = session.query(RoomUser).\
#         filter(RoomUser.roomname == room_name,
#                RoomUser.username == username).\
#         first()
#     if roomuser:
#         result['message'] = '已经在聊天室中！'
#         secure_channel.send(Command.JOIN_ROOM_RESULT, result)
#         return

#     roomuser = RoomUser(roomname=room_name, username=username)
#     session.add(roomuser)
#     session.commit()
#     secure_channel.send(Command.ON_NEW_ROOM, room_name)


def _is_member(session, username, roomname):
    ''' 是否加入聊天室 '''
    exist = session.query(RoomUser).\
        filter(RoomUser.roomname == roomname,
               RoomUser.username == username).count()
    if exist:
        return True
    else:
        return False


@command_router(Command.COMMAND_WRONG)
def command_wrong(secure_channel, request):
    secure_channel.send(Command.COMMAND_WRONG, None)
