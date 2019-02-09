import os
from dotenv import load_dotenv
from pathlib import Path

class Config():
    def __init__(self):
        self.home = str(Path.home())
        self.network = network
        env_path = self.home + '/core2_tbw/core/config/config'
        load_dotenv(env_path)
        self.load_config()
    
    
    def load_config(self):
        self.epoch = os.getenv("EPOCH").split(',')
        self.version = os.getenv("VERSION")
        self.wif = os.getenv("WIF")
        self.api_port = os.getenv("API_PORT")
        self.database = os.getenv("DATABASE")
        self.database_user = os.getenv("DATABASE_USER")
        self.database_password = os.getenv("DATABASE_PASSWORD")
