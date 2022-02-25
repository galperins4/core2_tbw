import time

from config.config import Config
from flask import Flask, render_template, request
from flask_api import status
from network.network import Network
from util.sql import SnekDB
from util.util import Util
from lowercase_booleans import true, false

app = Flask(__name__)


@app.route('/')
def index():
    s = {}
    dstats = client.delegates.get(data.public_key)

    s['forged'] = dstats['data']['blocks']['produced']
    #s['missed'] = dstats['data']['blocks']['missed']
    s['missed'] = 0 # temp fix
    s['rank'] = dstats['data']['rank']
    #s['productivity'] = dstats['data']['production']['productivity']
    s['productivity'] = 100 # temp fix
    s['handle'] = dstats['data']['username']
    s['votes'] = "{:.2f}".format(int(dstats['data']['votes'])/100000000)
    s['rewards'] = dstats['data']['forged']['total']
    s['approval'] = dstats['data']['production']['approval']
    s['lastforged_no'] = dstats['data']['blocks']['last']['height']
    s['lastforged_id'] = dstats['data']['blocks']['last']['id']
    s['lastforged_ts'] = dstats['data']['blocks']['last']['timestamp']['human']
    s['lastforged_unix'] = dstats['data']['blocks']['last']['timestamp']['unix']
    s['lastforged_ago'] = "{:.2f}".format(time.time() - s['lastforged_unix'])
    if data.network in ['ark_mainnet', 'ark_devnet']:
        if s['rank'] <= 51:
            s['forging'] = 'Forging'
        else:
            s['forging'] = 'Standby'

    if data.network in ['solar_mainnet', 'solar_devnet']:
        if s['rank'] <= 53:
            s['forging'] = 'Forging'
        else:
            s['forging'] = 'Standby'

    snekdb = SnekDB(data.database_user, data.network, data.delegate)
    voter_ledger = snekdb.voters().fetchall()

    voter_stats = []
    ld          = dict((addr,(pend,paid)) for addr, pend, paid, r in voter_ledger)
    votetotal   = int(dstats['data']['votes'])
    voter_data  = client.delegates.voters(data.delegate)
    for _data in voter_data['data']:
        _sply = "{:.2f}".format(int(_data['balance'])*100/votetotal)
        _addr = _data['address']
        voter_stats.append([_addr,ld[_addr][0], ld[_addr][1], _sply])

    s['voters'] = voter_data['meta']['totalCount']

    node_sync_data = client.node.syncing()
    s['synced'] = 'Syncing' if node_sync_data['data']['syncing'] else 'Synced'
    s['behind'] = node_sync_data['data']['blocks']
    s['height'] = node_sync_data['data']['height']

    if data.pool_version == "original":
        return render_template('index.html', node=s, row=voter_stats, n=navbar)
    else:
        return render_template('geops_index.html', node=s, row=voter_stats, n=navbar)


@app.route('/payments')
def payments():
    s = {}
    dstats = client.delegates.get(data.public_key)
    s['handle'] = dstats['data']['username']
    snekdb = SnekDB(data.database_user, data.network, data.delegate)
    data_out = snekdb.transactions().fetchall()
    tx_data = []
    for i in data_out:
        data_list = [i[0], int(i[1]), i[2], i[3]]
        tx_data.append(data_list)

    if data.pool_version == 'original':
       return render_template('payments.html', row=tx_data, n=navbar)
    else:
       return render_template('geops_payments.html', row=tx_data, n=navbar)

'''
@app.route('/webhook', methods=['POST'])
def webhook():
    hook_data = json.loads(request.data)
    authorization = request.headers['Authorization']
    token = authorization+second

    if token == webhookToken:
        # do something with the data like store in database
        block = [[hook_data['data']['id'], hook_data['data']['timestamp'], hook_data['data']['reward'],
                 hook_data['data']['totalFee'], hook_data['data']['height']]]

        # store block to get allocated by tbw
        snekdb = SnekDB(data['dbusername'])
        snekdb.storeBlocks(block)
        return "OK"

    # Token does not match
    return '', status.HTTP_401_UNAUTHORIZED
'''

if __name__ == '__main__':
    data = Config()
    network = Network(data.network)
    u = Util(data.network)
    client = u.get_client(network.api_port)
    navbar = {
       'dname': data.delegate,
       'proposal': data.proposal,
       'explorer': data.explorer,
       'coin': data.coin}
    app.run(host=data.pool_ip, port=data.pool_port)
