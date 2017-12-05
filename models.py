from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy import func, Table, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///database.db', echo=True)
Session = sessionmaker(bind=engine)

room_user = Table(
    'room_users', Base.metadata,
    Column('chat_room_id', Integer, ForeignKey('chat_rooms.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)


class User(Base):
    ''' 用户 '''
    __tablename__ = 'users'
    created_at = Column(DateTime(timezone=False),
                        nullable=False, default=func.now())

    id = Column(Integer, primary_key=True)
    username = Column(String(20), nullable=False)
    nickname = Column(String(20), nullable=False)
    password = Column(String(100), nullable=False)

    chat_rooms = relationship('ChatRoom', secondary=room_user)

    def __repr__(self):
        return "<User(name='%s')>" % self.name


class Message(Base):
    ''' 消息 '''
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=False),
                        nullable=False, default=func.now())

    content = Column(String(200), nullable=False)


class ChatRoom(Base):
    ''' 聊天室 '''
    __tablename__ = 'chat_rooms'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=False),
                        nullable=False, default=func.now())

    room_name = Column(String(20), nullable=False)
    users = relationship('User', secondary=room_user)


class Friend(Base):
    ''' 好友 '''
    __tablename__ = 'friends'

    id = Column(Integer, primary_key=True)
    from_user = Column(Integer, nullable=False)
    to_user = Column(Integer, nullable=False)
    accepted = Column(Boolean, default=False)


Base.metadata.bind = engine
Base.metadata.create_all()



