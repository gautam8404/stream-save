from pymongo.collection import Collection


class baseDB:
    def __init__(self, collection: Collection):
        self.col = collection

    def find(self, data):
        return self.col.find_one(data)

    def full(self):
        return list(self.col.find())

    def add(self, data):
        try:
            self.col.insert_one(data)
        except:
            pass

    def remove(self, data):
        self.col.delete_one(data)
