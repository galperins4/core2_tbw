from client import ArkClient
from pathlib import Path


class Util():
    def __init__(self, coin, network):
        self.network = network
        self.coin = coin
        self.home = str(Path.home())
        self.core_config = '/.config/'+coin+"-core/"+network
        self.tbw_config = '/core2_tbw/config'
        
        self.core, self.tbw = get_paths()


    def get_paths(self):
        core_config_path = self.home+self.core_config
        tbw_config_path = self.home+self.tbw_config
        
        return core_config_path, tbw_config_path
        
    
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
