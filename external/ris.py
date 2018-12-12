import re
from typing import List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from external.abstract_retriever import AbstractRetriever


class RIS(AbstractRetriever):

    def newfilename(self, url):
        m = re.search(r'rrc\d+', url)
        rrc = m.group()
        filename = super().newfilename(url)
        return '{}.{}'.format(rrc, filename)

    def get(self) -> List[str]:
        regex = re.compile(r'http://data.ris.ripe.net/rrc\d+')
        urls = []
        r = requests.get('https://www.ripe.net/analyse/internet-measurements/routing-information-service-ris/ris-raw-data', auth=self.auth)
        soup = BeautifulSoup(r.text, features="html.parser")
        core = soup.find('div', {'id': 'content-core'})
        links = core.find_all('a')
        for link in links:
            href = link['href'] + '/'
            if regex.search(href):
                for day in self.days:
                    url = urljoin(href, '{year}.{month:02d}/bview.{year}{month:02d}{day:02d}.{hour:04d}.gz'.format(
                        year=day.year, month=day.month, day=day.day, hour=0))
                    urls.append(url)
        return urls


def get(args):
    ris = RIS(args)
    urls = ris.get()
    ris.parallel_download(urls)
