import sys
sys.path.append('/dev/blockchain-python/')

from Blockchain.backend.core.block import Block
from Blockchain.backend.core.blockheader import BlockHeader
from Blockchain.backend.core.database.database import BlockChainDB
from Blockchain.backend.util.util import hash256, merkle_root, target_to_bits
from Blockchain.backend.core.transaction import CoinbaseTx
from multiprocessing import Process, Manager
from Blockchain.frontend.run import main

import time

ZERO_HASH = '0' * 64
VERSION = 1
INITIAL_TARGET = 0x0000FFFF00000000000000000000000000000000000000000000000000000000


class BlockChain:
    """
    Blockchain class is the actual chain of blocks mined and validated. 
    These blocks contain different transactions happening in the network.

    When the class is first instanciated, the genesis block is also created.
    Then after we loop through to continuously mine new blocks (respecting the puzzle complexity defined in the block class)
    and we add the newly solved block to the existing chain.
    """
    
    def __init__(self, utxos, memPool):
        self.utxos = utxos
        self.memPool = memPool
        self.currentTarget = INITIAL_TARGET
        self.bits = target_to_bits(INITIAL_TARGET)

    def write_on_disk(self, block):
        blockChainDB = BlockChainDB()
        blockChainDB.write(block)
    
    def fetch_last_block(self):
        blockChainDB = BlockChainDB()
        return blockChainDB.last_block()
    
    """ Keep track of all the unspent transaction in cache memory for fast retrieval """
    def store_utxos_in_cache(self):
        for tx in self.addTransactionsInBlock:
            print(f"Transaction added {tx.txId} ")
            self.utxos[tx.txId] = tx

    def remove_spent_transactions(self):
        for txId_index in self.removeSpentTransactions:
            if txId_index[0].hex() in self.utxos:
                if len(self.utxos[txId_index[0].hex()].txOuts) < 2:
                    print(f"Spent transaction removed  {txId_index[0].hex()} ")
                    del self.utxos[txId_index[0].hex()]
                else:
                    prevTx = self.utxos[txId_index[0].hex()]
                    self.utxos[txId_index[0].hex()] = prevTx.txOuts.pop(txId_index[1])


    """ Read transaction from memory pool """
    def read_transaction_from_memorypool(self):
        self.blockSize = 80
        self.txIds = []
        self.addTransactionsInBlock = []
        self.removeSpentTransactions = []

        
        for tx in self.memPool:
            self.txIds.append(bytes.fromhex(tx))
            self.addTransactionsInBlock.append(self.memPool[tx])
            self.blockSize += len(self.memPool[tx].serialize())

            for spent in self.memPool[tx].txIns:
                self.removeSpentTransactions.append([spent.prevTx, spent.prevIndex])

    def remove_transactions_from_memorypool(self):
        for tx in self.txIds:
            if tx.hex() in self.memPool:
                del self.memPool[tx.hex()]   
    
    def genenis_block(self):
        BlockHeight = 0
        prevBlockHash = ZERO_HASH
        self.add_block(BlockHeight, prevBlockHash)

    def convert_to_json(self):
        self.txJson = []

        for tx in self.addTransactionsInBlock:
            self.txJson.append(tx.to_dict())

    def calculate_fee(self):
        self.inputAmount = 0
        self.outputAmount = 0

        """ calculate input amount """
        for txId_index in self.removeSpentTransactions:
            if txId_index[0].hex() in self.utxos:
                self.inputAmount += self.utxos[txId_index[0].hex()].txOuts[txId_index[1]].amount
        
        """ calculate output amount """
        for tx in self.addTransactionsInBlock:
            for txOut in tx.txOuts:
                self.outputAmount += txOut.amount
            
        self.fee = self.inputAmount - self.outputAmount

    
    def add_block(self, BlockHeight, prevBlockHash):

        self.read_transaction_from_memorypool()
        self.calculate_fee()
        timestamp = int(time.time())
        coinbaseInstance = CoinbaseTx(BlockHeight)
        coinbaseTx = coinbaseInstance.CoinbaseTransaction()
        self.blockSize += len(coinbaseTx.serialize())

        coinbaseTx.txOuts[0].amount = coinbaseTx.txOuts[0].amount + self.fee

        self.txIds.insert(0, bytes.fromhex(coinbaseTx.txId))
        self.addTransactionsInBlock.insert(0, coinbaseTx)

        merkleRoot = merkle_root(self.txIds)[::-1].hex()
        blockHeader = BlockHeader(VERSION, prevBlockHash, merkleRoot, timestamp, self.bits)
        blockHeader.mine(self.currentTarget)
        self.remove_spent_transactions()
        self.remove_transactions_from_memorypool()
        self.store_utxos_in_cache()
        self.convert_to_json()
        
        print(f"Blocked mined: {BlockHeight} - Nonce: {blockHeader.nonce}")
        self.write_on_disk([Block(BlockHeight, self.blockSize, blockHeader.__dict__, 1, self.txJson).__dict__])
        

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
        memPool = manager.dict()

        webapp = Process(target = main, args = (utxos, memPool))
        webapp.start()

        blockChain = BlockChain(utxos, memPool)
        blockChain.main()

