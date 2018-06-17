
#!/usr/bin/env python
#from python_crypto import crypto FOR NEW PYTHON CLIENT CRYPTO FUNCTION

from tbw import parse_config
from snek.snek import SnekDB
from ark.ark import ArkClient
import random
import time

def get_network(d, n, ip="localhost"):

    return ArkClient(
        ip,
        n[d['network']]['port'],
        n[d['network']]['nethash'],
        n[d['network']]['version']
    )

def broadcast(tx, ark):
    records = []

    #broadcast to relay
    try:
        transaction = ark.transport().createBatchTransaction(tx)
        records = [[j['recipientId'],j['amount'],j['id']] for j in tx]
        time.sleep(1)
    except BaseException:
        # fall back to delegate node to grab data needed
        bark = get_network(data, network, data['delegate_ip'])
        transaction = bark.transport().createBatchTransaction(tx)
        records = [[j['recipientId'],j['amount'],j['id']] for j in tx]
        time.sleep(1)
    
    snekdb.storeTransactions(records)
        
if __name__ == '__main__':
   
    data, network = parse_config()
    snekdb = SnekDB(data['dbusername'])
    
    # Get the passphrase from config.json
    passphrase = data['passphrase']
    # Get the second passphrase from config.json
    secondphrase = data['secondphrase']
    if secondphrase == 'None':
        secondphrase = None
    
    ark = get_network(data, network)

    while True:
        # get peers
        signed_tx = []
        unique_rowid = []
        
        # check for unprocessed payments
        unprocessed_pay = snekdb.stagedArkPayment().fetchall()
    
        # query not empty means unprocessed blocks
        if unprocessed_pay:
            unique_rowid = [y[0] for y in unprocessed_pay]
            for i in unprocessed_pay:              
                #tx = crypto.sign(i[1], str(i[2]), i[3], passphrase, secondphrase)
                # TEST SIGNED OBJECT
                tx = "dummy"
                signed_tx.append(tx)
  
            broadcast(signed_tx, ark)
            snekdb.processStagedPayment(unique_rowid)

            # payment run complete
            print('Payment Run Completed!')
            #sleep 5 minutes between 50tx blasts
            time.sleep(300)
        
        else:
            time.sleep(300)
