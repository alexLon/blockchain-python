import os
from backend.core.script import Script
from backend.util.util import int_to_little_endian, bytes_needed, decode_base58, little_endian_to_int
from dotenv import load_dotenv


"""
This module contains different classes related to transactions in our blockchain network
Classes : - Transaction (Tx),
          - Transaction Ins (TxIns),
          - Transaction Outs (TxOuts)
"""

load_dotenv()  # take environment variables from .env.

ZERO_HASH = b'\0' * 32
REWARD = 50

privateKey = os.getenv('PRIVATE_KEY')
minerAddress = os.getenv('MINER_ADDRESS')

class CoinbaseTx:
    def __init__(self, blockHeight):
        self.blockHeightLittleEndian = int_to_little_endian(blockHeight, bytes_needed(blockHeight))

    def CoinbaseTransaction(self):
        prevTx = ZERO_HASH
        prevIndex = 0xffffffff   

        txIns = []
        txIns.append(TxIn(prevTx, prevIndex))
        txIns[0].scriptSig.cmds.append(self.blockHeightLittleEndian)

        txOuts = []
        targetAmount = REWARD * 1000000
        targeth160 = decode_base58(minerAddress)
        targetScript = Script.p2pkh_script(targeth160)
        txOuts.append(TxOut(amount = targetAmount, scriptPublicKey = targetScript))

        return Tx(1, txIns, txOuts, 0)


class Tx:
    def __init__(self, version, txIns, txOuts, lockTime):
        self.version = version
        self.txIns = txIns
        self.txOuts = txOuts
        self.lockTime = lockTime

    def is_coinbase(self):
        """ 
        checks if there is exactly 1 input
        grabs first input and check if the prev_tx is b'x00' * 32
        check that the first input prev_index is 0xfffffff
        """
        if len(self.txIns) != 1:
            return False
        
        first_input = self.txIns[0]

        if first_input.prevTx != b'\x00' * 32:
            return False
        
        if first_input.prev_index != 0xffffffff:
            return False
        
        return True
    
    def to_dict(self):
        """
        This method will convert the coinbase transaction
        1. converts prevTx hash from bytes to hex
        2. converts blockHeight to hex
        """
        if self.is_coinbase():
            self.txIns[0].prev_tx = self.txIns[0].prev_tx.hex()
            self.txIns[0].scriptSig.cmd[0] = little_endian_to_int(self.txIns[0].scriptSig.cmds[0])
            self.txIns[0].scriptSig = self.txIns[0].scriptSig.__dict__
        
        self.txIns[0] = self.txIns[0].__dict__
        """
        Convert transaction output to dict
        1. if numbers, don't do anything
        2. if values in bytes, convert to hex
        3. loop through all the txOuts objects and convert to dict
        """
        self.txOuts[0].scriptPublicKey.cmds[2] = self.txOuts[0].scriptPublicKey.cmds[2].hex()
        self.txOuts[0].scriptPublicKey = self.txOuts[0].scriptPublicKey.__dict__
        self.txOuts[0] = self.txOuts[0].__dict__

        return self.__dict__


class TxIn:
    def __init__(self, prevTx, prevIndex, scriptSig = None, sequence = 0xffffffff):
        self.prevTx = prevTx
        self.prevIndex = prevIndex
        self.sequence = sequence
        if scriptSig is None:
            self.scriptSig = Script()
        else:
            self.scriptSig = scriptSig


class TxOut:
    def __init__(self, amount, scriptPublicKey):
        self.amount = amount
        self.scriptPublicKey = scriptPublicKey
