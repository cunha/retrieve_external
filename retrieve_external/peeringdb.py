from retrieve_external.abstract_retriever import AbstractRetriever, DownloadInfo

class PeeringdbRetriever(AbstractRetriever):

    def get(self):
        urls = []
        for day in self.days:
            url = 'https://publicdata.caida.org/datasets/peeringdb/{year}/{month:02d}/peeringdb_2_dump_{year}_{month:02d}_{day:02d}.json'.format(year=day.year, month=day.month, day=day.day)
            print(url)
            info = DownloadInfo(url, self.newfilename(url), auth=self.auth)
            urls.append(info)
        return urls

def get(args):
    pr = PeeringdbRetriever(args)
    urls = pr.get()
    pr.parallel_download(urls)
