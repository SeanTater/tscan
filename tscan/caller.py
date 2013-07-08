import argparse
import importlib

def call():
    module_names = ['crop', 'crop_gradient']

    ap = argparse.ArgumentParser()
    subparsers = ap.add_subparsers(help="Plugins")

    for module_name in module_names:
        plugin_name = module_name.title().replace("_", "")
        
        module = importlib.import_module('tscan.%s' %module_name)
        plugin = getattr(module, plugin_name)
        plugin_description, plugin_doc = [t.strip() for t in plugin.__doc__.split('\n', 1)]
        plugin_parser = subparsers.add_parser(module_name,
            help=plugin_description,
            epilog=plugin_doc)
        plugin_parser.set_defaults(plugin=plugin)
        plugin.arguments(plugin_parser)

    args = ap.parse_args()
    # Instantiate and call the plugin
    args.plugin.supervise(args)
