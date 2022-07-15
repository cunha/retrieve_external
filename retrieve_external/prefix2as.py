import datetime
import os
import re
import urllib

import requests
from bs4 import BeautifulSoup

from retrieve_external.abstract_retriever import (AbstractRetriever,
                                                  DownloadInfo)

_PREFIX2AS_BASE_URL = "https://publicdata.caida.org/datasets/routing/routeviews-prefix2as/"
_PREFIX2AS_FILENAME_REGEX = r".*-(?P<date>[0-9]{8})-[0-9]{4}.pfx2as.gz"


def _build_urls(retriever):
    regex = re.compile(_PREFIX2AS_FILENAME_REGEX)
    url2date2href = {}
    infos = []
    for d in retriever.days:
        url = f"{_PREFIX2AS_BASE_URL}/{d.year}/{d.month:02d}/"
        if url not in url2date2href:
            url2date2href[url] = {}
            r = requests.get(url)
            if not r.ok:
                print(f"Could not fetch {url}")
                continue
            soup = BeautifulSoup(r.text, features="html.parser")
            pre = soup.find("pre")

            for atag in pre.find_all("a"):
                href = atag["href"]
                m = regex.search(href)
                if not m:
                    continue
                date = datetime.datetime.strptime(m.group("date"), "%Y%m%d")
                url2date2href[url][date] = href

        href = url2date2href[url].get(d, None)
        if href is None:
            print(f"Did not find file for date {d}")
            continue
        joinedref = urllib.parse.urljoin(url, href)
        filename = os.path.basename(urllib.parse.urlparse(joinedref).path)
        infos.append(DownloadInfo(joinedref, filename, None))

    return infos


def get(args):
    retriever = AbstractRetriever(args)
    infos = _build_urls(retriever)
    retriever.parallel_download(infos)
