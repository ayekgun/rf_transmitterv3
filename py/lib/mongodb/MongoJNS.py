from pymongo import MongoClient
import sys
import os

sys.path.append(os.path.abspath("py/conf"))
from config import *

class mongo:
    def GetRetryTransmitter(self,trxid):
        client = MongoClient(mongo_conn)
        db = client['scheduler_retry']
        collection_name = "retry_transmitter"
        collection = db.get_collection(collection_name)
        document = collection.find_one({'trx_id': trxid}, {'_id': 0})
        client.close()
        return document