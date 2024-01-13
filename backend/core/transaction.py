import os
import base58
from backend.core.script import Script
from backend.util.util import int_to_little_endian, bytes_needed, decode_base58, little_endian_to_int, int_to_little_endian, encode_varint, hash256
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
SIGHASH_ALL = 1

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
        targeth160 = base58.b58decode(minerAddress)
        targetScript = Script.p2pkh_script(targeth160)
        txOuts.append(TxOut(amount = targetAmount, scriptPublicKey = targetScript))

        coinbaseTx = Tx(1, txIns, txOuts, 0)
        coinbaseTx.txId = coinbaseTx.id()

        return coinbaseTx
    
    def sign_hash(self, inputIndex, scriptPubKey):
        s = int_to_little_endian(self.version, 4)
        s += encode_varint(len(self.txIns))

        for i, txIn in enumerate(self.txIns):
            if i == inputIndex:
                s += TxIn(txIn.prevTx, txIn.prevIndex, scriptPubKey).serialize()
            else:
                s += TxIn(txIn.prevTx, txIn.prevIndex).serialize()

        s += encode_varint(len(self.txOuts))

        for txOut in self.txOuts:
            s += txOut.serialize()
        
        s += int_to_little_endian(self.lockTime, 4)
        s += int_to_little_endian(SIGHASH_ALL, 4)

        h256 = hash256(s)
        return int.from_bytes(hash256, 'big')

    
    def sign_input(self, inputIndex, privateKey, scriptPubKey):
        z = self.sign_hash(inputIndex, scriptPubKey)
        der = privateKey.sign(z).der()
        sig = der + SIGHASH_ALL.to_bytes(1, 'big')
        sec = privateKey.point.sec()
        self.txIns[inputIndex].scriptSig = Script([sig, sec])


class Tx:
    def __init__(self, version, txIns, txOuts, lockTime):
        self.version = version
        self.txIns = txIns
        self.txOuts = txOuts
        self.lockTime = lockTime

    def id(self):
        """ Human-readable Tx id"""
        return self.hash().hex()

    def hash(self):
        """ Binary has of serialization """
        return hash256(self.serialize())[::-1]

    def serialize(self):
        result = int_to_little_endian(self.version, 4)
        result += encode_varint(len(self.txIns))

        for txIn in self.txIns:
            result += txIn.serialize()
        
        result += encode_varint(len(self.txOuts))

        for txOut in self.txOuts:
            result += txOut.serialize()
        
        result += int_to_little_endian(self.lockTime, 4)

        return result

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
        
        if first_input.prevIndex != 0xffffffff:
            return False
        
        return True
    
    def to_dict(self):
        """
        This method will convert the coinbase transaction
        1. converts prevTx hash from bytes to hex
        2. converts blockHeight to hex
        """
        if self.is_coinbase():
            self.txIns[0].prevTx = self.txIns[0].prevTx.hex()
            self.txIns[0].scriptSig.cmds[0] = little_endian_to_int(self.txIns[0].scriptSig.cmds[0])
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
        if scriptSig is None:
            self.scriptSig = Script()
        else:
            self.scriptSig = scriptSig
        self.sequence = sequence

    def serialize(self):
        result = self.prevTx[::-1]
        result += int_to_little_endian(self.prevIndex, 4)
        result += self.scriptSig.serialize()
        result += int_to_little_endian(self.sequence, 4)
        
        return result

    def to_dict(self):
        self.prevTx = self.prevTx.__dict__
        self.prevIndex = self.prevIndex.__dict__
        self.sequence = self.sequence.__dict__
        self.scriptSig = self.scriptSig.__dict__

        return self.__dict__


class TxOut:
    def __init__(self, amount, scriptPublicKey):
        self.amount = amount
        self.scriptPublicKey = scriptPublicKey
    
    def serialize(self):
        result = int_to_little_endian(self.amount, 4)
        result += self.scriptPublicKey.serialize()
        
        return result
    
    def to_dict(self):
        self.amount = self.amount.__dict__
        self.scriptPublicKey = self.scriptPublicKey.__dict__

