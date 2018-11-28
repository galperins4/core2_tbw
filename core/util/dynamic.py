import os.path
import json

atomic = 100000000


class Dynamic:
    def __init__(self, u, msg):
        self.username = u
        self.msg = msg
        self.network = None
        self.delegate = None

    def get_node_configs(self):
        envpath = '/home/' + self.username + '/.ark/config/'
        # check if there is a network file
        if os.path.exists(envpath + 'network.json') is True:
            with open(envpath + 'network.json') as network_file:
                self.network = json.load(network_file)
        else:
            self.network = None
        # open delegate config file
        with open(envpath + 'delegates.json') as delegate_file:
            self.delegate = json.load(delegate_file)

    def calculate_dynamic_fee(self, t, s, c, min_accept):
        prelim_fee = int((t + s) * c)

        # check to see if fee will be accepted on node
        if prelim_fee < min_accept:
            return min_accept
        else:
            return prelim_fee

    def get_dynamic_fee(self):
        if self.network is None or self.network['constants'][0]['fees']['dynamic'] is False:
            # standard transaction fees
            transaction_fee = int(.1 * atomic)
        else:
            # get size of transaction - S
            standard_tx = 160
            v_msg = len(self.msg)
            tx_size = standard_tx + v_msg
            # get T
            dynamic_offset = self.network['constants'][0]['fees']['dynamicFees']['addonBytes']['transfer']
            # get C
            del_fee_multiplier = self.delegate['dynamicFees']['feeMultiplier']
            min_fee_pool = self.network['constants'][0]['fees']['dynamicFees']['minFeePool']
            #min_fee_broadcast = self.network['constants'][0]['fees']['dynamicFees']['minFeeBroadcast']
            high_fee = [del_fee_multiplier, min_fee_pool]
            fee_multiplier = max(high_fee)
            
            # get minimum acceptable fee for node
            min_fee = self.delegate['dynamicFees']['minAcceptableFee']
            transaction_fee = self.calculate_dynamic_fee(dynamic_offset, tx_size, fee_multiplier, min_fee)

        return transaction_fee
