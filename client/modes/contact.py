import re
from client.modes.base import BaseHandler
from client.modes.chat import ChatHandler
from client.modes.base import Mode
from commands import Command


class ContactHandler(BaseHandler):

    def _print_prefix(self):
        print("contact> ", end='', flush=True)
    
    def _print_help(self):
        ''' 打印帮助 '''
        print("Contact Mode Commands:")
        print("-   +<username> : 添加好友")
        print("-   :r : 所有聊天室")
        print("-   :f : 所有好友")
        print("-   :pr : 所有待处理好友请求")
        print("-   :m : 所有未读消息")
        print("-   @r <group> \"<message>\": 发送消息给聊天室")
        print("-   @f <username> \"<message>\": 发送消息给好友")
        print("-   &r <group>  : 进入群聊模式")
        print("-   &f <username>  : 进入私聊模式")
        print("-   ? : 查看未读消息统计")
        print("-   <group>=<user1>+<user2>+... : 创建聊天室")
        print("-   <group>+=<user> : 添加用户到现有的聊天室")
        print("-   find <keyword> : 查找用户")
        print("-   help : 帮助")
        self._print_prefix()

    def _hook_statement(self, statement):
        if statement == ':r':
            print("ChatRooms:")
            for idx, r in enumerate(self.client.chat_rooms):
                print(' <%d> %s' % (idx, r))
            self._print_prefix()
        elif statement == ':f':
            print('Friends:')
            for idx, f in enumerate(self.client.friends):
                print(' <%d> %s' % (idx, f))
            self._print_prefix()
        elif statement == ':m':
            print(self.client.chat_history)
            self._print_prefix()
        elif statement == ':pr':
            print('待处理好友请求:')
            for idx, pr in enumerate(self.client.pending_requests):
                print(' <%d> %s' % (idx, pr))
            self._print_prefix()
        elif statement.startswith('+'):
            parts = statement.split(None, 1)
            if len(parts) < 2:
                print('试图解析命令出错：\n +<f/r> <username/group> \"<message>\"')
                self._print_prefix()
                return
            if parts[0] == '+f':
                username = parts[1]
                self.client.secure_channel.send(Command.ADD_FRIEND, username)
            elif parts[0] == '+r':
                roomname = parts[1]
                self.client.secure_channel.send(Command.JOIN_ROOM, roomname)
            else:
                print('添加好友或者加入聊天室失败：\n +<f/r> <username/group>')
                self._print_prefix()
                return
        elif statement.startswith('@'):  # 发送消息
            parts = statement.split(None, 2)
            if len(parts) < 3:
                print('试图解析命令出错：\n @<f/r> <username/group> \"<message>\"')
                self._print_prefix()
                return
            if parts[0] == '@f':
                target_type = 0
            elif parts[0] == '@r':
                target_type = 1
            else:
                print('试图解析命令出错：\n @<f/r> <username/group> \"<message>\"')
                self._print_prefix()
                return
            data = {
                'target_type': target_type,
                'target': parts[1],
                'content': parts[2]
            }
            self.client.secure_channel.send(Command.SEND_MESSAGE, data)
        elif statement.startswith('?'):  # 查看未读消息
            if self.client.unread_messages[0]:
                for target, value in self.client.unread_messages[0].items():
                    if value['count']:
                        print('[用户:%s]----%d' % (target, value['count']))
            if self.client.unread_messages[1]:
                for target, value in self.client.unread_messages[1].items():
                    if value['count']:
                        print('[聊天室:%s]----%d' % (target, value['count']))
            self._print_prefix()
        elif statement.startswith('&'):  # 进入聊天模式
            parts = statement.split(None, 1)
            if len(parts) < 2:
                print('进入聊天模式失败：\n &<f/r> <username/group>')
                self._print_prefix()
                return
            if parts[0] == '&f':
                target_type = 0
            elif parts[0] == '&r':
                target_type = 1
            else:
                print('进入聊天模式失败：\n &<f/r> <username/group>')
                self._print_prefix()
                return
            target = parts[1]
            if target_type == 0:
                if target not in self.client.friends:
                    print('好友不存在！')
                    self._print_prefix()
                    return
            elif target_type == 1:
                if target not in self.client.chat_rooms:
                    print('聊天室不存在！')
                    self._print_prefix()
                    return
            self.client.mode = Mode.CHAT
            self.client.handler = ChatHandler(self.client, target_type, target)
        elif re.match('[a-zA-Z0-9_]+=.*', statement):
            parts = statement.split("=")
            if len(parts) > 2:
                print("创建聊天室失败：\n <roomname>=<member1>+<member2>...")
                self._print_prefix()
                return
            data = {}
            data['roomname'] = parts[0]
            data['members'] = [self.client.user]
            members = parts[1].split('+')
            data["members"].extend(members)
            if len(data['members']) < 2:
                print('创建聊天室失败：\n <roomname>=<member1>+<member2>...')
                self._print_prefix()
                return
            self.client.secure_channel.send(Command.CREATE_ROOM, data)
        # elif re.match('[a-zA-Z0-9_]+\+=.*', statement):
        #     req["do"] = 'addgroup'
        #     parts = statement.split("+=")
        #     if len(parts) > 2:
        #         print >> sys.stderr, "Badly formed group-add statement\n<group>+=<user>+<user>..."
        #         return None
        #     req["name"] = parts[0]
        #     req["member"] = parts[1]
        #     return req
        else:
            self._wrong_command()

    def _hook_request(self, command, request):
        if command == Command.ADD_FRIEND_RESULT:
            if request['success']:
                print('好友请求已发送!')
                self._print_prefix()
            else:
                print(request['message'])
                self._print_prefix()
        if command == Command.INCOMMING_FRIEND_REQUEST:
            self.handle_pending_request(request)
        if command == Command.NEW_CONTACT:
            print('新的好友：%s' % request)
            self.client.friends.append(request)
            if request in self.client.pending_requests:
                self.client.pending_requests.remove(request)
            self._print_prefix()
        if command == Command.ON_NEW_MESSAGE:
            print('你有一条新的消息！')
            self._print_prefix()
        if command == Command.SEND_MESSAGE_FAILURE:
            print(request)
            self._print_prefix()
        if command == Command.JOIN_ROOM_RESULT:
            print(request['message'])
            self._print_prefix()
        if command == Command.ON_NEW_ROOM:
            print('加入聊天室：[%s]' % request)
            self._print_prefix()
        if command == Command.ON_FRIEND_ONLINE:
            print('你的好友：【%s】上线了！' % request)
            self._print_prefix()

    def handle_pending_request(self, request):
        accepted = input('用户%s：请求添加你为好友(Y/N)！' % request)
        if accepted.upper() == 'Y':
            data = {
                'accepted': True,
                'username': request
            }
            self.client.secure_channel.\
                send(Command.RESOLVE_FRIEND_REQUEST, data)
        elif accepted.upper() == 'N':
            data = {
                'accepted': False,
                'username': request
            }
            self.client.secure_channel.\
                send(Command.RESOLVE_FRIEND_REQUEST, data)
        self._print_prefix()


    
