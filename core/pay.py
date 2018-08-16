#!/usr/bin/env python
from crypto.conf import use_network
from crypto.constants import TRANSACTION_TRANSFER
from crypto.transactions.builder.transfer import TransferBuilder
from tbw import parse_config
from snek.snek import SnekDB
from ark import ArkClient
import time

def get_network(d, n, ip="localhost"):
### NEED TO UPDATE FOR API2
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
        transaction = ark.transactions.create(tx)
        records = [[j['recipientId'],j['amount'],j['id']] for j in tx]
        time.sleep(1)
    except BaseException:
        # fall back to delegate node to grab data needed
        bark = get_network(data, network, data['delegate_ip'])
        transaction = bark.transactions.create(tx)
        records = [[j['recipientId'],j['amount'],j['id']] for j in tx]
        time.sleep(1)
    
    snekdb.storeTransactions(records)

def build_transfer_transaction():
    """Test if a transfer transaction gets built
    """
    use_network(data['network'])
    transaction = TransferBuilder(
        recipientId='DMzBk3g7ThVQPYmpYDTHBHiqYuTtZ9WdM3',
        amount=1000000,
        vendorField='This is a transaction from Python'.encode(),
    )
    transaction.sign(passphrase.encode())
    # transaction.second_sign(secondphrase.encode())
    transaction_dict = transaction.to_dict()
    transaction.verify()  # if no exception is raised, it means the transaction is valid
    # transaction.second_verify()

    return transaction_dict
if __name__ == '__main__':
   
    data, network = parse_config()
    snekdb = SnekDB(data['dbusername'])
    
    # Get the passphrase from config.json
    passphrase = data['passphrase']
    # Get the second passphrase from config.json
    secondphrase = data['secondphrase']
    if secondphrase == 'None':
        secondphrase = None
    
    tx = build_transfer_transaction()
    print(tx)
    client = ArkClient('http://127.0.0.1:4003/api/')

    delegate = client.delegates.all()
    print(delegate)

    #post_tx = client.transport.createTransaction(tx)
    #print(post_tx)








    '''
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
            
            signed_tx.append(test_tx)
            signed_tx.append(test_tx_two)
            
            broadcast(signed_tx, ark)
            snekdb.processStagedPayment(unique_rowid)

            # payment run complete
            print('Payment Run Completed!')
            #sleep 5 minutes between 50tx blasts
            time.sleep(300)
        
        else:
            time.sleep(300)
'''