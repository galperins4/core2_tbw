from client import ArkClient
from pathlib import Path


class Util():
    def __init__(self):
        #self.network = network
        #self.coin = coin
        self.home = str(Path.home())
        self.tbw = self.home+'/core2_tbw/config'
        
        data, network = self.parse_configs()
        net = data['network'].split('_')
        coin = net[0]
        network = net[1]
       
        self.core = self.home+'/.config/'+coin+"-core/"+network
        

    def get_client(self, ip="localhost"):
        port = network[data['network']]['port']
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
