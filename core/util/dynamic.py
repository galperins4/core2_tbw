import os.path
import json

atomic = 100000000


class Dynamic:
    def __init__(self, u, msg):
        self.username = u
        self.msg = msg
        self.network = None
        #self.delegate = None

    def get_node_configs(self):
        envpath = '/home/' + self.username + '/.ark/config/'
        # check if there is a network file
        if os.path.exists(envpath + 'network.json') is True:
            with open(envpath + 'network.json') as network_file:
                self.network = json.load(network_file)
        else:
            self.network = None
            

    def calculate_dynamic_fee(self, t, s, c):
        fee = int((t+s)*c)
        return fee


    def get_dynamic_fee(self):
        if self.network is None or self.network['constants'][0]['fees']['dynamic'] is False:
            # standard transaction fees
            transaction_fee = int(.1 * atomic)
        else:
            # get size of transaction - S
            standard_tx = 230
            v_msg = len(self.msg)
            tx_size = standard_tx + v_msg
            # get T
            dynamic_offset = self.network['constants'][0]['fees']['dynamicFees']['addonBytes']['transfer']
            # get C
            fee_multiplier = self.network['constants'][0]['fees']['dynamicFees']['minFeePool']
            #calculate transaction fee
            transaction_fee = self.calculate_dynamic_fee(dynamic_offset, tx_size, fee_multiplier)

        return transaction_fee
