import sys
sys.path.append('/dev/blockchain-python')

from backend.core.block import Block
from backend.core.blockheader import BlockHeader
from backend.util.util import hash256
import time

ZERO_HASH = '0' * 64
VERSION = 1


class BlockChain:
    
    def __init__(self):
        self.chain = []
        self.genenis_block()

    def genenis_block(self):
        BlockHeight = 0
        prevBlockHash = ZERO_HASH
        self.add_block(BlockHeight, prevBlockHash)

    def add_block(self, BlockHeight, prevBlockHash):
        timestamp = int(time.time())
        transaction = f"Alex sent {BlockHeight} bitcoins to Marie"
        merkleRoot = hash256(transaction.encode()).hex()
        bits = 'ffff0001f'
        blockheader = BlockHeader(VERSION, prevBlockHash, merkleRoot, timestamp, bits)
        blockheader.mine()
        self.chain.append(Block(BlockHeight, 1, blockheader, 1, transaction))
        print(self.chain)

if __name__ == "__main__":
    blockchain = BlockChain()

