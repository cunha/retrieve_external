import datetime
import os
import re
import urllib
from collections import defaultdict

import requests
from bs4 import BeautifulSoup

from retrieve_external.abstract_retriever import (AbstractRetriever,
                                                  DownloadInfo)


_ITDK_CAIDA_URL = "https://data.caida.org/datasets/topology/ark/ipv4/itdk/"
_ITDK_PUBLIC_URL = "https://publicdata.caida.org/datasets/topology/ark/ipv4/itdk/"
_ITDK_FILENAME = "midar-iff.nodes.as.bz2"
_ITDK_DATE_REGEX = r"(?P<year>[0-9]{4})-(?P<month>[0-9]{2})"
_DATEMAP_FILENAME = "datemap.txt"


def _build_urls(retriever, baseurl):
    r = requests.get(baseurl, auth=retriever.auth)
    if not r.ok:
        print(f"Could not fetch {baseurl}")
        return [], {}

    regex = re.compile(_ITDK_DATE_REGEX)
    date2url = defaultdict(list)
    soup = BeautifulSoup(r.text, features="html.parser")
    pre = soup.find("pre")
    for link in pre.find_all("a"):
        href = link["href"]
        m = regex.search(href)
        if m:
            date = datetime.datetime(year=int(m.group("year")), month=int(m.group("month")), day=1)
            joinedref = urllib.parse.urljoin(baseurl, href)
            joinedref = urllib.parse.urljoin(joinedref, _ITDK_FILENAME)
            date2url[date].append(joinedref)

    if not date2url:
        print(f"Did not identify any files in index of {baseurl}")
        return [], {}

    file_dates = date2url.keys()
    inputdate2filedate = retriever.map_dates(file_dates)

    infos = []
    for filedate in inputdate2filedate.values():
        for href in date2url[filedate]:
            filename = os.path.basename(urllib.parse.urlparse(href).path)
            filename = f"{filedate.year:04d}{filedate.month:02d}-{filename}"
            infos.append(DownloadInfo(href, filename, auth=retriever.auth))
    return infos, inputdate2filedate


def get(args, baseurl):
    retriever = AbstractRetriever(args)
    infos, inputdate2filedate = _build_urls(retriever, baseurl)
    if infos:
        os.makedirs(retriever.dir, exist_ok=True)
        with open(os.path.join(retriever.dir, _DATEMAP_FILENAME), "w", encoding="utf8") as fd:
            for inputdate, filedate in inputdate2filedate.items():
                fd.write(f"{inputdate.strftime('%Y%m%d')} {filedate.strftime('%Y%m%d')}\n")
    retriever.parallel_download(infos)


def get_public(args):
    get(args, _ITDK_PUBLIC_URL)


def get_caida(args):
    if not args.username or not args.password:
        raise RuntimeError('Must supply username and password')
    get(args, _ITDK_CAIDA_URL)
