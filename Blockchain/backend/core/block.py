

class Block:
    """
    Block class that stores transactions as well as other information such as blocksize, 
    blockheader (another class), and the number of transactions.
    """
    def __init__(self, height, blockSize, blockHeader, txCount, txs):
        self.height = height
        self.blockSize = blockSize
        self.blockHeader = blockHeader
        self.txCount = txCount
        self.txs = txs