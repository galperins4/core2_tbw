import json
import os
from pathlib import Path
from dotenv import load_dotenv


class Util():
    def __init__(self, coin network):
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
        
    
    def get_client(self):
        pass


    def parse_configs(self):
        pass    
    
    
    def parse_pool(self):
        pass
