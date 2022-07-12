#!/usr/bin/env python
from argparse import ArgumentParser

from retrieve_external import bgpribs, riperecent, rirdelegations, relationships, peeringdb, pch
from retrieve_external.caidatraceroute import get_caidateam, get_caidaprefix
from retrieve_external import publictraceroute

def main():
    parser = ArgumentParser()
    parser.add_argument('-b', '--begin', help='Beginning date.', required=True)
    parser.add_argument('-e', '--end', help='Ending date.')
    parser.add_argument('-i', '--interval', type=int, default=1, help='Interval in days')
    parser.add_argument('-u', '--username', help='Username.')
    parser.add_argument('-p', '--password', help='Password.')
    parser.add_argument('-n', '--processes', type=int, default=5, help='Number of processes to use.')
    parser.add_argument('-d', '--dir', required=True, help='Output directory for the traceroute files.')
    sub = parser.add_subparsers()

    caidat = sub.add_parser('caida-team', help='Retrieve the CAIDA team probing traceroutes.')
    caidat.set_defaults(func=get_caidateam)

    caidap = sub.add_parser('caida-prefix', help='Retrieve the CAIDA prefix probing traceroutes.')
    caidap.set_defaults(func=get_caidaprefix)

    publict = sub.add_parser('public-team', help='Retrieve the public CAIDA team probing traces')
    publict.set_defaults(func=publictraceroute.get_publicteam)

    publicp = sub.add_parser('public-prefix', help='Retrieve the public CAIDA prefix probing traces')
    publicp.set_defaults(func=publictraceroute.get_publicprefix)

    bgp = sub.add_parser('bgp', help='Retrieve bgp RIBs from RouteViews and RIPE RIS.')
    bgp.set_defaults(func=bgpribs.get)

    rir = sub.add_parser('rir', help='Retrieve the RIR extended delegation files.')
    rir.set_defaults(func=rirdelegations.get)

    rels = sub.add_parser('rels', help='Retrieve AS relationships and customer cone files.')
    rels.set_defaults(func=relationships.get)

    pdb = sub.add_parser('peeringdb', help='Retreive PeeringDB json files.')
    pdb.set_defaults(func=peeringdb.get)

    pchf = sub.add_parser('pch', help='Retreive PCH route collector dump files.')
    pchf.set_defaults(func=pch.get)

    riperecentp = sub.add_parser('ripe-recent', help='Retrieve recent RIPE Atlas traceroutes')
    riperecentp.set_defaults(func=riperecent.get)

    args = parser.parse_args()
    if not args.end:
        args.end = args.begin
    args.func(args)
    # print(args.func)

if __name__ == '__main__':
    main()
