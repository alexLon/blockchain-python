import sys
import json
sys.path.append('/dev/blockchain-python')

from backend.core.block import Block
from backend.core.blockheader import BlockHeader
from backend.util.util import hash256
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
        self.chain = []
        self.genenis_block()

    def genenis_block(self):
        BlockHeight = 0
        prevBlockHash = ZERO_HASH
        self.add_block(BlockHeight, prevBlockHash)

    def add_block(self, BlockHeight, prevBlockHash):
        timestamp = int(time.time())
        transaction = f"Alex sent {BlockHeight} BTC to Marie"
        merkleRoot = hash256(transaction.encode()).hex()
        bits = 'ffff0001f'
        blockHeader = BlockHeader(VERSION, prevBlockHash, merkleRoot, timestamp, bits)
        blockHeader.mine()
        self.chain.append(Block(BlockHeight, 1, blockHeader.__dict__, 1, transaction).__dict__)
        print(json.dumps(self.chain, indent=4))

    def main(self):
        while True:
            lastBlock = self.chain[::-1]
            BlockHeight = lastBlock[0]["height"] + 1
            prevBlockHash = lastBlock[0]["blockHeader"]["blockHash"]
            self.add_block(BlockHeight, prevBlockHash)


if __name__ == "__main__":
    blockChain = BlockChain()
    blockChain.main()

