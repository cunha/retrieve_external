from retrieve_external.abstract_retriever import AbstractRetriever, DownloadInfo
import pandas as pd

class PCHRetriever(AbstractRetriever):

    def _get(self, inet):
        urls = []
        for day in self.days:
            df = pd.read_html(
                'https://www.pch.net/resources/Routing_Data/IPv{inet}_daily_snapshots/{year}/{month:02d}/'.format(inet=inet, year=day.year, month=day.month))[0]
            collectors = df.Name.unique()
            for collector in collectors:
                url = 'https://www.pch.net/resources/Routing_Data/IPv{inet}_daily_snapshots/{year}/{month:02d}/{coll}/{coll}-ipv{inet}_bgp_routes.{year}.{month:02d}.{day:02d}.gz'.format(
                    inet=inet, year=day.year, month=day.month, day=day.day, coll=collector)
                # print(url)
                info = DownloadInfo(url, self.newfilename(url), auth=self.auth)
                urls.append(info)
        return urls

    def get(self):
        urls = self._get(4)
        urls.extend(self._get(6))
        # for day in self.days:
        #     df = pd.read_html('https://www.pch.net/resources/Routing_Data/IPv4_daily_snapshots/{}/{:02d}/'.format(day.year, day.month))[0]
        #     collectors = df.Name.unique()
        #     for collector in collectors:
        #         url = 'https://www.pch.net/resources/Routing_Data/IPv4_daily_snapshots/{year}/{month:02d}/{coll}/{coll}-ipv4_bgp_routes.{year}.{month:02d}.{day:02d}.gz'.format(year=day.year, month=day.month, day=day.day, coll=collector)
        #         print(url)
        #         info = DownloadInfo(url, self.newfilename(url), auth=self.auth)
        #         urls.append(info)
        return urls

def get(args):
    pr = PCHRetriever(args)
    urls = pr.get()
    pr.parallel_download(urls)
