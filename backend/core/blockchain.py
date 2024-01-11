import sys
sys.path.append('/dev/blockchain-python')

from backend.core.block import Block
from backend.core.blockheader import BlockHeader
from backend.core.database.database import BlockChainDB
from backend.util.util import hash256
from backend.core.transaction import CoinbaseTx

import time

ZERO_HASH = '0' * 64
VERSION = 1


class BlockChain:
    """
    Blockchain class is the actual chain of blocks mined and validated. 
    These blocks contain different transactions happening in the network.

    When the class is first instanciated, the genesis block is also created.
    Then after we loop through to continuously mine new blocks (respecting the puzzle complexity defined in the block class)
    and we add the newly solved block to the existing chain.
    """
    
    def __init__(self):
        self.genenis_block()

    def write_on_disk(self, block):
        blockChainDB = BlockChainDB()
        blockChainDB.write(block)
    
    def fetch_last_block(self):
        blockChainDB = BlockChainDB()
        return blockChainDB.last_block()

    def genenis_block(self):
        BlockHeight = 0
        prevBlockHash = ZERO_HASH
        self.add_block(BlockHeight, prevBlockHash)

    def add_block(self, BlockHeight, prevBlockHash):
        timestamp = int(time.time())
        coinbaseInstance = CoinbaseTx(BlockHeight)
        coinbaseTx = coinbaseInstance.CoinbaseTransaction()
        merkleRoot = ''
        bits = 'ffff0001f'
        blockHeader = BlockHeader(VERSION, prevBlockHash, merkleRoot, timestamp, bits)
        blockHeader.mine()
        self.write_on_disk([Block(BlockHeight, 1, blockHeader.__dict__, 1, coinbaseTx).__dict__])
        

    def main(self):
        while True:
            lastBlock = self.fetch_last_block()
            BlockHeight = lastBlock["height"] + 1
            prevBlockHash = lastBlock["blockHeader"]["blockHash"]
            self.add_block(BlockHeight, prevBlockHash)


if __name__ == "__main__":
    blockChain = BlockChain()
    blockChain.main()

