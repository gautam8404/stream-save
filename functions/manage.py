import requests

from functions.metadata.metadata import Metadata
from .mongo.moviedb import movieCatalog, movieStreams
from .mongo.seriesdb import seriesCatalog, seriesStreams
from pymongo import MongoClient

CINEMETA_URL = "https://cinemeta-live.strem.io/meta/{}/{}.json"


def removeMovie(id, db_url):
    client = MongoClient(db_url)
    moviecat = movieCatalog(client)
    moviestream = movieStreams(client)

    rem = {"_id": id}
    moviecat.remove(rem)
    moviestream.remove(rem)


def removeSeries(id, db_url):
    client = MongoClient(db_url)
    seriescat = seriesCatalog(client)
    seriestream = seriesStreams(client)
    videos = requests.get(CINEMETA_URL.format("series", id)).json()['meta']['videos']
    rem = {"_id": id}
    seriescat.remove(rem)

    for i in videos:
        s = str(i['season'])
        e = str(i['episode'])

        rem = {"_id": id + ':' + s + ':' + e}
        seriestream.remove(rem)


def addMovie(id, stream, db_url):
    client = MongoClient(db_url)
    removeMovie(id, db_url)

    meta = Metadata()
    moviecat = movieCatalog(client)
    moviestream = movieStreams(client)

    x, y = meta.get_movie(id, stream)
    moviecat.add(x)

    for i in y:
        moviestream.add(i)


def addSeries(id, stream, db_url):
    client = MongoClient(db_url)
    removeSeries(id, db_url)

    meta = Metadata()
    seriescat = seriesCatalog(client)
    seriestream = seriesStreams(client)

    x, y = meta.get_series(id, stream)
    seriescat.add(x)
    for i in y:
        seriestream.add(i)
