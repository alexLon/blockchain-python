from flask import Flask, render_template, request
from Blockchain.client.sendBTC import SendBTC
from Blockchain.backend.core.transaction import Tx

app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def wallet():
    message = ''
    if request.method == 'POST':
        fromAddress = request.form.get('fromAddress')
        toAddress = request.form.get('toAddress')
        amount = request.form.get('Amount', type = int)
        sendCoin = SendBTC(fromAddress, toAddress, amount, UTXOS)
        txObj = sendCoin.prepare_transaction()

        scriptPubKey = sendCoin.script_pub_key(fromAddress)
        verified = True

        if not txObj:
            message = "Invalid transaction"
        
        if isinstance(txObj, Tx):
            # Because there can be multiple transactions
            for index, tx in enumerate(txObj.txIns):
                # this will verify them
                if not txObj.verify_input(index, scriptPubKey):
                    verifed = False
            
            if verified:
                MEMPOOL[txObj.txId] = txObj
                message = 'Transaction added in memory pool'

    return render_template('wallet.html', message = message)

def main(utxos, memPool):
    global UTXOS
    global MEMPOOL
    UTXOS = utxos
    MEMPOOL = memPool
    app.run()



