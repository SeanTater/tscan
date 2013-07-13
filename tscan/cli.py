import argparse
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help="Plugins")
plugins = []

enabled = False

class PluginRegistry(object):
    def __init__(self, enabled):
        self.enabled = enabled
        self.plugins = []
    
    def transform_to_argparse(self, argument, as_flag):
        ''' Remove ['name'] from argument but leave the original intact.
            The original arguments are  conveniently defined to be the same as argparse,
            but with the positional argument(s) to add_argument as 'name' in the dict. Undo that.'''
        arg_sans_name = argument.copy()
        names = arg_sans_name.pop('name')
        if not isinstance(names, (tuple, list)):
            names = [names]
        if not as_flag:
            names = [n.strip('-') for n in names]
        return names, arg_sans_name

    def register(self, plugin):
        ''' Add a plugin to the CLI '''
        plugins.append(plugin)
        if not enabled:
            # Only actually act if CLI is enabled
            return plugin
        
        def init_from_cli(cli_args):
            kw = {}
            for arg in plugin._args:
                names, extra = transform_to_argparse(argument, as_flag=False)
                name = names[-1]
                if name in cli_args:
                    kw[name] = cli_args[name]
            return plugin(**kw)
        
        return init_from_cli

default = PluginRegistry(enabled=False)