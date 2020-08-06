import sys
import argparse
from conics_parser import parse
from display import display
from synthesize import synthesize

argparser = argparse.ArgumentParser(description = 'Synthesize a transducer from a sketch.')
argparser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help='A sketch, see examples for inspiration and grammar for completeness')
args = argparser.parse_args()

raw_text = ''.join(args.infile.readlines())
sexpr = parse(raw_text)
display(synthesize(sexpr))