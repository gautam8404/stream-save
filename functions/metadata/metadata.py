import re
import tempfile
import time

import libtorrent as lt

import requests


class Metadata:
    OPTIONAL_META = ["posterShape", "description", "releaseInfo", "imdbRating", "director", "cast",
                     "inTheaters", "runtime", "trailers", "videos"]

    def __init__(self):
        self.base_url = "https://cinemeta-live.strem.io/meta/{}/{}.json"

    @staticmethod
    def identify_link(url: str) -> dict:
        yt_pattern = re.compile(r'(?:https?:\/\/)?(?:[0-9A-Z-]+\.)?(?:youtube|youtu|youtube-nocookie)\.(?:com|be)\/(' \
                                r'?:watch\?v=|watch\?.+&v=|embed\/|v\/|.+\?v=)?([^&=\n%\?]{11})')

        magnet_pattern = re.compile(r"magnet:\?xt=urn:[a-z0-9]+:[a-zA-Z0-9]{32}")

        res = yt_pattern.findall(url)
        try:
            if res:
                return {"ytId": res}
            elif magnet_pattern.match(url) is not None:
                return {"infoHash": url.split("btih:")[1].split("&")[0]}
            elif url.startswith(("http", "https")) and url.endswith(("mp4", "mkv")):
                return {"url": url}
            else:
                return {"url": None}
        except:
            raise MetaExceptions("Invalid Url")

    def get_magnet_streams(self, magnet, res):
        retries = 20
        ses = lt.session()
        ses.listen_on(6881, 6891)

        params = {
            "save_path": tempfile.mkdtemp(),
            "file_priorities": [0] * 5000,  # just to make sure it doesn't download anything
            "storage_mode": lt.storage_mode_t(2)
        }
        handle = lt.add_magnet_uri(ses, magnet, params)
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
                        or specifiers[1].format(s, e) in j:
                    x = {'_id': i['id'], 'data': {'title': i['title'], 'fileIdx': files.index(j)}}
                    y = self.identify_link(magnet)
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
            raise MetaExceptions("Invalid ID")
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
        x = {'title': catalog['name']}
        y = self.identify_link(stream)
        z = {**x , **y}
        streams = [{"_id": imdbId, 'data': z}]

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

        if "infoHash" in link and separate is False:
            streams = self.get_magnet_streams(stream, res)
        else:
            a = {'title': catalog['name']}
            b = {**a, **link}
            streams = [{"_id": imdbId, 'data': b}]

        return catalog, streams


class MetaExceptions(Exception):
    pass
