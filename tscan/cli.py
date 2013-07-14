
class Argument(object):
    def __init__(self, *flags, **tags):
        self.flags = flags
        self.names = [flag.strip('-') for flag in flags]
        self.name = max(self.names, key=len)
        self.tags = tags
    
    def add_to_argparse(self, parser):
        parser.add_argument(*self.flags, **self.tags)

class Plugin(object):
    all_plugins = set()
    
    @classmethod
    def init_from_cli(cls, cli_args):
        kw = {arg.name: getattr(cli_args, arg.name) for arg in cls._args if arg.name in cli_args}
        return cls(**kw)

    @classmethod
    def register(cls, plugin):
        ''' Add a plugin to the CLI '''
        cls.all_plugins.add(plugin)
        return plugin