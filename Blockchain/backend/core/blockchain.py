import sys
sys.path.append('/dev/blockchain-python/')

from Blockchain.backend.core.block import Block
from Blockchain.backend.core.blockheader import BlockHeader
from Blockchain.backend.core.database.database import BlockChainDB
from Blockchain.backend.util.util import hash256
from Blockchain.backend.core.transaction import CoinbaseTx
from multiprocessing import Process, Manager
from Blockchain.frontend.run import main

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
    
    def __init__(self, utxos):
        self.utxos = utxos

    def write_on_disk(self, block):
        blockChainDB = BlockChainDB()
        blockChainDB.write(block)
    
    def fetch_last_block(self):
        blockChainDB = BlockChainDB()
        return blockChainDB.last_block()
    
    """ Keep track of all the unspent transaction in cache memory for fast retrieval """
    def store_utxos_in_cache(self, transaction):
        self.utxos[transaction.txId] = transaction

    def genenis_block(self):
        BlockHeight = 0
        prevBlockHash = ZERO_HASH
        self.add_block(BlockHeight, prevBlockHash)

    def add_block(self, BlockHeight, prevBlockHash):
        timestamp = int(time.time())
        coinbaseInstance = CoinbaseTx(BlockHeight)
        coinbaseTx = coinbaseInstance.CoinbaseTransaction()
        merkleRoot = coinbaseTx.txId
        bits = 'ffff0001f'
        blockHeader = BlockHeader(VERSION, prevBlockHash, merkleRoot, timestamp, bits)
        blockHeader.mine()

        self.store_utxos_in_cache(coinbaseTx)
        
        print(f"Blocked mined: {BlockHeight} - Nonce: {blockHeader.nonce}")
        self.write_on_disk([Block(BlockHeight, 1, blockHeader.__dict__, 1, coinbaseTx.to_dict()).__dict__])
        

    def main(self):
        lastBlock = self.fetch_last_block()
        if lastBlock is None:
            self.genenis_block()
        while True:
            lastBlock = self.fetch_last_block()
            BlockHeight = lastBlock["height"] + 1
            prevBlockHash = lastBlock["blockHeader"]["blockHash"]
            self.add_block(BlockHeight, prevBlockHash)


if __name__ == "__main__":
    with Manager() as manager:
        utxos = manager.dict()

        webapp = Process(target = main, args = (utxos,))
        webapp.start()

        blockChain = BlockChain(utxos)
        blockChain.main()

