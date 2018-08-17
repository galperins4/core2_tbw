#!/usr/bin/env python
from crypto.conf import use_network
from crypto.transactions.builder.transfer import TransferBuilder
from tbw import parse_config
from snek.snek import SnekDB
from ark import ArkClient
import time

def get_client(ip="localhost", api_version='v2'):
    port = network[data['network']]['port']
    return ArkClient('http://{0}:{1}/api/'.format(ip, port), api_version=api_version)

def broadcast(tx):
    #broadcast to relay
    try:
        transaction = client.transactions.create(tx)
        records = [[j['recipientId'],j['amount'],j['id']] for j in tx]
        time.sleep(1)
    except BaseException:
        # fall back to delegate node to grab data needed
        backup_client = get_client(data['delegate_ip'])
        transaction = backup_client.transactions.create(tx)
        records = [[j['recipientId'],j['amount'],j['id']] for j in tx]
        time.sleep(1)

    snekdb.storeTransactions(records)

def build_transfer_transaction(address, amount, vendor, fee, pp, sp):
    use_network(data['network'])
    transaction = TransferBuilder(
        recipientId=address,
        amount=amount,
        vendorField=vendor,
        fee=fee
    )
    transaction.sign(pp)
    if sp != None:
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
                tx = build_transfer_transaction(i[1], (i[2]), i[3], dynamic_fee, passphrase, secondphrase)
                signed_tx.append(tx)

            broadcast(signed_tx)
            snekdb.processStagedPayment(unique_rowid)

            # payment run complete
            print('Payment Run Completed!')
            # sleep 5 minutes between 50tx blasts
            time.sleep(300)

        else:
            time.sleep(300)

if __name__ == '__main__':
   
    data, network = parse_config()
    snekdb = SnekDB(data['dbusername'])
    client = get_client()
    dynamic_fee = data['override_fee']

    # Get the passphrase from config.json
    passphrase = data['passphrase']
    # Get the second passphrase from config.json
    secondphrase = data['secondphrase']
    if secondphrase == 'None':
        secondphrase = None

    go()