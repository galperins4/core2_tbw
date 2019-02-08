import os
from dotenv import load_dotenv

class Network():
    def __init__(self, network):
        self.network = network
        print(self.network)
        quit()
        load_dotenv(self.network)
        self.load_network()
        
        
    def load_network(self):
         self.epoch = os.getenv("EPOCH").split(',')
         self.version = os.getenv("VERSION")
         self.wif = os.getenv("WIF")
         self.api_port = os.getenv("API_PORT")
         self.database = os.getenv("DATABASE")
         self.database_user = os.getenv("DATABASE_USER")
         self.database_password = os.getenv("DATABASE_PASSWORD")
