import argparse
import importlib

def call():
    module_names = ['crop']

    ap = argparse.ArgumentParser()
    subparsers = ap.add_subparsers(help="Plugins")

    for module_name in module_names:
        plugin_name = module_name.title().replace("_", "")
        
        module = importlib.import_module('tscan.%s' %module_name)
        plugin = getattr(module, plugin_name)
        
        plugin_parser = subparsers.add_parser(module_name, help=plugin.__description__)
        plugin_parser.set_defaults(plugin=plugin)
        plugin.arguments(plugin_parser)

    args = ap.parse_args()
    # Instantiate and call the plugin
    args.plugin.supervise(args)
