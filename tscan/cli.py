import argparse
import importlib

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
    
def call():
    # Import in the function to avoid cyclic dependencies
    from common import NameListSource, Progress, Pipe, FileSink
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output-pattern', help='Output filename or '
                        'pattern')
    parser.add_argument('-p', '--progress', action='store_true', help='Give simple progress info')
    
    parser.add_argument('filenames', metavar='filename', nargs='+', help='Input'
                        ' filenames')
    parser.add_argument('-w', '--max-workers', help='Maximum number of threads')
    subparsers = parser.add_subparsers(help="Plugins")
    # How to do this automatically?
    module_names = ['crop_contrast', 'crop_gradient', 'destripe']

    # It would be great if we didn't have to load all of these every time
    for module_name in module_names:
        module = importlib.import_module('tscan.%s' %module_name)
    
    for plugin in Plugin.all_plugins:
        plugin_description, plugin_doc = [t.strip() for t in plugin.__doc__.split('\n', 1)]
        
        # Certain builtin plugins have no commands
        plugin_parser = subparsers.add_parser(plugin._name,
            help=plugin_description,
            epilog=plugin_doc)
        plugin_parser.set_defaults(plugin=plugin)
        
        for arg in plugin._args:
            arg.add_to_argparse(plugin_parser)
    
    cli_args = parser.parse_args()

    # These all take "args" because of cli.register
    parts = []
    parts.append(NameListSource(cli_args.filenames))
    if cli_args.progress: parts.append(Progress())
    parts.append(cli_args.plugin.init_from_cli(cli_args))
    parts.append(FileSink(cli_args.output_pattern or "%(path_noext)s_out%(ext)s"))
    if cli_args.max_workers: Pipe.max_workers = cli_args.max_workers
    Pipe(*parts).run()