# Python True Block Weight

## Installation

```sh
install and sync relay server
git clone https://github.com/galperins4/core2_tbw
cd ~/core2_tbw/config
fill out configs (see below)
cd ~/core2_tbw
bash tbw.sh
```

## Configuration & Usage
After the repository has been cloned you need to open the `config.json` / `pool.json` and change it to your liking. Once this has been done navigate to core2_tbw folder and execute `bash tbw.sh` to get to the main menu script. Install required packages with option 1. Initialize tbw with option 2. You can then select options 3-7 to either run all modules of tbw or parts. 

Important! - pay_addresses and keep keys should match in config.json. DO NOT delete the reserve key as it is required. All other's can be deleted or more added. In addition, payment is triggered to start based on when total blocks forged / interval is an integer (with no remainder). 

To use custom voter shares, the following 2 options are available:
1) Directly update the column "share" column in the voters table of ark.db
2) Turn on custom.py and send a POST request to the http://ip:port/updateShare endpoint. See below for example: `{"address":"DKahhVFVJfqCcCmaQHuYzAVFKcWjBu5i6Z", "share":0.10}`


Python 3.6+ is required.

## Available Configuration Options (TRUE BLOCK WEIGHT)
- network: which network (options are ark_mainnet, ark_devnet)
- start_block: script will start calculations only for blocks after specified start block
- delegate IP: this serves as a back-up IP for the API to call to in case the localhost does not respond
- dbusername: this is the postgresql database username nodeDB (usually your os username)
- publicKey: delegate public key
- interval:  the interval you want to pay voters in blocks. A setting of 211 would pay ever 211 blocks (or 422 ark)
- voter_share: percentage to share with voters (0.xx format)
- passphrase: delegate passphrase
- secondphrase: delegate second passphrase
- voter_msg: ARK and ARKfork coins only - message you want in vendor field for share payments
- block_check: How often you want the script to check for new blocks in seconds. Recommend low value (e.g., 30 seconds for ARK coins, high value for LISK coins)
- cover_tx_fees: Use this to indicate if you want to cover transaction fees (Y) or not (N)
- vote_cap: Use this if you cap voters for how much they can earn with votes. For example 10000 will mean any wallet over 10K will only be paid based on 10K weight
- vote_min: Use this if you have a minumum wallet balance to be eligible for payments
- whitelist: Y or N. Enable payment to only whitelisted addresses
- whitelist_addr: comma seperated list of addresses to allow voter payments to
- blacklist: Options are block or assign. Block zero's out blocked accounts which then distributes their earnings to voters. Assign does the same but assigns weight to a designated account. 
- blacklist_addr: comma seperated list of addresses to block from voter payments
- blacklist_assign: if assign option is picked, this is the address those blacklisted shares go to. DO NOT SET to an account voting for said delegate. It is HIGHLY recommended this is set to the reserve address!
- fixed_deal: use this if you have a fixed deal with a voter (e.g., 45 ark per day).
- fixed_deal_amt: format is address:amount. The amount to pay should correspond to interval. 
- min_payment: Minimum threshold for payment. If set to 1, any payout less than 1 ARK will be held until the next pay run and accumulated
- keep: there are the percentages for delegates to keep and distrubute among x accounts (Note: reserve is required! all others are optional)
- pay_addresses: these are the addresses to go with the keep percentages (Note: reserve is required! all others are optional)

## Available Configuration Options (POOL)
- network: which network (same as tbw options)
- pool_ip: IP of the node the pool is installed on
- explorer: The address of the explorer for the coin
- coin: which coin (e.g., ARK, KAPU)
- proposal: link to delegate proposal (if any)
- dbusername: this is the postgresql database username nodeDB (usually your os username)
- pubkey: delegate public key
- custom_port: custom port for using custom voter share update functionality

Note: Pool runs on port 5000

## To Do

- Add more features as necessary
- Additional exception handling

## Changelog

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





