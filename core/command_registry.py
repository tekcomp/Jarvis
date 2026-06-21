COMMANDS = {}

def register(name):
    def wrapper(fn):
        COMMANDS[name] = fn
        return fn
    return wrapper


def get(name):
    return COMMANDS.get(name)


def all_commands():
    return COMMANDS