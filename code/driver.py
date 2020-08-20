import sys
import argparse
from conics_parser import parse
from dot import dot_parser
from display import display
from synthesize import synthesize

argparser = argparse.ArgumentParser(description = 'Synthesize a transducer from a sketch.')
argparser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help='A sketch, see examples for inspiration and grammar for completeness')
argparser.add_argument('-s', '--start', help='start node')
args = argparser.parse_args()

print(args.start)

examples = [
    [['word', 's1'], ['word', 's1']],
    [['word', 's1', 's1', 's1', 's1'], ['word', 's1', 's2', 's2', 's2']]
]

raw_text = ''.join(args.infile.readlines())
sexpr = dot_parser(raw_text)
for example in examples:
    sexpr.append(["example", *example])
display(synthesize(sexpr, args.start))