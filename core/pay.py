#!/usr/bin/env python
import time
import os
from dotenv import load_dotenv
from crypto.configuration.network import set_custom_network
from crypto.transactions.builder.transfer import Transfer
from config.config import Config
from network.network import Network
from util.sql import SnekDB
from util.dynamic import Dynamic
from util.write import JsWrite
from util.util import Util
from datetime import datetime


def broadcast(tx):
    
    # broadcast to relay
    try:
        transaction = client.transactions.create(tx)
        print(transaction)
        records = [[j['recipientId'], j['amount'], j['id']] for j in tx]
        time.sleep(1)
    except BaseException as e:
        # error
        print("Something went wrong", e)
        quit()

    snekdb.storeTransactions(records)
    
    return transaction['data']['accept']


def build_network():
    e = network.epoch
    t = [int(i) for i in e]
    epoch = datetime(t[0], t[1], t[2], t[3], t[4], t[5])
    set_custom_network(epoch, network.version, network.wif)


def build_transfer_transaction(address, amount, vendor, fee, pp, sp, nonce):
    if sp == 'None':
        sp = None
    
    print(address)
    print(amount)
    print(vendor)
    print(fee)
    print(pp)
    print(sp)
    print(nonce)
    quit()
  
    
    js.write(network.version, pp, sp, data.public_key, address, nonce, vendor, amount, fee)
    transaction_dict = js.run()
    print(transaction_dict)
    quit()
    js.delete()
    return transaction_dict
    
    # python3 crypto version when ready
    '''
    version = 2
    transaction = Transfer(
        recipientId=address,
        amount=amount,
        vendorField=vendor,
        fee=fee,
        version = version,
        nonce = nonce,
        network = int(network.version)
    )
    transaction.sign(pp)
    
    if sp == 'None':
        sp = None
    if sp is not None:
        transaction.second_sign(sp)

    transaction_dict = transaction.to_dict()
    return transaction_dict

    '''
def get_nonce():
    n = client.wallets.get(data.delegate)
    return int(n['data']['nonce'])


def non_accept_check(c, a):
    removal_check = []
    for k,v in c.items():
        if k not in a:
            removal_check.append(v)
            #print("TransactionID not accepted: ", k)
            snekdb.deleteTransactionRecord(k)
        else:
            #print("TransactionID accepted: ", k)
            pass
    
    return removal_check
            

def share():
    while True:
        signed_tx = []

        # get max blast tx and check for unprocessed payments
        max_tx = os.getenv("CORE_TRANSACTION_POOL_MAX_PER_REQUEST")
        if max_tx == None:
            unprocessed_pay = snekdb.stagedArkPayment().fetchall()
        else:
            unprocessed_pay = snekdb.stagedArkPayment(int(max_tx)).fetchall()

        # query not empty means unprocessed blocks
        if unprocessed_pay:
            unique_rowid = [y[0] for y in unprocessed_pay]
            check = {}
            
            temp_nonce = get_nonce()+1
            for i in unprocessed_pay:
                dynamic = Dynamic(data.database_user, i[3], data.network, network.api_port)
                transaction_fee = dynamic.get_dynamic_fee()

                # fixed processing
                if i[1] in data.fixed.keys():
                    fixed_amt = int(data.fixed[i[1]] * data.atomic)
                    tx = build_transfer_transaction(i[1], (fixed_amt), i[3], transaction_fee, data.passphrase, data.secondphrase, str(temp_nonce))
                else:           
                    tx = build_transfer_transaction(i[1], (i[2]), i[3], transaction_fee, data.passphrase, data.secondphrase, str(temp_nonce))
                check[tx['id']] = i[0]
                signed_tx.append(tx)
                temp_nonce+=1
                time.sleep(0.25)
                     
            accepted = broadcast(signed_tx)
            for_removal = non_accept_check(check, accepted)
            
            # remove non-accepted transactions from being marked as completed
            if len(for_removal) > 0:
                for i in for_removal:
                    print("Removing RowId: ", i)
                    unique_rowid.remove(i)
                    
            snekdb.processStagedPayment(unique_rowid)

            # payment run complete
            print('Payment Run Completed!')
            # sleep 10 minutes between tx blasts
            time.sleep(600)

        else:
            time.sleep(150)


if __name__ == '__main__':
   
    data = Config()
    js = JsWrite()
    network = Network(data.network)
    u = Util(data.network)
    snekdb = SnekDB(data.database_user, data.network, data.delegate)
    client = u.get_client(network.api_port)
    build_network()
    
    #get dot path for load_env and load
    dot = u.core+'/.env'
    load_dotenv(dot)
    share()
