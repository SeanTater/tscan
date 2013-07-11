import argparse

parser = argparse.ArgumentParser()
subparsers = ap.add_subparsers(help="Plugins")

parser.add_argument("input", nargs='+', help='input filename[s]')
parser.add_argument("output", nargs='?', default=None,
    help='output filename or pattern (if more than one input)')