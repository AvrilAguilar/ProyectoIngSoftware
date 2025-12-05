# Base de datos falsa para pruebas (NO usa Mongo real)

class FakeCollection:
    def __init__(self):
        self.data = []
    
    async def insert_one(self, doc):
        doc["_id"] = str(len(self.data) + 1)
        self.data.append(doc)
        return type("obj", (), {"inserted_id": doc["_id"]})

    def find(self, query):
        # Regresar elementos que coincidan con la llave
        class Cursor:
            def __init__(self, data):
                self._data = data
            
            async def to_list(self, length=None):
                return self._data
            
            async def __aiter__(self):
                for item in self._data:
                    yield item
        
        filtered = [
            d for d in self.data
            if all(d.get(k) == v for k, v in query.items())
        ]
        
        return Cursor(filtered)

    async def find_one(self, query):
        for doc in self.data:
            if all(doc.get(k) == v for k, v in query.items()):
                return doc
        return None


books_collection_test = FakeCollection()
reviews_collection_test = FakeCollection()
