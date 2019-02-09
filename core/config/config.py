import os
from dotenv import load_dotenv
from pathlib import Path

class Config():
    def __init__(self):
        self.home = str(Path.home())
        env_path = self.home + '/core2_tbw/core/config/config'
        load_dotenv(env_path)
        self.load_tbw_config()
        self.load_pool_config()
    
    
    def load_tbw_config(self):
        self.start_block = os.getenv("START_BLOCK")
        self.network = os.getenv("NETWORK")
        self.delegate_ip = os.getenv("DELEGATE_IP")
        self.database_user = os.getenv("DATABASE_USER")
        self.public_key = os.getenv("PUBLIC_KEY")
        self.interval = os.getenv("INTERVAL")
        self.voter_share = os.getenv("VOTER_SHARE")
        self.passphrase = os.getenv("PASSPHRASE")
        self.secondphrase = os.getenv("SECONDPHRASE")
        self.voter_msg = os.getenv("VOTER_MSG")
        self.block_check = os.getenv("BLOCK_CHECK")
        self.cover_tx_fee = os.getenv("COVER_TX_FEE")
        self.vote_cap = os.getenv("VOTE_CAP")
        self.vote_min = os.getenv("VOTE_MIN")
        self.fixed = os.getenv("FIXED").split(',')
        self.whitelist = os.getenv("WHITELIST")
        self.whitelist_addr = os.getenv("WHITELIST_ADDR").split(',')
        self.blacklist = os.getenv("BLACKLIST")
        self.blacklist_addr = os.getenv("BLACKLIST_ADDR").split(',')
        self.blacklist_assign = os.getenv("BLACKLIST_ASSIGN")
        self.min_payment = os.getenv("MIN_PAYMENT")
        self.keep = os.getenv("KEEP").split(',')
        self.pay_addresses = os.getenv("PAY_ADDRESSES").split(',')
        
        
    def load_pool_config(self):
        self.pool_ip = os.getenv("POOL_IP")
        self.explorer = os.getenv("EXPLORER")
        self.delegate = os.getenv("DELEGATE")
        self.coin = os.getenv("COIN")
        self.proposal = os.getenv("PROPOSAL")
        self.pool_port = os.getenv("POOL_PORT")
        self.custom_port = os.getenv("CUSTOM_PORT")
        self.pool_version = os.getenv("POOL_VERSION")
