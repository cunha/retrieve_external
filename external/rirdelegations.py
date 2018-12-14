from datetime import datetime

from external.abstract_retriever import AbstractRetriever, DownloadInfo


class RIRRetriever(AbstractRetriever):

    @staticmethod
    def afrinic(dt: datetime):
        return 'https://ftp.afrinic.net/pub/stats/afrinic/{year}/delegated-afrinic-extended-{year}{month:02d}{day:02d}'.format(year=dt.year, month=dt.month, day=dt.day)

    @staticmethod
    def apnic(dt: datetime):
        return 'https://ftp.apnic.net/stats/apnic/{year}/delegated-apnic-extended-{year}{month:02d}{day:02d}.gz'.format(year=dt.year, month=dt.month, day=dt.day)

    @staticmethod
    def arin(dt: datetime):
        archive = '' if dt.year >= 2017 else 'archive/{year}/'.format(year=dt.year)
        return 'https://ftp.arin.net/pub/stats/arin/{archive}delegated-arin-extended-{year}{month:02d}{day:02d}'.format(year=dt.year, month=dt.month, day=dt.day, archive=archive)

    @staticmethod
    def lacnic(dt: datetime):
        return 'https://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-extended-{year}{month:02d}{day:02d}'.format(year=dt.year, month=dt.month, day=dt.day)

    @staticmethod
    def ripe(dt: datetime):
        return 'https://ftp.ripe.net/pub/stats/ripencc/{year}/delegated-ripencc-extended-{year}{month:02d}{day:02d}.bz2'.format(year=dt.year, month=dt.month, day=dt.day)

    @staticmethod
    def urls(dt: datetime):
        yield RIRRetriever.afrinic(dt)
        yield RIRRetriever.apnic(dt)
        yield RIRRetriever.arin(dt)
        yield RIRRetriever.lacnic(dt)
        yield RIRRetriever.ripe(dt)

    def get(self):
        urls = []
        for day in self.days:
            for url in self.urls(day):
                info = DownloadInfo(url, self.newfilename(url))
                urls.append(info)
        return urls


def get(args):
    rir = RIRRetriever(args)
    urls = rir.get()
    rir.parallel_download(urls)
