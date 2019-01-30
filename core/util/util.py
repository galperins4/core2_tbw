import json
from client import ArkClient
from pathlib import Path


class Util():
    def __init__(self):
        self.home = str(Path.home())
        self.tbw = self.home+'/core2_tbw/config'
        
        self.data, self.network = self.parse_configs()
        net = self.data['network'].split('_')
        coin, network = net[0], net[1]
       
        self.core = self.home+'/.config/'+coin+"-core/"+network
        

    def get_client(self, ip="localhost"):
        port = self.network[self.data['network']]['port']
        return ArkClient('http://{0}:{1}/api'.format(ip, port))


    def parse_configs(self):
        with open((self.tbw+'/config.json')) as data_file:
            d = json.load(data_file)
        with open((self.tbw+'/networks.json')) as network_file:
            n = json.load(network_file)

        return d, n    
    
    
    def parse_pool(self):
        with open((self.tbw+'/pool.json')) as data_file:
            d = json.load(data_file)
        with open((self.tbw+'/networks.json')) as network_file:
            n = json.load(network_file)
        
        return d, n
