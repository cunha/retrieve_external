import sys
from abc import ABC, abstractmethod
from collections import namedtuple
from datetime import timedelta
from multiprocessing.pool import Pool
from os import makedirs
from os.path import basename, join as pjoin
from urllib.parse import urlparse

import requests
from dateutil.parser import parse
from humanfriendly import format_size
from traceutils.progress.bar import Progress

class DownloadInfo:
    def __init__(self, url, filename, auth=None):
        self.url = url
        self.filename = filename
        self.auth = auth

class AbstractRetriever(ABC):
    def __init__(self, args):
        self.auth = (args.username, args.password) if args.username else None
        self.begin = parse(args.begin)
        self.end = parse(args.end)
        self.interval = args.interval
        self.days = [self.begin + timedelta(i) for i in range(0, (self.end - self.begin).days + 1, self.interval)]
        self.processes = args.processes
        self.dir = args.dir
        if self.dir != '.' and self.dir != '..':
            makedirs(self.dir, exist_ok=True)

    def newfilename(self, url: str):
        return basename(urlparse(url).path)

    def download(self, info: DownloadInfo):
        r = requests.get(info.url, auth=info.auth, allow_redirects=True)
        if not r.ok:
            print('\r\033[KWarning: {}'.format(info.url), file=sys.stderr)
            return 0
        content = r.content
        with open(pjoin(self.dir, info.filename), 'wb') as f:
            f.write(content)
        return len(content)

    def parallel_download(self, urls):
        if not urls:
            print('No files found to download')
            return
        totalsize = 0
        pb = Progress(len(urls), 'Downloading files',
                      callback=lambda: 'Size {}'.format(format_size(totalsize)))
        try:
            with Pool(min(self.processes, len(urls))) as pool:
                for size in pb.iterator(pool.imap_unordered(self.download, urls)):
                    totalsize += size
        except KeyboardInterrupt:
            print('Ending prematurely.')
