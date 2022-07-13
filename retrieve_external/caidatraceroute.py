import re
from enum import Enum
from typing import Iterable, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from retrieve_external.abstract_retriever import AbstractRetriever, DownloadInfo

class TType(Enum):
    """Traceroute types."""
    team = 1
    prefix = 2

class TTypeException(Exception):
    """Raise for incorrectly supplied traceroute types."""

class CaidaTraceroute(AbstractRetriever):
    PREFIX_BASE_URL = "https://data.caida.org/datasets/topology/ark/ipv4/prefix-probing/"
    TEAM_BASE_URL = "https://data.caida.org/datasets/topology/ark/ipv4/probe-data/"


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
                        info = DownloadInfo(joinedhref, self.newfilename(joinedhref), auth=self.auth)
                        urls.append(info)
        return urls

    def get_prefix(self):
        for day in self.days:
            url = f"{CaidaTraceroute.PREFIX_BASE_URL}/{day.year}/{day.month:02d}/"
            regex = f".*{day.year}{day.month:02d}{day.day:02d}.*.warts.gz"
            yield url, regex

    def get_team(self):
        for day in self.days:
            for team in range(1, 4):
                path = f"team-{team}/daily/{day.year}/cycle-{day.year}{day.month:02d}{day.day:02d}/"
                url = f"{CaidaTraceroute.TEAM_BASE_URL}/{path}"
                yield url, r'.*\.warts\.gz'

def get(args, ttype):
    if not args.username or not args.password:
        raise Exception('Must supply username and password')
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
