import sqlite3
from collections import namedtuple

conn = sqlite3.connect('sqlite.db')

User = namedtuple('User', 'id name password created_at')
ChatRoom = namedtuple('ChatRoom', 'id name encrypted password created_at')
RoomUser = namedtuple('RoomUser', 'id user_id room_id')
Message = namedtuple('Message', 'id content read user_id created_at')
Friend = namedtuple('Friend', 'id from_user_id to_user_id accepted created_at')

CREATE_USER_TABLE_SQL = """NONE"""
CREATE_CHATROOM_TABLE_SQL = """NONE"""
CREATE_ROOMUSER_TABLE_SQL = """NONE"""
CREATE_MESSAGE_TABLE_SQL = """NONE"""
CREATE_FRIEND_TABLE_SQL = """NONE"""

CREATE_DATABASE = {
    'users': CREATE_USER_TABLE_SQL,
    'chat_rooms': CREATE_CHATROOM_TABLE_SQL,
    'room_users': CREATE_ROOMUSER_TABLE_SQL,
    'messages': CREATE_MESSAGE_TABLE_SQL,
    'friends': CREATE_FRIEND_TABLE_SQL
}


def create_database():
    c = conn.cursor()
    for table_name in CREATE_DATABASE.keys():
        try:
            c.execute(CREATE_DATABASE[table_name])
        except Exception:
            print('table: [%s] already exist, passed!' % table_name)


def get_user(user_id):
    ''' 获取用户信息 '''
    c = conn.cursor()
    row = c.execute('SELECT ' + ','.join(User._fields) +
                    ' FROM users WHERE id=?', [user_id]).fetchall()
    if len(row) == 0:
        return None
    else:
        user = User(*row[0])
        user['online'] = user_id in user_id_to_sc
        return user
    
