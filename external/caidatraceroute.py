import re
from enum import Enum
from typing import Iterable, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from external.abstract_retriever import AbstractRetriever


class TType(Enum):
    """Traceroute types."""
    team = 1
    prefix = 2


class TTypeException(Exception):
    """Raise for incorrectly supplied traceroute types."""


class CaidaTraceroute(AbstractRetriever):

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
    elif ttype == TType.prefix:
        urls = ct.get(ct.get_prefix())
    else:
        raise TTypeException('Invalid TType')
    ct.parallel_download(urls)


def get_caidateam(args):
    get(args, TType.team)


def get_caidaprefix(args):
    get(args, TType.prefix)
