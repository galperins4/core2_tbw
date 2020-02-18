#!/usr/bin/env python
import time
import os
from dotenv import load_dotenv
from crypto.configuration.network import set_custom_network
from crypto.transactions.builder.transfer import Transfer
from crypto.transactions.builder.multi_payment import MultiPayment
from config.config import Config
from network.network import Network
from util.sql import SnekDB
from util.dynamic import Dynamic
from util.util import Util
from datetime import datetime


def broadcast_multi(tx):
    
    print(tx)
    quit()
    # broadcast to relay
    try:
        transaction = client.transactions.create(tx)
        print(transaction)
        for i in tx:
            id = i['id']
            records = [[j['recipientId'], j['amount'], id] for j in i['asset']['payments']]
            snekdb.storeTransactions(records)
        print(records)
        time.sleep(1)
    except BaseException as e:
        # error
        print("Something went wrong", e)
        quit()
    
    return transaction['data']['accept']


def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]


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


def build_multi_transaction(payments, nonce):
    transaction = MultiPayment(vendorField=data.voter_msg)
    transaction.set_nonce(int(nonce))

    for i in payments:
        # fixed processing
        if i[1] in data.fixed.keys():
            fixed_amt = int(data.fixed[i[1]] * data.atomic)
            transaction.add_payment(fixed_amt, i[1])
        else:
            transaction.add_payment(i[2], i[1])

    transaction.schnorr_sign(data.passphrase)
    sp = data.secondphrase
    if sp == 'None':
        sp = None
    if sp is not None:
        transaction.second_sign(sp)
    
    transaction_dict = transaction.to_dict()
    return transaction_dict


def build_transfer_transaction(address, amount, vendor, fee, pp, sp, nonce):
    # python3 crypto version    
    transaction = Transfer(
        recipientId=address,
        amount=amount,
        vendorField=vendor,
        fee=fee
    )
    transaction.set_nonce(int(nonce))
    transaction.schnorr_sign(pp)

    if sp == 'None':
        sp = None
    if sp is not None:
        transaction.second_sign(sp)

    transaction_dict = transaction.to_dict()
    return transaction_dict


def build_network():
    e = network.epoch
    t = [int(i) for i in e]
    epoch = datetime(t[0], t[1], t[2], t[3], t[4], t[5])
    set_custom_network(epoch, network.version, network.wif)


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

    
def get_nonce():
    n = client.wallets.get(data.delegate)
    return int(n['data']['nonce'])


def share_multipay():
    while True:
        signed_tx = []
        check = {}
        max_tx_limit = 20
        # set max multipayment
        #max_tx = dynamic.get_multipay_limit()
        # hard code multipay for test
        max_tx = 3
        unprocessed_pay = snekdb.stagedArkPayment(multi=data.multi).fetchall()
        multi_chunk = list(chunks(unprocessed_pay, max_tx))
        nonce = int(get_nonce() + 1)
        for i in multi_chunk:
            if len(i) > 1:
                unique_rowid = [y[0] for y in i]
                tx = build_multi_transaction(i, str(nonce))
                check[tx['id']] = unique_rowid
                signed_tx.append(tx)
                nonce += 1        
        accepted = broadcast_multi(signed_tx)
        
        # query not empty means unprocessed blocks
        if len(unprocessed_pay) != 1:
            unique_rowid = [y[0] for y in unprocessed_pay]
            check = {}
            nonce = int(get_nonce() + 1)
            tx = build_multi_transaction(unprocessed_pay, str(nonce))
            signed_tx.append(tx)
            id = signed_tx[0]['id']
            accepted = broadcast_multi(signed_tx)
            #check if multipay was accepted
            if id in accepted:
                #mark all staged payments as complete
                snekdb.processStagedPayment(unique_rowid)
            else:
                #delete all transaction records with relevant multipay txid
                snekdb.deleteTransactionRecord(id)

            # payment run complete
            print('Payment Run Completed!')
            # sleep 1 minutes between tx blasts
            time.sleep(150)
        elif len(unprocessed_pay) == 1:
            share()
        else:
            time.sleep(150)


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
    network = Network(data.network)
    u = Util(data.network)
    snekdb = SnekDB(data.database_user, data.network, data.delegate)
    client = u.get_client(network.api_port)
    build_network()
    dynamic = Dynamic(data.database_user, data.voter_msg, data.network, network.api_port)
    #get dot path for load_env and load
    dot = u.core+'/.env'
    load_dotenv(dot)
    if data.multi == "Y":
        share_multipay()
    else:
        share()
