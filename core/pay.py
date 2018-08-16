#!/usr/bin/env python
from crypto.conf import use_network
from crypto.serializer import Serializer
from crypto.transactions.builder.transfer import TransferBuilder
from tbw import parse_config
from snek.snek import SnekDB
from ark import ArkClient
import time


def build_transfer_transaction():
    """Test if a transfer transaction gets built
    """
    use_network(data['network'])
    transaction = TransferBuilder(
        recipientId='DMzBk3g7ThVQPYmpYDTHBHiqYuTtZ9WdM3',
        amount=1000000,
        vendorField='Test'.encode()
        # vendorField='This is a transaction from Python'.encode()
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

    tx_v2 = Serializer(tx).serialize()
    print(tx_v2)
    quit()

    client = ArkClient('http://127.0.0.1:4003/api/')

    post_tx = client.transactions.create(tx)
    print(post_tx)

  
