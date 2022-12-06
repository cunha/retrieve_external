import datetime
import os
import re
import urllib

import requests
from bs4 import BeautifulSoup

from retrieve_external.abstract_retriever import (AbstractRetriever,
                                                  DownloadInfo)


_BASE_URL = "https://data-store.ripe.net/datasets/atlas-daily-dumps/"
_DATE_REGEX = r"(?P<year>[0-9]{4})-(?P<month>[0-9]{2})-(?P<day>[0-9]{2})"


def _build_urls(retriever):
    r = requests.get(_BASE_URL)
    if not r.ok:
        print(f"Could not fetch {_BASE_URL}")
        return []

    soup = BeautifulSoup(r.text, features="html.parser")
    table = soup.find("table")
    if not table:
        # As of 2022-12-06, it seems RIPE updated their servers and the
        # index page has a different DOM. We're keeping the find("table")
        # above for additional resilience for now.
        table = soup.find("pre")
    if not table:
        print("Failed to parse file index from RIPE's server, no table or pre tags")
        print(f"URL was {_BASE_URL}")
        return []
    available = set()
    regex = re.compile(_DATE_REGEX)
    for link in table.find_all("a"):
        href = link["href"]
        m = regex.search(href)
        if m:
            year, month, day = int(m.group("year")), int(m.group("month")), int(m.group("day"))
            date = datetime.datetime(year, month, day)
            available.add(date)

    days = [d for d in retriever.days if d in available]
    if not days:
        print("RIPE traceroutes for the target period are no longer available")
        return []
    if len(days) < len(retriever.days):
        print("Some of the requested days were not available")

    retriever.days = days
    infos = []
    for d in days:
        regex_str = f"traceroute-{d.strftime('%Y-%m-%d')}T" + r"[0-9]{4}.bz2"
        regex = re.compile(regex_str)
        url = urllib.parse.urljoin(_BASE_URL, d.strftime("%Y-%m-%d") + "/")
        r = requests.get(url)
        if not r.ok:
            print(f"Could not get {url}")
            continue
        soup = BeautifulSoup(r.text, features="html.parser")
        table = soup.find("table")
        if not table:
            table = soup.find("pre")
        if not table:
            print("Failed to parse file index from RIPE's server, no table or pre tags")
            print(f"URL was {url}")
            continue
        for link in table.find_all("a"):
            href = link["href"]
            m = regex.search(href)
            if m:
                fullhref = urllib.parse.urljoin(url, href)
                filename = os.path.basename(urllib.parse.urlparse(fullhref).path)
                infos.append(DownloadInfo(fullhref, filename, auth=None))

    return infos


def get(args):
    retriever = AbstractRetriever(args)
    infos = _build_urls(retriever)
    retriever.parallel_download(infos)
