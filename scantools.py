#!/usr/bin/python
import argparse
import importlib
plugin_names = ['DSVCrop']
plugins = {}

ap = argparse.ArgumentParser("tscan")
ap.add_argument("plugin")
ap.add_argument("input")
subparsers = ap.add_subparsers(help="Plugins")

for name in plugins:
    plugin_module = importlib.import_module(name.lowercase())
    plugin = getattr(plugin_module, name)
    plugin_parser = subparsers.add_parser(name.lowercase(), help=getattr(plugin, "__description__"))
    plugin.arguments(plugin_parser)
    plugins[name] = plugin

opts, args = ap.parse_args()


