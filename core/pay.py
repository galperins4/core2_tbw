#!/usr/bin/env python
import time
import os
from dotenv import load_dotenv
from solar_crypto.configuration.network import set_custom_network
from solar_crypto.transactions.builder.transfer import Transfer
from config.config import Config
from network.network import Network
from util.sql import SnekDB
from util.dynamic import Dynamic
from util.exchange import Exchange
from util.util import Util
from datetime import datetime


def broadcast_payment(tx):    
    # broadcast to relay
    try:
        transaction = client.transactions.create(tx)
        print(transaction)
        for i in tx:
            records = []
            id = i['id']
            records = [[j['recipientId'], j['amount'], id] for j in i['asset']['transfers']]
            snekdb.storeTransactions(records)
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


def build_transfer_transaction(payments, nonce):
    f = dynamic.get_dynamic_fee(len(payments))
    transaction = Transfer(memo=data.voter_msg)
    transaction.set_nonce(int(nonce))
    transaction.set_fee(f)

    for i in payments:
        # fixed processing
        if i[1] in data.fixed.keys():
            fixed_amt = int(data.fixed[i[1]] * data.atomic)
            transaction.add_transfer(fixed_amt, i[1])
        elif i[1] in data.convert_address:
            if data.exchange == "Y":
                index = data.convert_address.index(i[1])
                pay_in = exchange.exchange_select(index, i[1], i[2],data.provider[index])
                transaction.add_transfer(i[2], pay_in)
            else:
                transaction.add_transfer(i[2], i[1])
        else:
            transaction.add_transfer(i[2], i[1])

    transaction.sign(data.passphrase)
    sp = data.secondphrase
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

    
def get_nonce():
    n = client.wallets.get(data.delegate)
    return int(n['data']['nonce'])


def share_payment():
    signed_tx = []
    check = {}       
    
    max_tx_limit = os.getenv("CORE_TRANSACTION_POOL_MAX_PER_REQUEST")
    if max_tx_limit == None:
        max_tx_limit = 40
    else:
        max_tx_limit = int(max_tx_limit)
      
    # set max multipayment
    max_tx = dynamic.get_multipay_limit()
    unprocessed_pay = snekdb.stagedArkPayment().fetchall()

    if unprocessed_pay:
        temp_multi_chunk = list(chunks(unprocessed_pay, max_tx))
        # remove any items over max_tx_limit
        multi_chunk = temp_multi_chunk[:max_tx_limit]
        nonce = int(get_nonce() + 1)
        for i in multi_chunk:
            unique_rowid = [y[0] for y in i]
            tx = build_transfer_transaction(i, str(nonce))
            check[tx['id']] = unique_rowid
            signed_tx.append(tx)
            nonce += 1        
        accepted = broadcast_payment(signed_tx)
        #check for accepted and non-accepted transactions
        for k,v in check.items():
            if k in accepted:
                # mark all accepted records complete
                snekdb.processStagedPayment(v)
            else:
                #delete all transaction records with relevant multipay txid
                snekdb.deleteTransactionRecord(k) 

        # payment run complete
        print('Payment Run Completed!')
        # sleep 3 minutes between tx blasts
        time.sleep(300)
    else:
        time.sleep(300)
        quit()


if __name__ == '__main__':
   
    data = Config()
    network = Network(data.network)
    u = Util(data.network)
    snekdb = SnekDB(data.database_user, data.network, data.delegate)
    exchange = Exchange(snekdb, data)
    client = u.get_client(network.api_port)
    build_network()
    dynamic = Dynamic(data.database_user, data.voter_msg, data.network, network.api_port)
    # get dot path for load_env and load
    dot = u.core+'/.env'
    load_dotenv(dot)
    
    while True:
        share_payment()
