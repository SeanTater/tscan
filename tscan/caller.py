import importlib
import cli
from common import *

def call():
    cli.enabled = True
    # How to do this automatically?
    module_names = ['crop', 'crop_gradient']

    # It would be great if we didn't have to load all of these every time
    for module_name in module_names:
        module = importlib.import_module('tscan.%s' %module_name)
    
    for plugin in cli.plugins:
        plugin_description, plugin_doc = [t.strip() for t in plugin.__doc__.split('\n', 1)]
        
        # Certain builtin plugins have no commands
        if hasattr(plugin, '_builtin'):
            plugin_parser = cli.parser
        else:
            plugin_parser = cli.subparsers.add_parser(plugin._name,
                help=plugin_description,
                epilog=plugin_doc)
            plugin_parser.set_defaults(plugin=plugin)
        
        for arg in plugin._args:
            names, extra = cli.transform_to_argparse(arg, as_flag=True)
            plugin_parser.add_argument(*names, **extra)
        

    cli_args = cli.parser.parse_args()

    # These all take "args" because of cli.register
    p_in = NameListSource(cli_args)
    p_middle = cli_args.plugin(cli_args)
    p_out = FileSink(cli_args)
    
    Pipe(p_in, p_middle, p_out).run()
    
    