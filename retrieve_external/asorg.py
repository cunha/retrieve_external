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
_DATEMAP_FILENAME = "datemap.txt"


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

    file_dates = date2url.keys()
    inputdate2filedate = retriever.map_dates(file_dates)

    infos = []
    for d in inputdate2filedate.values():
        for href in date2url[d]:
            filename = os.path.basename(urllib.parse.urlparse(href).path)
            infos.append(DownloadInfo(href, filename, auth=None))
    return infos, inputdate2filedate


def get(args):
    retriever = AbstractRetriever(args)
    infos, inputdate2filedate = _build_urls(retriever)
    with open(os.path.join(retriever.dir, _DATEMAP_FILENAME), "w", encoding="utf8") as fd:
        for inputdate, filedate in inputdate2filedate.items():
            fd.write(f"{inputdate.strftime('%Y%m%d')} {filedate.strftime('%Y%m%d')}\n")

    retriever.parallel_download(infos)
