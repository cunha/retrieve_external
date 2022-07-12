import datetime
import sys

from retrieve_external.caidatraceroute import TType, CaidaTraceroute


class PublicTraceroute(CaidaTraceroute):
    PREFIX_BASE_URL = "https://publicdata.caida.org/datasets/topology/ark/ipv4/prefix-probing"
    TEAM_BASE_URL = "https://publicdata.caida.org/datasets/topology/ark/ipv4/probe-data"

    def __init__(self, args):
        super().__init__(args)
        now = datetime.datetime.now()
        # Publishing seems to happen at the end of the month
        last_public_day = datetime.datetime(now.year - 1, now.month, 1)
        last_public_day -= datetime.timedelta(days=1)
        orig_days = len(self.days)
        self.days = [d for d in self.days if d <= last_public_day]
        print(f"Estimated last day of public traces: {last_public_day}")
        if not self.days:
            print("Traceroutes for the target period are not public yet!")
        if self.days and orig_days > len(self.days):
            print("Some traceroues in the target period are not public yet.")
            print(f"Will download public traceroutes between {min(self.days)} and {max(self.days)}")

    def get_prefix(self):
        for day in self.days:
            url = f"{PublicTraceroute.PREFIX_BASE_URL}/{day.year}/{day.month:02d}/"
            regex = f".*{day.year}{day.month:02d}{day.day:02d}.*.warts.gz"
            yield url, regex

    def get_team(self):
        for day in self.days:
            for team in range(1, 4):
                path = f"team-{team}/{day.year}/cycle-{day.year}{day.month:02d}{day.day:02d}/"
                url = f"{PublicTraceroute.TEAM_BASE_URL}/{path}"
                yield url, r".*\.warts\.gz"


def get(args, ttype):
    pt = PublicTraceroute(args)
    if ttype == TType.team:
        urls = pt.get(pt.get_team())
    elif ttype == TType.prefix:
        urls = pt.get(pt.get_prefix())
    else:
        raise ValueError(f"Invalid trace type: {ttype}")
    pt.parallel_download(urls)


def get_publicteam(args):
    get(args, TType.team)


def get_publicprefix(args):
    get(args, TType.prefix)
