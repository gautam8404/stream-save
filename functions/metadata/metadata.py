import re
import tempfile
import time

import libtorrent as lt

import requests
import urllib.parse


class Metadata:
    OPTIONAL_META = ["posterShape", "description", "releaseInfo", "imdbRating", "director", "cast",
                     "inTheaters", "runtime", "trailers", "videos"]

    def __init__(self):
        self.base_url = "https://cinemeta-live.strem.io/meta/{}/{}.json"

    @staticmethod
    def append_tracker(tracker):
        return "tracker:" + tracker

    def identify_link(self, url: str) -> dict:
        yt_pattern = re.compile(r'(?:https?:\/\/)?(?:[0-9A-Z-]+\.)?(?:youtube|youtu|youtube-nocookie)\.(?:com|be)\/('
                                r'?:watch\?v=|watch\?.+&v=|embed\/|v\/|.+\?v=)?([^&=\n%\?]{11})')

        magnet_pattern = re.compile(r"magnet:\?xt=urn:[a-z0-9]+:[a-zA-Z0-9]{32}")

        res = yt_pattern.findall(url)
        common_dict = {'description': None}
        try:
            if res:
                common_dict["ytId"] = res[0]
                return common_dict
            elif magnet_pattern.match(url) is not None:
                mg_dict = {}
                parsed_magnet = urllib.parse.urlparse(url)
                parsed_magnet_dict = urllib.parse.parse_qs(parsed_magnet.query)
                infohash = parsed_magnet_dict['xt'][0].split(':')[-1]
                try:
                    trackers = parsed_magnet_dict['tr']
                    trackers = list(map(self.append_tracker, trackers))
                except KeyError:
                    trackers = []
                try:
                    description = parsed_magnet_dict['dn'][0]
                except KeyError:
                    description = None

                mg_dict['sources'] = trackers + [f'dht:{infohash.lower()}']
                mg_dict['name'] = "Stream Save"
                mg_dict['infoHash'] = infohash
                mg_dict['description'] = description

                return mg_dict

            elif url.startswith(("http", "https")):
                common_dict["url"] = url
                return common_dict
            else:
                common_dict["url"] = None
                return common_dict
        except Exception as e:
            print(e)
            raise MetaExceptions("Invalid Url")

    def get_magnet_streams(self, magnet, res):
        parsed_magnet = urllib.parse.urlparse(magnet)
        try:
            trackers = urllib.parse.parse_qs(parsed_magnet.query)['tr']
        except KeyError:
            trackers = []

        retries = 20
        ses = lt.session()
        ses.listen_on(6881, 6891)

        params = {
            "save_path": tempfile.mkdtemp(),
            "file_priorities": [0] * 5000,  # just to make sure it doesn't download anything
            "storage_mode": lt.storage_mode_t(2)
        }
        handle = lt.add_magnet_uri(ses, magnet, params)
        for tracker in trackers:
            handle.add_tracker({"url": tracker})
        ses.start_dht()
        while not handle.has_metadata() and retries > 0:
            retries = retries - 1
            time.sleep(1)
        if not handle.has_metadata():
            return {}

        files = []
        torinfo = handle.get_torrent_info()
        for x in range(torinfo.files().num_files()):
            files.append("".join((torinfo.files().file_path(x).lower()).split()))
        if not files:
            return {}
        videos = res['videos']
        files.sort()

        s = '0'
        e = '0'
        streams = []
        specifiers = ["s{}e{}", "{}x{}"]
        for i in videos:
            s = str(i['season'])
            e = str(i['episode'])

            # print(i)

            for j in files:
                if specifiers[0].format(s.zfill(2), e.zfill(2)) in j \
                        or specifiers[0].format(s.zfill(2), e.zfill(2)) in j \
                        or specifiers[1].format(s, e.zfill(2)) in j \
                        or specifiers[1].format(s, e) in j \
                        and j.endswith(
                    ('.mkv', '.mp4', '.webm', '.mov', '.avi', '.mpg', '.mpeg', '.m4v', '.flv', '.m4p')):
                    x = {'_id': i['id'], 'data': {'fileIdx': files.index(j)}}
                    y = self.identify_link(magnet)
                    if y['description'] is None:
                        y['description'] = i['title']
                    x['data'].update(y)
                    streams.append(x)
                    break
        return streams

    def make_meta(self, item):
        meta = dict((key, item[key])
                    for key in item.keys() if key in self.OPTIONAL_META)
        meta['_id'] = item['id']
        meta['id'] = item['id']
        meta['type'] = item['type']
        meta['name'] = item['name']
        meta['genres'] = item['genres']
        meta['poster'] = item['poster']
        return meta

    def _call(self, res):
        if res.status_code == 404:
            raise MetaExceptions("Invalid IMDB ID")
        elif res.json() == {}:
            raise MetaExceptions("Invalid Type")
        elif res.status_code != 200:
            raise MetaExceptions(f"{res.status_code} error")

    def get_movie(self, imdbId, stream: str):
        url = self.base_url.format("movie", imdbId)
        res = requests.get(url)
        self._call(res)

        res = res.json()['meta']

        catalog = self.make_meta(res)

        y = self.identify_link(stream)
        print(catalog)
        if y['description'] is None:
            y['description'] = catalog['name']

        streams = [{"_id": imdbId, 'data': y}]

        return catalog, streams

    def get_series(self, imdbId: str, stream: str):
        series_id = imdbId
        separate = False
        if ":" in imdbId:
            series_id = imdbId.split(":")[0]
            separate = True

        url = self.base_url.format("series", series_id)
        res = requests.get(url)
        self._call(res)
        res = res.json()['meta']
        catalog = self.make_meta(res)
        link = self.identify_link(stream)
        if "infoHash" in list(link.keys()) and separate is False:
            streams = self.get_magnet_streams(stream, res)
        else:
            if link['description'] is None:
                link['description'] = catalog['name']
            streams = [{"_id": imdbId, 'data': link}]

        return catalog, streams


class MetaExceptions(Exception):
    pass
