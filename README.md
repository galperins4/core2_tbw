# Python True Block Weight

## Clean/New Installation

```sh
Install and sync relay server
git clone https://github.com/galperins4/core2_tbw
cd ~/core2_tbw/core/config
nano config
fill out configs (see below)
cd ~/core2_tbw
bash tbw.sh
```

## Configuration & Usage
After the repository has been cloned you need to open the `config` and change it to your liking (see details below for Available Configuration Options). Once this has been done navigate to core2_tbw folder and execute `bash tbw.sh` to get to the main menu script. Install required packages with option 1. Initialize tbw with option 2. You can then select options 3-7 to either run all modules of tbw or parts. 

Important! - pay_addresses and keep keys should match in config. DO NOT delete the reserve key as it is required. All other's can be deleted or more added. In addition, payment is triggered to start based on when total blocks forged / interval is an integer (with no remainder). 

To use custom voter shares, the following 2 options are available:
1) Directly update the column "share" column in the voters table of ark.db
2) Turn on custom.py and send a POST request to the http://ip:port/updateShare endpoint. See below for example: `{"address":"DKahhVFVJfqCcCmaQHuYzAVFKcWjBu5i6Z", "share":0.10}`

IMPORTANT: If at any time you change you share rate you must stop tbw, update your config.json and run the following command `python3 tbw.py --shareChange`

Python 3.6+ is required.

## Available Configuration Options (TRUE BLOCK WEIGHT)

START_BLOCK = 0      
# Script will start calculations only for blocks after specified start block

NETWORK = "network"       
# ark_mainnet or persona_mainnet or qredit_mainnet etc..)

DATABASE_USER = "dbname"     
# This is the postgresql database username nodeDB (usually your os username)

DELEGATE = "delegate"        
# Delegate name

PUBLIC_KEY = "publicKey"     
# Delegate public key

INTERVAL = 211               
# The interval you want to pay voters in blocks. A setting of 211 would pay ever 211 blocks (or 422 ark)

VOTER_SHARE = 0.50           
# Percentage to share with voters (0.xx format)

PASSPHRASE = "passphrase"    
# 12 word delegate passphrase inside ""

SECONDPHRASE = "None"        
# 2nd 12 word delegate passphrase inside ""

VOTER_MSG = "Delegate X - True Block Weight"  
# ARK and ARKfork coins only - message you want in vendor field for share payments

BLOCK_CHECK = 30             
# How often you want the script to check for new blocks in seconds. Recommend low value (e.g., 30 seconds for ARK coins, high value for LISK coins)

COVER_TX_FEE = "Y"           
# Use this to indicate if you want to cover transaction fees (Y) or not (N)

VOTE_CAP = 0                 
# Use this if you cap voters for how much they can earn with votes. For example 10000 will mean any wallet over 10K will only be paid based on 10K weight

VOTE_MIN = 0                 
# Use this if you have a minimum wallet balance to be eligible for payments

FIXED = "addr1:0,addr2:0"    
# Fixed payout addresses - Use this for fixed deals. Amount will be spread evenly over the set interval

WHITELIST = "N"              
# Enable payment to only whitelisted addresses

WHITELIST_ADDR = "addr1,addr2,addr3"  
# Comma seperated list of addresses to allow voter payments to

BLACKLIST = "block"          
# Options are block or assign. Block zero's out blocked accounts which then distributes their earnings to voters. Assign does the same but assigns weight to a designated account.    

BLACKLIST_ADDR = "addr1,addr2,addr3"   
# Comma seperated list of addresses to block from voter payments

BLACKLIST_ASSIGN = "addr"    
# If assign option is picked, this is the address those blacklisted shares go to. DO NOT SET to an account voting for said delegate. It is HIGHLY recommended this is set to the reserve address!

MIN_PAYMENT = 0.5            
# Minimum threshold for payment. If set to 1, any payout less than 1 ARK will be held until the next pay run and accumulated

KEEP = "reserve:0.25,your_second:0.25"  
# there are the percentages for delegates to keep and distribute among x accounts (Note: reserve is required! all others are optional)

PAY_ADDRESSES = "reserve:your_addr1,your_second:addr2"  
# These are the addresses to go with the keep percentages (Note: reserve is required! all others are optional)

# pool
POOL_IP = "xx.xx.xx.xx"                  # IP of the node the pool is installed on     
EXPLORER = "https://dexplorer.ark.io/"   # The address of the explorer for the coin
COIN = "DARK"                            # Coin name, DARK, ARK, QREDIT, PRSN etc
PROPOSAL = "https://xx.xx.xx/"           # Link to delegate proposal (if any)
POOL_PORT = 5000                         # Port for pool/webhooks
CUSTOM_PORT = 5004                       # Custom port for using custom voter share update functionality
POOL_VERSION = "original"                # Set the pool website version - options are "original" or "geops"

## To Do

- Add more features as necessary
- Additional exception handling

## Changelog

### 0.3
- updated for Typescript and changes to dynamic fee location
- Added support for Qredit, Ripa, and Phantom Core2
- Added back fixed deal support
- Added new pool website option (credits to Ark Delegate Geops)

### 0.2
- add function to adjust share rates if global value is changed
- add environment check to determine max tx to submit per broadcast
- increased tx blast spacing to prevent tx pool from being filled too quickly

### 0.1
- ark core_v2 initial release
- new custom voter share functionality

## Security

If you discover a security vulnerability within this package, please open an issue. All security vulnerabilities will be promptly addressed.

## Credits

- [galperins4](https://github.com/galperins4)
- [All Contributors](../../contributors)

## License

[MIT](LICENSE) © [galperins4](https://github.com/galperins4)





