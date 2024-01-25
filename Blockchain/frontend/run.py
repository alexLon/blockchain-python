from flask import Flask, render_template, request
from Blockchain.client.sendBTC import SendBTC
from Blockchain.backend.core.transaction import Tx
from Blockchain.backend.core.database.database import BlockChainDB
import time 

timestamp = time.time()
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("home.html")

@app.route('/block')
def block():
    return "<h1>Block</h1>"

@app.route('/transactions')
def transactions():
    return "<h1>Transactions</h1>"

@app.route('/mempool')
def mempool():
    return "<h1>Mempool</h1>"

@app.route("/search")
def search():
    return "<h1>search</h1>"

""" Read data from the blockchain """
def read_database():
    errorFlag = False
    while errorFlag:
        try:
            blockchain = BlockChainDB()
            blocks = blockchain.read()
            errorFlag = False
        except:
            errorFlag = True
            print("Error reading database")
    return blocks

@app.route("/block")
def block():
    blocks = read_database()
    return render_template('block.html', blocks=blocks)


@app.route('/wallet', methods = ['GET', 'POST'])
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



