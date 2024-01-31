from flask import Flask, render_template, request, redirect, url_for
from Blockchain.client.sendBTC import SendBTC
from Blockchain.backend.core.transaction import Tx
from Blockchain.backend.core.database.database import BlockChainDB
from Blockchain.backend.util.util import encode_base58
from hashlib import sha256
import time 

timestamp = time.time()
app = Flask(__name__)
main_prefix = b'\x00'
global memoryPool
memoryPool = {}

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/transactions/<txid>")
@app.route("/transactions")
def transactions(txid = None):
    if txid:
        return redirect(url_for('txDetail', txid = txid))
    else:
        errorFlag = True
        while errorFlag:
            try:
                allTxs = dict(UTXOS)
                errorFlag = False
                return render_template('transactions.html', allTransactions=allTxs, refreshtime=10)
            except:
                errorFlag = True
                return render_template('transactions.html', allTransactions={}, refreshtime=10)

@app.route("/tx/<txid>")
def txDetail(txid):
    blocks = read_database()
    for block in blocks:
        for tx in block['txs']:
            if tx['txId'] == txid:
                return render_template('txDetail.html', tx=tx, block=block, encode_base58=encode_base58,
                                       bytes=bytes, sha256=sha256, main_prefix=main_prefix)

@app.route("/mempool")
def mempool():
    try:
        blocks = read_database()
        errorFlag = True
        while errorFlag:
            try:
                mempoolTxs = dict(MEMPOOL)
                print(f"\nmempoolTxs VARIABLE {mempoolTxs}")
                errorFlag = False
            except:
                errorFlag = True
                #print("Error reading database")
        
        """ if txId is not in the original list then remove it from the mempool"""
        for txId in memoryPool:
            if txId not in mempoolTxs:
                del memoryPool[txId]

        """ Add the new tx to the mempool if it is not already there"""
        for txId in mempoolTxs:
            amount = 0
            txObj = mempoolTxs[txId]
            matchFound = False

            """ Total amount """
            for txIn in txObj.txIns:
                for block in blocks:
                    for tx in block['txs']:
                        if tx['txId'] == txIn.prevTx.hex():
                            amount += tx['txOuts'][txIn.prevIndex]['amount']
                            matchFound = True
                            break
                    if matchFound:
                        matchFound = False
                        break
            
            memoryPool[txObj.txId] = [txObj.to_dict(), amount/100000000, txIn.prevIndex]
        return render_template("mempool.html",txs=memoryPool,refreshtime=2)
    except Exception as e:
        return render_template("mempool.html",txs=memoryPool,refreshtime=2)

@app.route("/memTx/<txId>")
def memTxDetails(txId):
    if txId in memoryPool:
        tx = memoryPool.get(txId)[0]
        return render_template('txDetail.html', tx=tx, refreshtime=2,
                               encode_base58=encode_base58, bytes=bytes, sha256=sha256, main_prefix=main_prefix,
                               Unconfirmed=True)
    else:
        return redirect(url_for('transactions', txid=txId))


@app.route("/search")
def search():
    return "<h1>search</h1>"

""" Read data from the blockchain """
def read_database():
    errorFlag = True
    while errorFlag:
        try:
            blockchain = BlockChainDB()
            blocks = blockchain.read()
            errorFlag = False
        except:
            errorFlag = True
            print("Error reading database")
    return blocks

@app.route('/block')
def block():
    if request.args.get('blockHeader'):
            return redirect(url_for('show_block', blockHeader=request.args.get('blockHeader')))
    else:
        blocks = read_database()
        return render_template('block.html', blocks=blocks, refreshtime = 10)

@app.route("/block/<blockHeader>")
def show_block(blockHeader):
    blocks = read_database()
    for block in blocks:
        if block['blockHeader']['blockHash'] == blockHeader:
            return render_template('blockDetails.html', block = block, main_prefix = main_prefix, 
                                   encode_base58 = encode_base58, bytes = bytes, sha256 = sha256)

@app.route("/address")
def address():
    return "<h1> Address page </h1>"

@app.route("/wallet", methods = ['GET', 'POST'])
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
                print(f"\n +++++++++++++++++++++++   test    +++++++++++++++++++++++++ Length:" + str(len(MEMPOOL)))
                message = 'Transaction added in memory pool'

    return render_template('wallet.html', message = message)

def main(utxos, memPool):
    global UTXOS
    global MEMPOOL
    UTXOS = utxos
    MEMPOOL = memPool
    app.run()



