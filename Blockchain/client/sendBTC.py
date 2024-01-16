import base58
from Blockchain.backend.util.util import decode_base58
from Blockchain.backend.core.script import Script
from Blockchain.backend.core.transaction import Tx, TxIn, TxOut
from Blockchain.backend.core.database.database import AccountDB
from Blockchain.backend.core.EllipticCurve.EllipticCurve import PrivateKey
import time
"""
write doc here!
"""

class SendBTC:
    
    def __init__(self, fromAccount, toAccount, amount, UTXOS):
        self.COIN = 1000000 # satoshi
        self.fromPublicAddress = fromAccount
        self.toAccount = toAccount
        self.amount = amount * self.COIN
        self.utxos = UTXOS

    def script_pub_key(self, publicAddress):
        h160 = decode_base58(publicAddress)
        scriptPubKey = Script().p2pkh_script(h160)
        return scriptPubKey
    
    def get_private_key(self):
        allAccounts = AccountDB().read()
        for account in allAccounts:
            if account['publicAddress'] == self.fromPublicAddress:
                return account['privateKey']
        return False

    def prepare_tx_in(self):
        txIns = []
        self.total = 0

        """ Convert Public Address into Public Hash to find txOuts that are locked to this address"""
        self.fromAddressScriptPubKey = self.script_pub_key(self.fromPublicAddress)
        self.fromPubKeyHash = self.fromAddressScriptPubKey.cmds[2]

        # define new dict to track unspent transactions output
        newUtxos = {}

        # loop until any utxos are available
        try:
            while len(newUtxos) < 1:
                newUtxos = dict(self.utxos)
                time.sleep(2)
        except Exception as e:
            print(f'Error in converting the managed Dict to Normal Dict')
        
        # in order to send a transaction, we need to check the total UTXOS for this specific address
        for txByte in newUtxos:
            if self.total < self.amount:
                txObj = newUtxos[txByte]
                # iterating through all UTXOS
                for index, txOut in enumerate(txObj.txOuts):
                    # when the public key hash matches those in the block, creating txIn object and incrementing total
                    if txOut.scriptPublicKey.cmds[2] == self.fromPubKeyHash:
                        self.total += txOut.amount
                        prevTx = bytes.fromhex(txByte)
                        txIns.append(TxIn(prevTx, index))
            else:
                break
        
        # in the scenario where the person has insufficient balance in their account
        self.isBalancedEnough = True
        if self.total < self.amount:
            self.isBalancedEnough = False

        return txIns

    def prepare_tx_out(self):
        txOuts = []
        toScriptPubKey = self.script_pub_key(self.toAccount)
        txOuts.append(TxOut(self.amount, toScriptPubKey))
        """ Calculate fee"""
        self.fee = self.COIN
        self.changeAmount = self.total - self.amount - self.fee 

        txOuts.append(TxOut(self.changeAmount, self.fromAddressScriptPubKey))

        return txOuts
    
    def sign_transaction(self):
        secret = self.get_private_key()
        priv = PrivateKey(secret= secret)

        for i, input in enumerate(self.txIns):
            self.txObj.sign_input(i, priv, self.fromAddressScriptPubKey)
        
        return True

    def prepare_transaction(self):
        self.txIns = self.prepare_tx_in()
        
        if self.isBalancedEnough:
            self.txOuts = self.prepare_tx_out()
            self.txObj = Tx(1, self.txIns, self.txOuts, 0)
            self.txObj.txId = self.txObj.id()
            self.sign_transaction()
            return self.txObj
        return False


