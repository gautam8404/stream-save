from pymongo.collection import Collection
from pymongo import MongoClient
from .base.basedb import baseDB


class seriesCatalog(baseDB):
    def __init__(self, client: MongoClient):
        super(seriesCatalog, self).__init__(Collection(client['streamsave-catalog'], "series"))


class seriesStreams(baseDB):
    def __init__(self, client: MongoClient):
        super(seriesStreams, self).__init__(Collection(client['streamsave-streams'], "series"))
