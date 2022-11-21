from pymongo.collection import Collection
from pymongo import MongoClient
from .base.basedb import baseDB


class movieCatalog(baseDB):
    def __init__(self, client: MongoClient):
        super(movieCatalog, self).__init__(Collection(client['streamsave-catalog'], "movie"))


class movieStreams(baseDB):
    def __init__(self, client: MongoClient):
        super(movieStreams, self).__init__(Collection(client['streamsave-streams'], "movie"))