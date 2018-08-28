#!/usr/bin/env python
from crypto.configuration.network import set_network
from crypto.transactions.builder.transfer import Transfer
from tbw import parse_config, get_node_configs, get_dynamic_fee
from snek.snek import SnekDB
from ark import ArkClient
import time

atomic = 100000000

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
    set_network(data['network'])
    transaction = Transfer(
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
                tx = build_transfer_transaction(i[1], (i[2]), i[3], transaction_fee, passphrase, secondphrase)
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

    # get node config and fee
    net, delegate = get_node_configs(data['dbusername'])
    if net == None or net['constants'][0]['fees']['dynamic']==False:
        # standard transaction fees
        transaction_fee = int(.1 * atomic)
    else:
        # get size of transaction - S
        standard_tx = 80
        padding = 80
        v_msg = len(data['voter_msg'])
        tx_size = standard_tx+padding+v_msg

        # get T
        dynamicOffset = net['constants'][0]['dynamicOffsets']['transfer']

        # get C
        feeMultiplier = delegate['dynamicFees']['feeMultiplier']

        # get minimum acceptable fee for node
        minFee = delegate['dynamicFees']['minAcceptableFee']

        transaction_fee = get_dynamic_fee(dynamicOffset, tx_size, feeMultiplier, minFee)

    # Get the passphrase from config.json
    passphrase = data['passphrase']
    # Get the second passphrase from config.json
    secondphrase = data['secondphrase']
    if secondphrase == 'None':
        secondphrase = None

    go()
