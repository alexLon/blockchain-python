from backend.util.util import hash256


class BlockHeader:
    """
    Blockheader Class
    """
    def __init__(self, version, prevBlockHash, merkleRoot, timestamp, bits):
        self.version = version
        self.prevBlockHash = prevBlockHash
        self.merkleRoot = merkleRoot
        self.timestamp = timestamp
        self.bits = bits
        self.nonce = 0
        self.blockHash = ''

    def mine(self):
        while (self.blockHash[0:4] != '0000'):
            self.blockHash = hash256((str(self.version) + str(self.prevBlockHash) + str(self.merkleRoot) + str(self.timestamp) + str(self.bits) + str(self.nonce)).encode()).hex()
            self.nonce += 1
            print(f"Mining Started: {self.nonce}", end="\r")
    