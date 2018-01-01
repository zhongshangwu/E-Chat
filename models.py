from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy import func, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
# engine = create_engine('sqlite:///database.db', echo=True)
engine = create_engine(
    'mysql+pymysql://root:iPhone520@rm-2ze4u71p01tjv03741o.mysql.rds.aliyuncs.com:3306/echat?charset=utf8', echo=True)
Session = sessionmaker(bind=engine)


class Friend(Base):
    ''' 好友 '''
    __tablename__ = 'freinds'

    from_user = Column('from_user', String(20), primary_key=True)
    to_user = Column('to_user', String(20), primary_key=True)
    created_at = Column(DateTime, default=func.now())
    accepted = Column('accepted', Boolean, default=False)


class User(Base):
    ''' 用户 '''
    __tablename__ = 'users'
    created_at = Column('created_at', DateTime(timezone=False),
                        nullable=False, default=func.now())

    # id = Column('id', Integer, primary_key=True)
    username = Column('username', String(20), primary_key=True)
    password = Column('password', String(100), nullable=False)

    def __repr__(self):
        return "<User(username='%s')>" % self.username


class Message(Base):
    ''' 消息 '''
    __tablename__ = 'messages'
    id = Column('id', Integer, primary_key=True)
    send_time = Column('send_time', Integer, nullable=False)
    username = Column('username', String(20), ForeignKey('users.username'))
    sender = Column('sender', String(20), ForeignKey('users.username'))
    target_type = Column('target_type', Integer, nullable=False)
    target = Column('target', String(20), nullable=False)
    content = Column('content', String(200), nullable=False, default='')
    sent = Column('sent', Boolean, default=False)


class ChatRoom(Base):
    ''' 聊天室 '''
    __tablename__ = 'chat_rooms'

    created_at = Column('created_at', DateTime(timezone=False),
                        nullable=False, default=func.now())

    room_name = Column('room_name', String(20), primary_key=True)


class RoomUser(Base):
    ''' 聊天室成员 '''
    __tablename__ = 'room_users'

    roomname = Column('room', String(20), primary_key=True)
    username = Column('user', String(20), primary_key=True)


Base.metadata.bind = engine
Base.metadata.create_all()
