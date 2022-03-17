# Installation

## Clean Install
```bash
cd && bash <(curl -s https://raw.githubusercontent.com/osrn/core2_tbw/develop/install.sh)
```

clone the [sample config](./core/config/config.sample) i.e. `cp core/config/config.example core/config/config`, and modify as explained in [README.md #Configuration Options](README.md#configuration--usage)

<br>

## Update An Existing Installation
```bash
cd ~/core2_tbw
git pull
```

Check and revize your config file if necessary

Restart the processes
```bash
pm2 restart tbw
pm2 restart pay
pm2 restart pool
pm2 logs twb pay pool
```

<br>

## Overwrite An Existing Installation
- Stop all pm2 TBW processes
- Backup your config file
- Remove core2_tbw folder
- Follow the [Clean Install](#installation) section above
- Restore your config file

<br>


## Changelog
### v2.6.4 [osrn](https://github.com/osrn)
- To keep solar a non-sudo user and simplify the installation, seperated core installation from tbw.sh into the standalone [install.sh](./install.sh) script.
- tbw.sh is used for initialization and start-stop actions.
- Ported the app to python virtual environment.
- Moved COIN definition from core/config/config into core/network/network

**Changes for Solar 3.2.0-next.0 compatibility:** Solar 3.2.0-next.0 no longer accepts TCPIP connections to postgresql, but utilize UNIX-domain-socket connection. Moreover, an isolated instance of Postgresql is now in effect, hence the local socket path needs to be provided.
- ark.py, tbw.py. Added logic for optional postgresql connection type (UNIX / INET) (*)
- added solar_testnet under core/network with definitions for DATABASE HOST (unix socket connection), USER, COIN and EXPLORER
- core/config/config EXPLORER definition will override the same parameter in core/network/network
- get_yield function adjusted to cope with the change in how delegate blocks listed in 3.2.0-next0 API

*(\*) compatibiliy with other chains preserved by keeping'localhost' as the default postgresql host which defaults to TCPIP connection.*

<br>

### v2.6.3 [osrn](https://github.com/osrn)
Pool enhanced with more information retrieved through Solar API
- Added relay sync status and height
- Added delegate total votes
- Forging position correction
- Added total blocks forged and last forged block, with links to explorer
- Added productivity calculation
- Added a Summary (Totals) row and Voter supply ratios column to the pool ledger
- Added coloring to ending/paid amounts
- Added delegate name to the page title


<br>

## Credits
- Original author [galperins4](https://github.com/galperins4)
- Extensive testing [mtaylan](https://github.com/mtaylan/)
