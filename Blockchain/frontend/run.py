from flask import Flask, render_template, request
from Blockchain.client.sendBTC import SendBTC

app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def wallet():
    message = ''
    if request.method == 'POST':
        fromAddress = request.form.get('fromAddress')
        toAddress = request.form.get('toAddress')
        amount = request.form.get('Amount', type = int)
        sendCoin = SendBTC(fromAddress, toAddress, amount, UTXOS)
        if not sendCoin.prepare_transaction():
            message = 'Insufficient balance.'
    return render_template('wallet.html', message = message)

def main(utxos):
    global UTXOS 
    UTXOS = utxos
    app.run()



