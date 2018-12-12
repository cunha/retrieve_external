from abc import ABC
from datetime import timedelta
from multiprocessing.pool import Pool
from os import makedirs
from os.path import basename, join as pjoin
from urllib.parse import urlparse

import requests
from dateutil.parser import parse
from humanfriendly import format_size
from progress.bar import Progress


class AbstractRetriever(ABC):
    def __init__(self, args):
        self.auth = (args.username, args.password) if args.username else None
        self.begin = parse(args.begin)
        self.end = parse(args.end)
        self.days = [self.begin + timedelta(i) for i in range((self.end - self.begin).days + 1)]
        self.processes = args.processes
        self.dir = args.dir
        if self.dir != '.' and self.dir != '..':
            makedirs(self.dir, exist_ok=True)

    def newfilename(self, url):
        return basename(urlparse(url).path)

    def download(self, url):
        filename = self.newfilename(url)
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
