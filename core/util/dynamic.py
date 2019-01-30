import os.path
import json
from .util import Util

atomic = 100000000


class Dynamic:
    def __init__(self, u, msg):
        self.username = u
        self.msg = msg
        self.network = None
        self.dot = None

    def get_node_configs(self):
        u = Util()
        plugin_file = u.core+'/plugins.js'
        
        
        #plugin_file = '/home/' + self.username + '/.ark/config/plugins.js'
        lines = [line.rstrip('\n') for line in open(plugin_file)]
        self.plugins = lines

    
    def parser(self, line):
        temp = line.split(':')[1]
        return temp.replace(',','').strip()
    
    
    def calculate_dynamic_fee(self, t, s, c):
        fee = int((t+s)*c)
        return fee

    
    def scan_file(self,f):
        check = False

        for count,i in enumerate(f):
            # check for dynamic fees
            if "dynamicFees" in i:
                check = True
            elif "enabled" in i:
                if check is True:
                    e = self.parser(i)
                    check = False
            # check for minPoolFee
            elif "minFeePool" in i:
                mfp = int(self.parser(i))
            # check for transfer bytes
            elif "transfer" in i:
                o = int(self.parser(i))
    
        return e, mfp, o
    
    def get_dynamic_fee(self):
        
        enabled, fee_multiplier, dynamic_offset = self.scan_file(self.plugins)
        if enabled is "false":
            transaction_fee = int(.1 * atomic)
        else:
            # get size of transaction - S
            standard_tx = 230
            v_msg = len(self.msg)
            tx_size = standard_tx + v_msg
            #calculate transaction fee
            transaction_fee = self.calculate_dynamic_fee(dynamic_offset, tx_size, fee_multiplier)

        return transaction_fee
