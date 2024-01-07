import os
import json

"""
This file controls the blockchain, meaning reading and writing to the database. 
The DB is very simple and consists of a json file. All blocks get added to the DB.
Json format is used to stored the data
"""

class BaseDB:
    """
    This is the base class that defines where the data is stored from a defined path and file.
    It also handles reads and writes
    """
    def __init__(self):
        self.basePath = 'data'
        self.filePath = './'.join((self.basePath, self.fileName))

    def read(self):
        if not os.path.exists(self.filePath):
            print(f"file {self.filePath} not available")
            return False
        
        with open(self.filePath, "r") as file:
            raw = file.readline()
        
        if len(raw) > 0:
            data = json.loads(raw)
        else:
            data = []
        return data

    def write(self, item):
        data = self.read()
        if data:
            data = data + item
        else:
            data = item

        with open(self.filePath, "w+") as file:
            file.write(json.dumps(data))


class BlockChainDB(BaseDB):
    """
    This class is inherited from BaseDB
    It starts the blockchain database and has a function to read the latest block (this will be used in other modules)
    """
    def __init__(self):
        self.fileName = 'BTC blockchain'
        super().__init__()

    def last_block(self):
        data = self.read()
        
        if data:
            return data[-1]