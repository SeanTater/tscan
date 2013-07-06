#!/usr/bin/python
import argparse
import importlib
plugin_names = ['Crop', 'CropCorners']
plugins = {}

ap = argparse.ArgumentParser("tscan")
subparsers = ap.add_subparsers(help="Plugins")

for name in plugin_names:
    plugin_module = importlib.import_module(name.lower())
    plugin = getattr(plugin_module, name)
    plugin_parser = subparsers.add_parser(name.lower(), help=plugin.__description__)
    plugin_parser.set_defaults(plugin=plugin)
    plugin.arguments(plugin_parser)
    plugins[name] = plugin

args = ap.parse_args()
# Instantiate and call the plugin
args.plugin.supervise(args)
