import os
from dotenv import load_dotenv
from pathlib import Path

class Config():
    def __init__(self):
        self.home = str(Path.home())
        self.network = network
        env_path = self.home + '/core2_tbw/core/config/config'
        load_dotenv(env_path)
        self.load_tbw_config()
        self.load_pool_config()
    
    
    def load_tbw_config(self):
        self.start_block
        self.network
        self.delegate_ip
        self.database_user
        self.public_key
        self.interval
        self.voter_share
        self.passphrase
        self.secondphrase
        self.voter_msg
        self.block_check
        self.cover_tx_fee
        self.vote_cap
        self.vote_min
        self.fixed
        self.whitelist
        self.whitelist_addr
        self.blacklist
        self.blacklist_addr
        self.blacklist_assign
        self.min_payment
        self.keep
        self.pay_addresses
        
        
    def load_pool_config(self):
        self.pool_ip = os.getenv("POOL_IP")
        self.explorer = os.getenv("EXPLORER")
        self.delegate = os.getenv("DELEGATE")
        self.coin = os.getenv("COIN")
        self.proposal = os.getenv("PROPOSAL")
        self.pool_port = os.getenv("POOL_PORT")
        self.custom_port = os.getenv("CUSTOM_PORT")
        self.pool_version = os.getenv("POOL_VERSION")
        
                
        self.epoch = os.getenv("EPOCH").split(',')

