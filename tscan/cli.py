
class Argument(object):
    def __init__(self, *flags, **tags):
        self.flags = flags
        self.names = [flag.strip('-') for flag in flags]
        self.name = max(self.names, key=len)
        self.tags = tags
    
    def add_to_argparse(self, parser):
        parser.add_argument(*self.flags, **self.tags)

class PluginRegistry(object):
    def __init__(self, enabled):
        self.enabled = enabled
        self.plugins = []

    def register(self, plugin):
        ''' Add a plugin to the CLI '''
        self.plugins.append(plugin)
        if not self.enabled:
            # Only actually act if CLI is enabled
            return plugin
        
        def init_from_cli(cli_args):
            kw = {arg.name: getattr(cli_args, arg.name) for arg in plugin._args if arg.name in cli_args}
            return plugin(**kw)
        
        return init_from_cli

default = PluginRegistry(enabled=False)