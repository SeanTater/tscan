import importlib
import cli

from common import *

def call():
    # How to do this automatically?
    module_names = ['crop', 'crop_gradient']

    for module_name in module_names:
        plugin_name = module_name.title().replace("_", "")
        
        module = importlib.import_module('tscan.%s' %module_name)
        plugin = getattr(module, plugin_name)
        plugin_description, plugin_doc = [t.strip() for t in plugin.__doc__.split('\n', 1)]
        plugin_parser = cli.subparsers.add_parser(module_name,
            help=plugin_description,
            epilog=plugin_doc)
        plugin_parser.set_defaults(plugin=plugin)

    args = cli.parser.parse_args()
    # Instantiate and call the plugin
    args.plugin.supervise(args)

    # Backward
    p_out = FileSink(args.output)
    p_middle = Pipe(plugin, p_out)
    p_in = NameListSource(args.input)
    
    # Forward
    p_in.run()
    p_middle.run()
    p_out.run()