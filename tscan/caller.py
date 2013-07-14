import argparse
import importlib
import cli
from common import *

def call():
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', metavar='filename', nargs='+', help='Input'
                        ' filenames')
    parser.add_argument('-o', '--output-pattern', help='Output filename or '
                        'pattern')
    subparsers = parser.add_subparsers(help="Plugins")
    # How to do this automatically?
    module_names = ['crop_contrast', 'crop_gradient']

    # It would be great if we didn't have to load all of these every time
    for module_name in module_names:
        module = importlib.import_module('tscan.%s' %module_name)
    
    for plugin in cli.Plugin.all_plugins:
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
    p_in = NameListSource(cli_args.filenames)
    p_middle = cli_args.plugin.init_from_cli(cli_args)
    p_out = FileSink(cli_args.filenames)
    
    Pipe(p_in, p_middle, p_out).run()
    
    