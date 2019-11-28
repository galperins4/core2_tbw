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
    
    # broadcast to relay
    try:
        transaction = client.transactions.create(tx)
        print(transaction)
        id = tx[0]['id']
        records = [[j['recipientId'], j['amount'], id] for j in tx[0]['asset']['payments']]
        time.sleep(1)
    except BaseException as e:
        # error
        print("Something went wrong", e)
        quit()

    snekdb.storeTransactions(records)
    
    return transaction['data']['accept']


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


def get_nonce():
    n = client.wallets.get(data.delegate)
    return int(n['data']['nonce'])


def share_multipay():
    while True:
        signed_tx = []

        # set max multipayment
        max_tx = dynamic.get_multipay_limit()
        unprocessed_pay = snekdb.stagedArkPayment(int(max_tx)).fetchall()

        # query not empty means unprocessed blocks
        if unprocessed_pay:
            unique_rowid = [y[0] for y in unprocessed_pay]
            check = {}
            nonce = int(get_nonce() + 1)

            transaction = MultiPayment()
            transaction.set_version()
            transaction.set_nonce(nonce)

            for i in unprocessed_pay:

                # fixed processing
                if i[1] in data.fixed.keys():
                    fixed_amt = int(data.fixed[i[1]] * data.atomic)
                    transaction.add_payment(fixed_amt, i[1])
                else:
                    transaction.add_payment(i[2], i[1])

            transaction.sign(data.passphrase)
            sp = data.secondphrase
            if sp == 'None':
                sp = None
            if sp is not None:
                transaction.second_sign(sp)

            transaction_dict = transaction.to_dict()
            signed_tx.append(transaction_dict)
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
            time.sleep(60)

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
    transaction_fee = dynamic.get_transaction_fee()
    print(transaction_fee)
    quit()
    #get dot path for load_env and load
    dot = u.core+'/.env'
    load_dotenv(dot)
    #share_standard()
    share_multipay()
