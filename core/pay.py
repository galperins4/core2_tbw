#!/usr/bin/env python
from crypto.configuration.network import set_custom_network
from crypto.transactions.builder.transfer import Transfer
from tbw import parse_config
from util.sql import SnekDB
from util.dynamic import Dynamic
from ark import ArkClient
from datetime import datetime
import time

atomic = 100000000


def get_client(ip="localhost", api_version='v2'):
    port = network[data['network']]['port']
    return ArkClient('http://{0}:{1}/api/'.format(ip, port), api_version=api_version)


def broadcast(tx):
    # broadcast to relay
    try:
        transaction = client.transactions.create(tx)
        print(transaction)
        records = [[j['recipientId'], j['amount'], j['id']] for j in tx]
        time.sleep(1)
    except BaseException:
        # fall back to delegate node to grab data needed
        backup_client = get_client(data['delegate_ip'])
        transaction = backup_client.transactions.create(tx)
        print(transaction)
        records = [[j['recipientId'], j['amount'], j['id']] for j in tx]
        time.sleep(1)

    snekdb.storeTransactions(records)


def build_network():
    e = network[data['network']]['epoch']
    t = [int(i) for i in e]
    epoch = datetime(t[0], t[1], t[2], t[3], t[4], t[5])
    version = network[data['network']]['version']
    wif = network[data['network']]['wif']
    set_custom_network(epoch, version, wif)


def build_transfer_transaction(address, amount, vendor, fee, pp, sp):
    transaction = Transfer(
        recipientId=address,
        amount=amount,
        vendorField=vendor,
        fee=fee
    )
    transaction.sign(pp)
    if sp is not None:
        transaction.second_sign(sp)

    transaction_dict = transaction.to_dict()
    return transaction_dict


def go():
    while True:
        signed_tx = []

        # check for unprocessed payments
        unprocessed_pay = snekdb.stagedArkPayment().fetchall()

        # query not empty means unprocessed blocks
        if unprocessed_pay:
            unique_rowid = [y[0] for y in unprocessed_pay]

            for i in unprocessed_pay:
                tx = build_transfer_transaction(i[1], (i[2]), i[3], transaction_fee, passphrase, secondphrase)
                signed_tx.append(tx)
                time.sleep(0.25)

            broadcast(signed_tx)
            snekdb.processStagedPayment(unique_rowid)

            # payment run complete
            print('Payment Run Completed!')
            # sleep 2.5 minutes between tx blasts
            time.sleep(150)

        else:
            time.sleep(150)


if __name__ == '__main__':
   
    data, network = parse_config()
    snekdb = SnekDB(data['dbusername'])
    client = get_client()
    build_network()

    dynamic = Dynamic(data['dbusername'], data['voter_msg'])
    dynamic.get_node_configs()
    transaction_fee = dynamic.get_dynamic_fee()

    # Get the passphrase from config.json
    passphrase = data['passphrase']
    # Get the second passphrase from config.json
    secondphrase = data['secondphrase']
    if secondphrase == 'None':
        secondphrase = None

    go()
