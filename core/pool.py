import time
from functools import cmp_to_key

from config.config import Config
from flask import Flask, render_template, request
from flask_api import status
from network.network import Network
from util.sql import SnekDB
from util.util import Util
from lowercase_booleans import true, false

app = Flask(__name__)


def get_round(height):
    mod = divmod(height,network.delegates)
    return (mod[0] + int(mod[1] > 0))


def get_yield(netw_height, dblocks):
    drounds = dblocks['meta']['count'] #number of forged blocks 

    missed = 0
    forged = 0
    netw_round = get_round(netw_height)
    last_forged_round = get_round(dblocks['data'][0]['height'])

    if netw_round > last_forged_round + 1:
        missed += netw_round - last_forged_round - 1
    else:
        forged += 1

    if drounds > 1:
        for i in range(0, drounds - 1):
            cur_round = get_round(dblocks['data'][i]['height'])
            prev_round = get_round(dblocks['data'][i + 1]['height'])
            if prev_round < cur_round - 1:
                if cur_round - prev_round - 1 > drounds - missed - forged:
                    missed += drounds - missed - forged
                    break
                else:
                    missed += cur_round - prev_round - 1
            else:
                forged += 1

    yield_over_drounds = "{:.2f}".format(round((forged * 100)/(forged + missed)))
    return yield_over_drounds


@app.route('/')
def index():
    stats = {}
    ddata = client.delegates.get(data.public_key)

    stats['forged'] = ddata['data']['blocks']['produced']
    #s['missed'] = dstats['data']['blocks']['missed']
    #s['missed'] = 0 # temp fix
    stats['rank'] = ddata['data']['rank']
    #s['productivity'] = dstats['data']['production']['productivity']
    #s['productivity'] = 100 # temp fix
    stats['handle'] = ddata['data']['username']
    stats['wallet'] = ddata['data']['address']
    stats['votes'] = "{:.2f}".format(int(ddata['data']['votes'])/data.atomic)
    stats['rewards'] = ddata['data']['forged']['total']
    stats['approval'] = ddata['data']['production']['approval']
    
    # get all forged blocks in reverse chronological order, first page, max 100 as default
    dblocks = client.delegates.blocks(data.delegate)
    stats['lastforged_no'] = dblocks['data'][0]['height']
    stats['lastforged_id'] = dblocks['data'][0]['id']
    stats['lastforged_ts'] = dblocks['data'][0]['timestamp']['human']
    stats['lastforged_unix'] = dblocks['data'][0]['timestamp']['unix']
    age = divmod(int(time.time() - stats['lastforged_unix']), 60)
    stats['lastforged_ago'] = "{0}:{1}".format(age[0],age[1])
    stats['forging'] = 'Forging' if stats['rank'] <= network.delegates else 'Standby'

    snekdb = SnekDB(data.database_user, data.network, data.delegate)
    voters = snekdb.voters().fetchall()

    voter_stats = []
    pend_total = 0
    paid_total = 0
    ld         = dict((addr,(pend,paid)) for addr, pend, paid, rate in voters)
    votetotal  = int(ddata['data']['votes'])
    vdata      = client.delegates.voters(data.delegate)
    for _data in vdata['data']:
        if _data['address'] in ld:
            _sply = "{:.2f}".format(int(_data['balance'])*100/votetotal) if votetotal > 0 else "-"
            _addr = _data['address']
            voter_stats.append([_addr,ld[_addr][0], ld[_addr][1], _sply])
            pend_total += ld[_addr][0]
            paid_total += ld[_addr][1]

    reverse_key = cmp_to_key(lambda a, b: (a < b) - (a > b))
    voter_stats.sort(key=lambda rows: (reverse_key(rows[3]),rows[0]))
    voter_stats.insert(0,["Total",pend_total, paid_total, "100"])

    stats['voters'] = vdata['meta']['totalCount']

    node_sync_data = client.node.syncing()
    stats['synced'] = 'Syncing' if node_sync_data['data']['syncing'] else 'Synced'
    stats['behind'] = node_sync_data['data']['blocks']
    stats['height'] = node_sync_data['data']['height']

    stats['yield'] = get_yield(stats['height'], dblocks)

    if data.pool_version == "original" or not data.pool_version:
        return render_template('index.html', node=stats, row=voter_stats, n=navbar)
    else:
        return render_template(data.pool_version + '_index.html', node=stats, row=voter_stats, n=navbar)


@app.route('/payments')
def payments():
    snekdb = SnekDB(data.database_user, data.network, data.delegate)
    data_out = snekdb.transactions().fetchall()

    tx_data = []
    for i in data_out:
        data_list = [i[0], int(i[1]), i[2], i[3]]
        tx_data.append(data_list)

    if data.pool_version == "original" or not data.pool_version:
       return render_template('payments.html', row=tx_data, n=navbar)
    else:
       return render_template(data.pool_version + '_payments.html', row=tx_data, n=navbar)

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
       'proposalx': data.proposalx,
       'proposalxlang': data.proposalxlang,
       'explorer': network.explorer if ((data.explorer is None) or (data.explorer == '')) else data.explorer,
       'coin': network.coin}

    app.run(host=data.pool_ip, port=data.pool_port)
