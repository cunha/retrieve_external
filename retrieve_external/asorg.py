import datetime
import os
import re
import urllib
from collections import defaultdict

import requests
from bs4 import BeautifulSoup

from retrieve_external.abstract_retriever import (AbstractRetriever,
                                                  DownloadInfo)

_AS2ORG_BASE_URL = "https://publicdata.caida.org/datasets/as-organizations/"
_AS2ORG_FILENAME_REGEX = r"(?P<date>[0-9]+)\.as-org2info\..*\.gz"


def _build_urls(retriever):
    r = requests.get(_AS2ORG_BASE_URL)
    if not r.ok:
        print(f"Could not fetch {_AS2ORG_BASE_URL}")
        return []

    regex = re.compile(_AS2ORG_FILENAME_REGEX)
    date2url = defaultdict(list)
    soup = BeautifulSoup(r.text, features="html.parser")
    pre = soup.find("pre")
    for link in pre.find_all("a"):
        href = link["href"]
        m = regex.search(href)
        if m:
            date = datetime.datetime.strptime(m.group("date"), "%Y%m%d")
            joinedref = urllib.parse.urljoin(_AS2ORG_BASE_URL, href)
            date2url[date].append(joinedref)
    if not date2url:
        print(f"Did not identify any files in index of {_AS2ORG_BASE_URL}")
        return []

    i = 0
    sorted_dates = sorted(date2url.keys())
    sorted_dates.append(datetime.datetime(9999, 1, 1))  # sentinel
    closest_dates = set()
    for d in retriever.days:
        while sorted_dates[i + 1] < d:
            # Try to place d between sorted_dates[i] and sorted_dates[i+1]
            i += 1
        if abs(d - sorted_dates[i]) < abs(sorted_dates[i + 1] - d):
            closest_dates.add(sorted_dates[i])
        else:
            closest_dates.add(sorted_dates[i + 1])

    infos = []
    for d in closest_dates:
        for href in date2url[d]:
            filename = os.path.basename(urllib.parse.urlparse(href).path)
            infos.append(DownloadInfo(href, filename, auth=None))
    return infos


def get(args):
    retriever = AbstractRetriever(args)
    infos = _build_urls(retriever)
    retriever.parallel_download(infos)
