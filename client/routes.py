from commands import Command

registry = dict()


def command_router(command=None):
    def decorate(func):
        registry[command] = func

        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorate


@command_router(Command.LOGIN)
def login(request):
    pass
