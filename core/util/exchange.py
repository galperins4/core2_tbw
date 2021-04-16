import os.path
import json
from .util import Util

atomic = 100000000


class Dynamic:
    def __init__(self, u, msg, network, port):
        self.username = u
        self.msg = msg
        self.network = network
        self.port = port
        self.u = Util(self.network)
        self.client = self.u.get_client(self.port)

    
    def get_multipay_limit(self):
        try:
            limit = int(self.client.node.configuration()['data']['constants']['multiPaymentLimit'])
        except:
            limit = 20
        return limit
