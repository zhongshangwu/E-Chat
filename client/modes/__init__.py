from client.modes.base import Mode
from client.modes.login import LoginHandler
from client.modes.chat import ChatHandler
from client.modes.query import QueryHandler
from client.modes.command import CommandHandler


modes = {
    Mode.COMMAND.name: CommandHandler,
    Mode.CHAT.name: ChatHandler,
    Mode.QUERY.name: QueryHandler,
    Mode.Login.name: LoginHandler
}




