

class Block:
    """
    Block container storing transactions
    """
    def __init__(self, Height, Blocksize, Blockheader, TxCount, Txs):
        self.Height = Height
        self.Blocksize = Blocksize
        self.Blockheader = Blockheader
        self.Txcount = TxCount
        self.Txs = Txs