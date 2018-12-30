from dateutil.relativedelta import relativedelta

from external.abstract_retriever import AbstractRetriever, DownloadInfo


class BGPRetriever(AbstractRetriever):

    def get(self):
        urls = []
        months = self.end.month - self.begin.month
        months += 12 * (self.end.year - self.begin.year)
        for i in range(months + 1):
            month = self.begin + relativedelta(months=i)
            url = 'http://data.caida.org/datasets/as-relationships/serial-1/{year}{month:02d}01.as-rel.txt.bz2'.format(year=month.year, month=month.month)
            info = DownloadInfo(url, self.newfilename(url), auth=self.auth)
            urls.append(info)
            url = 'http://data.caida.org/datasets/as-relationships/serial-1/{year}{month:02d}01.ppdc-ases.txt.bz2'.format(year=month.year, month=month.month)
            info = DownloadInfo(url, self.newfilename(url), auth=self.auth)
            urls.append(info)
        return urls


def get(args):
    br = BGPRetriever(args)
    urls = br.get()
    br.parallel_download(urls)
