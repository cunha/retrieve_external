from datetime import timedelta, timezone, datetime
from typing import Any, Dict, List

import requests
from traceutils.progress.bar import Progress

from retrieve_external.abstract_retriever import AbstractRetriever, DownloadInfo

class BGPRetriever(AbstractRetriever):

    def get(self):
        urls = []
        pb = Progress(len(self.days), 'Gathering urls')
        print(self.days)
        for day in pb.iterator(self.days):
            nextday = utctimestamp(day + timedelta(1))
            tstamp = utctimestamp(day)
            url = 'https://bgpstream.caida.org/broker/data?human&intervals[]={begin},{end}&types[]=ribs'.format(begin=tstamp, end=nextday)
            r = requests.get(url)
            results = r.json()
            dumps: List[Dict[str, Any]] = results['data']['dumpFiles']
            for file in dumps:
                href = file['url']
                base = self.newfilename(href)
                filename = '{project}.{collector}.{type}.{base}'.format(base=base, **file)
                auth = self.auth if file['project'] == 'ris' else None
                info = DownloadInfo(href, filename, auth=auth)
                urls.append(info)
        return urls

def utctimestamp(dt: datetime):
    return dt.replace(tzinfo=timezone.utc).timestamp()

def get(args):
    ris = BGPRetriever(args)
    urls = ris.get()
    ris.parallel_download(urls)
