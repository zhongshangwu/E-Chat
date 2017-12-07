from client.modes.base import Mode
from client.modes.login import LoginHandler
from client.modes.chat import ChatHandler
from client.modes.query import QueryHandler
from client.modes.command import CommandHandler
from client.modes.register import RegisterHandler
from client.modes.contact import ContactHandler


modes = {
    Mode.COMMAND: CommandHandler,
    Mode.CHAT: ChatHandler,
    Mode.QUERY: QueryHandler,
    Mode.Login: LoginHandler,
    Mode.REGISTER: RegisterHandler,
    Mode.CONTACT: ContactHandler
}




