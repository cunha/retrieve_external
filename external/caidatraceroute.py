from datetime import timedelta
from multiprocessing.pool import Pool
from os import makedirs
from os.path import basename, join as pjoin
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
from humanfriendly import format_size
from progress.bar import Progress


class CaidaTraceroute:

    def __init__(self, args):
        self.args = args
        self.auth = (args.username, args.password) if args.username else None
        self.begin = parse(args.begin)
        self.end = parse(args.end)
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

    def get(self):
        days = [self.begin + timedelta(i) for i in range((self.end - self.begin).days + 1)]
        urls = []
        for day in days:
            for team in range(1, 4):
                url = ('https://topo-data.caida.org/team-probing/list-7.allpref24/team-{team}/daily/{year}/'
                       'cycle-{year}{month:02d}{day:02d}/').format(
                    team=team, year=day.year, month=day.month, day=day.day)
                r = requests.get(url, auth=self.auth)
                if r.ok:
                    soup = BeautifulSoup(r.text, features="html.parser")
                    pre = soup.find('pre')
                    links = pre.find_all('a')
                    for link in links:
                        href = link['href']
                        if href.startswith('daily'):
                            joinedhref = urljoin(url, href)
                            urls.append(joinedhref)
        totalsize = 0
        pb = Progress(len(urls), 'Downloading traceroute files',
                      callback=lambda: 'Size {}'.format(format_size(totalsize)))
        with Pool(self.processes) as pool:
            for size in pb.iterator(pool.imap_unordered(self.download, urls)):
                totalsize += size


def get_caidatraceroute(args):
    ct = CaidaTraceroute(args)
    ct.get()
