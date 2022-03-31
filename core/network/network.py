import os
from dotenv import load_dotenv
from pathlib import Path

class Network():
    def __init__(self, network):
        self.home = str(Path.home())
        self.network = network
        env_path = self.home + '/core2_tbw/core/network/' + self.network
        load_dotenv(env_path)
        self.load_network()
        
        
    def load_network(self):
         self.epoch = os.getenv("EPOCH").split(',')
         self.version = int(os.getenv("VERSION"))
         self.wif = int(os.getenv("WIF"))
         self.api_port = os.getenv("API_PORT")
         self.database = os.getenv("DATABASE")
         self.database_user = os.getenv("DATABASE_USER")
         self.database_password = os.getenv("DATABASE_PASSWORD")
