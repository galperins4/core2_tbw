# Python True Block Weight

## INSTALLATION

### A/ Clean Install
Run the following in relay/forger user. Replace SUDO_USER with a username with sudo elevation (i.e. having sudo group)
```bash
cd && bash <(curl -s https://raw.githubusercontent.com/galperins4/core2_tbw/solar/install.sh) SUDO_USER
```

Next, clone the [sample config](./core/config/config.sample), then modify as explained in [Configuration & Usage](#configuration--usage)
```bash
cd ~/core2_tbw && cp core/config/config.sample core/config/config

Next, move on to [configuration](#configuration--usage)
```
---
<br>

### B/ Update An Existing Installation
#### update core
```bash
cd ~/core2_tbw
git pull
```

#### update python libraries
see [changelog](#changelog) if an update is required


#### check config
see [changelog](#changelog) if an update is required


#### Restart the processes
```bash
pm2 restart tbw
pm2 restart pay
pm2 restart pool
pm2 logs /"(tbw|pay|pool)"/
```
---

<br>

### C/ Overwrite An Existing Installation/Clean Start
Assuming you opted to wipe the existing installation when the install script asks, it will already care for the following. Just; restore your config afterwards (make sure start block is correct to avoid double payment for previous blocks), and move on to [initialization](#2-initialize)

- Stop all pm2 TBW processes (`pm2 stop tbw pay pool`)
- Delete all pm2 TBW process (`pm2 delete tbw pay pool`)
- (Optional) delete logs (`cd ~/.pm2/logs; rm -rf tbw-* pay-* pool-*`)
- Backup your config file (`cp ~/core2_tbw/core/config/config ~/tbw-config-timestamp`)
- Backup your databases (`cp ~/core2_tbw/*.db ~/*.db-timestamp`)
- Remove core2_tbw folder
- Fetch the latest version of the package and build dependencies
<br>

---

## CONFIGURATION & USAGE

### 1. Configure
After installation completed, you need to clone the [sample config](./core/config/config.sample) modify according to [Available Configuration Options](#available-configuration-options)

```bash
cd ~/core2_tbw && cp core/config/config.sample core/config/config && chmod 600 core/config/config
```

Main values to update here are the following:

```txt
START_BLOCK, NETWORK, DATABASE_USER,
DELEGATE, PUBLIC_KEY,
INTERVAL, VOTER_SHARE, PASSPHRASE, KEEP, PAY_ADDRESSES,
POOL_IP, PROPOSAL
```

### 2. Initialize
Once this has been done you need to execute first time initialization

```bash
cd ~/core2_tbw && bash tbw.sh
```

This will get you to the main menu script. 
- Initialize with option `[0]`. 
- You can then select options `[1]`-`[5]` to either run all modules at once or in parts. Notice that **tbw is prerequisite to pay & pool**.

---
---
<br>

## AVAILABLE CONFIGURATION OPTIONS
> **Important!**<br>
> - Pay_addresses and keep keys should match.
> - DO NOT delete the reserve key as it is required. All other's can be deleted or more added.
> - In addition, payment is triggered to start based on when total blocks forged / interval is an integer (with no remainder).

> **Custom voter shares**<br>
> To use custom voter shares, following 2 options are available:
> 1. Directly update the column "share" column in the voters table of `your_network`.db
> 2. Turn on custom.py and send a POST request to `http://ip:port/updateShare` endpoint.<br>
>   example: `{"address":"DKahhVFVJfqCcCmaQHuYzAVFKcWjBu5i6Z", "share":0.10}`

> **Important!**<br>
> If at any time you need to change the share rate in config, 
> - you must stop tbw
> - update your config
> - reconfigure database 
> ```bash 
> pm2 stop tbw
> cd ~/core2_tbw
> . .venv/bin/activate
> python3 core/tbw.py --shareChange
> deactivate
> pm2 start tbw
> ```

> **Python 3.6+ is required**
---
<br>

### True Block Weight
| Config Option | Default Setting | Description | 
| :--- | :---: | :--- |
| START_BLOCK | 0 | Script will start calculations only for blocks after specified start block |
| NETWORK | network | ark_mainnet or persona_mainnet or qredit_mainnet or solar_mainnet etc.. |
| DATABASE_USER | dbname | This is the postgresql database username nodeDB (usually your os username) |
| DELEGATE | delegate | Delegate name |
| PUBLIC_KEY | publicKey | Delegate public key |
| INTERVAL | 204  | The interval you want to pay voters in blocks. A setting of 204 would pay every 204 blocks (~= 204 x 8 x 53 seconds) |
| VOTER_SHARE | 0.50  | Percentage to share with voters (0.xx format) |
| PASSPHRASE | passphrase | 12 word delegate passphrase |
| SECONDPHRASE | None | Second 12 word delegate passphrase |
| VOTER_MSG | Delegate X - True Block Weight | ARK and ARK Fork coins only - message you want in vendor field for share payments |
| BLOCK_CHECK | 30 | How often you want the script to check for new blocks in seconds. Recommend low value (e.g., 30 seconds) |
| VOTE_CAP | 0 | Cap voters for how much they can earn with votes. For example 10000 will mean any wallet over 10K will only be paid based on 10K weight |
| VOTE_MIN | 0 | Use this if you have a minimum wallet balance to be eligible for payments |
| FIXED | addr1:0,addr2:0 | Use this for fixed deals. Amount will be spread evenly over the set interval |
| WHITELIST | N | Enable payment to only whitelisted addresses |
| WHITELIST_ADDR | addr1,addr2,addr3 | Comma seperated list of addresses to allow voter payments to |
| BLACKLIST | block | Options are block or assign. Block zero's out blocked accounts which then distributes their earnings to voters. Assign does the same but assigns weight to a designated account |
| BLACKLIST_ADDR | addr1,addr2,addr3 | Comma seperated list of addresses to block from voter payments |
| BLACKLIST_ASSIGN | addr | If assign option is picked, this is the address those blacklisted shares go to. DO NOT SET to an account voting for said delegate. It is HIGHLY recommended this is set to the reserve address! |
| MIN_PAYMENT| 0 | Minimum threshold for payment. If set to 1, any payout less than 1 ARK will be held until the next pay run and accumulated |
| KEEP | reserve:0.25,second:0.25 | These are the percentages for delegates to keep and distribute among x accounts (Note: reserve:your_addr1 is required! all others are optional |
| PAY_ADDRESSES | reserve:addr1,second:addr2 | These are the addresses to go with the keep percentages (Note: reserve:your_addr1 is required! all others are optional) |
| MULTI | N | Change to "Y" if you'd like payments to be made using Multipayments |

<br>

### Exchange (Experimental - ark network only)
| Config Option | Default Setting | Description | 
| :--- | :---: | :--- |
| EXCHANGE | N | Changing value to Y will enable exchange swap functionality |
| CONVERT_FROM | ark, ark | Network the swap is sending from - ark only |
| CONVERT_ADDRESS | addr1, addr2 | Reward address we are converting from for the swap - can support one or many|
| CONVERT_TO | usdc, xrp | Cryptocurrency we want to swap / exchange into - can support one or many |
| ADDRESS_TO | usdc_addr1, xrp_addr2 | Addresses to exchange into - can support one or many |
| NETWORK_TO | eth, xrp | Network for the receving swap cryptocurrency - can support one or many |
| PROVIDER | provider, provider | Provider of the swap - Available options are "SimpleSwap" or "ChangeNow" |

**NOTE 1**: Exchange address does not currently work with fixed amount/address processing. Do NOT enable exchange for fixed accounts

**NOTE 2**: For full disclosure - swap exchanges require an API key to create. All swaps are requested through my affiliate accounts at SimpleSwap / ChangeNow which generates a referral fee. All exchange/swap processing is the responsibility of SimpleSwap and ChangeNow.

**NOTE 3**: exchange_configtest.py (under core folder) has been created to test exchange config to prior to turning on. To execute run `python3 exchange_configtest.py` after setting up configuration as described in the table above

<br>

### Pool
| Config Option | Default Setting | Description | 
| :--- | :---: | :--- |
| POOL_IP | xx.xx.xx.xx | IP of the node the pool is installed on |
| EXPLORER | https://explorer.solar.org/ | The address of the explorer for the coin. If not exists or empty (''), will be read from network definitions|
| PROPOSAL | https://xx.xx.xx/ | Link to the delegate proposal (if any) |
| PROPOSALX | https://yy.yy.yy/ | Link to the delegate proposal in different language |
| PROPOSALX_LANG | CC | Language (code) of the second proposal |
| POOL_PORT | 5000 | Port for pool/webhooks |
| CUSTOM_PORT | 5004 | Custom port for using custom voter share update functionality |
| POOL_VERSION | original | Set the pool website version - options are "original" or "geops" |

---
---
<br>

## TO-DO

- Add more features as necessary
- Additional exception handling

<br>

## CHANGELOG

### 3.0.1
- updated to support multi-vote implementation


### 3.0.0
- new change to account for devfund implementation 
- updated to v3 (bip340) transaction signing


### 2.7.6
dynamic multifee
- multifee is no longer fixed but fetched dynamically
- added option to backup databases during reinstall


### 2.7.5
pool template osrn
- new config options PROPOSALX and PROPOSALX_LANG
- new pool website option osrn (based on geops template)


### 2.7.4
- fix: 500 error in pool if new voter registered in tbw sleep


### 2.7.3
- fix: fee burn added to reward alloc calculation


### 2.7.2
- fix: alias expansion needs to be performed earlier in install script
- fix: dotenv cannot expand variables after quotes in config.sample


### 2.7.1
- fix: div/0 when votesum is 0


### 2.7.0
- Solar Mainnet added to networks
- fix: dotenv cannot expand variables after quotes in config.sample


### 2.6.7
- changes in installer and tbw.sh for detecting pm2 executable. Compatible with solar 3.2.0-next.2+.
- installer now offers to backup the config if detects a reinstall and stops if backup fails.


### 2.6.6
- doc: README-FIRST merged to README with updated install & config info 


### 2.6.5
- fix: read blocks in correct order when calculating productivity
- requires a modified python-client[^1] to utilize orderBy parameter when fetching blocks from API<br>

If updating from an earlier version, execute the following after git pull:
```bash
cd ~/core2_tbw
. .venv/bin/activate
pip3 uninstall arkecosystem-client
pip3 install git+https://github.com/osrn/python-client.git@master#egg=solar-client
deactivate
```

[^1]: using forked repo until pull request is approved at solar-network/python-client. 


### 2.6.4
- To keep solar a non-sudo user and simplify the installation, seperated core installation from tbw.sh into the standalone [install.sh](./install.sh) script.
- install.sh now rewrites CPATH to prevent python package compilation errors (CPATH is restored back afterwards) 
- tbw.sh is used for initialization and start-stop actions.
- Ported the app to python virtual environment.
- Moved COIN definition from core/config/config into core/network/network

**Changes for Solar 3.2.0-next.0 compatibility:** Solar 3.2.0-next.0 no longer accepts TCPIP connections to postgresql, but utilize UNIX-domain-socket connection. Moreover, an isolated instance of Postgresql is now in effect, hence the local socket path needs to be provided.
- ark.py, tbw.py. Added logic for optional postgresql connection type (UNIX / INET) (*)
- added solar_testnet under core/network with definitions for DATABASE HOST (unix socket connection), USER, COIN and EXPLORER
- core/config/config EXPLORER definition will override the same parameter in core/network/network
- get_yield function adjusted to cope with the change in how delegate blocks listed in 3.2.0-next0 API

*(\*) compatibiliy with other chains preserved by keeping'localhost' as the default postgresql host which defaults to TCPIP connection.*


### 2.6.3
Pool enhanced with more information retrieved through Solar API
- Added relay sync status and height
- Added delegate total votes
- Forging position correction
- Added total blocks forged and last forged block, with links to explorer
- Added productivity calculation
- Added a Summary (Totals) row and Voter supply ratios column to the pool ledger
- Added coloring to ending/paid amounts
- Added delegate name to the page title


### 0.4
 - Added exchange / swap functionality (for ark network only)

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

<br>

## SECURITY

If you discover a security vulnerability within this package, please open an issue. All security vulnerabilities will be promptly addressed.


<br>

## CREDITS

- [galperins4](https://github.com/galperins4)
- [All Contributors](../../contributors)

<br>

## LICENSE

[MIT](LICENSE) © [galperins4](https://github.com/galperins4)
