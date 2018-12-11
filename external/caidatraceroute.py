import re
from datetime import timedelta
from enum import Enum
from multiprocessing.pool import Pool
from os import makedirs
from os.path import basename, join as pjoin
from typing import Iterable, Tuple
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
from humanfriendly import format_size
from progress.bar import Progress


class TType(Enum):
    """Traceroute types."""
    team = 1
    probing = 2


class TTypeException(Exception):
    """Raise for incorrectly supplied traceroute types."""


class CaidaTraceroute:

    def __init__(self, args):
        self.args = args
        self.auth = (args.username, args.password) if args.username else None
        self.begin = parse(args.begin)
        self.end = parse(args.end)
        self.days = [self.begin + timedelta(i) for i in range((self.end - self.begin).days + 1)]
        self.processes = args.processes
        self.dir = args.dir
        if self.dir != '.' and self.dir != '..':
            makedirs(self.dir, exist_ok=True)

    def download(self, url):
        filename = basename(urlparse(url).path)
        r = requests.get(url, auth=self.auth, allow_redirects=True)
        content = r.content
        with open(pjoin(self.dir, filename), 'wb') as f:
            f.write(content)
        return len(content)

    def parallel_download(self, urls):
        totalsize = 0
        pb = Progress(len(urls), 'Downloading traceroute files',
                      callback=lambda: 'Size {}'.format(format_size(totalsize)))
        with Pool(self.processes) as pool:
            for size in pb.iterator(pool.imap_unordered(self.download, urls)):
                totalsize += size

    def get(self, iterable: Iterable[Tuple[str, str]]):
        urls = []
        for url, regex in iterable:
            regex = re.compile(regex)
            r = requests.get(url, auth=self.auth)
            if r.ok:
                soup = BeautifulSoup(r.text, features="html.parser")
                pre = soup.find('pre')
                links = pre.find_all('a')
                for link in links:
                    href = link['href']
                    if regex.search(href):
                        joinedhref = urljoin(url, href)
                        urls.append(joinedhref)
        return urls

    def get_prefix(self):
        for day in self.days:
            url = ('https://topo-data.caida.org/prefix-probing/'
                   '{year}/{month:02d}/').format(year=day.year, month=day.month)
            regex = r'.*{year}{month:02d}{day:02d}.*.warts.gz'.format(year=day.year, month=day.month, day=day.day)
            yield url, regex

    def get_team(self):
        for day in self.days:
            for team in range(1, 4):
                url = ('https://topo-data.caida.org/team-probing/list-7.allpref24/team-{team}/daily/{year}/'
                       'cycle-{year}{month:02d}{day:02d}/').format(
                    team=team, year=day.year, month=day.month, day=day.day)
                yield url, r'.*\.warts\.gz'


def get(args, ttype):
    ct = CaidaTraceroute(args)
    if ttype == TType.team:
        urls = ct.get(ct.get_team())
    elif ttype == TType.probing:
        urls = ct.get(ct.get_prefix())
    else:
        raise TTypeException('Invalid TType')
    ct.parallel_download(urls)


def get_caidateam(args):
    get(args, TType.team)


def get_caidaprefix(args):
    get(args, TType.probing)
