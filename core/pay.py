
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
            '''
            for i in unprocessed_pay:              
                #tx = crypto.sign(i[1], str(i[2]), i[3], passphrase, secondphrase)
                # TEST SIGNED OBJECT
                tx = "dummy"
                signed_tx.append(tx)
            '''
            test_tx = {"type":0,
                       "amount":100000000000,
                       "fee":10000000,
                       "recipientId":"DS2YQzkSCW1wbTjbfFGVPzmgUe1tNFQstN",
                       "timestamp":39108789,
                       "asset":{},
                       "vendorField":"core2test",
                       "senderPublicKey":"030dee498e6ff341ec3a51df821d5d39d5ac19142ac27eba9fd1f13b6e30dc1528",
                       "signature":"304402203b39b925179858ac24ce58d10ff4ca70f756a0cf48db9e69638d08eb87b977f6022015dcacbace1ed2e13d0be497147585300467ce83f57d577e67755395666e7c85",
                       "id":"ca8dcc428804b745422915f5e6ab41020b951c56e331ac3c397932255e474622"}

            signed_tx.append(test_tx)
            
            broadcast(signed_tx, ark)
            snekdb.processStagedPayment(unique_rowid)

            # payment run complete
            print('Payment Run Completed!')
            #sleep 5 minutes between 50tx blasts
            time.sleep(300)
        
        else:
            time.sleep(300)
