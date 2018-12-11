#!/usr/bin/env python
from argparse import ArgumentParser

from external.caidatraceroute import get_caidatraceroute


def main():
    parser = ArgumentParser()
    sub = parser.add_subparsers()
    caida = sub.add_parser('caida', help='Retrieve the CAIDA traceroutes.')
    caida.add_argument('-b', '--begin', help='Beginning date.', required=True)
    caida.add_argument('-e', '--end', help='Ending date.', required=True)
    caida.add_argument('-u', '--username', help='CAIDA username')
    caida.add_argument('-p', '--password', help='CAIDA password')
    caida.add_argument('-n', '--processes', type=int, default=5, help='Number of processes to use.')
    caida.add_argument('-d', '--dir', default='.', help='Output directory for the traceroute files.')
    caida.set_defaults(func=get_caidatraceroute)
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
