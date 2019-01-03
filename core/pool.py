from ark import ArkClient
from flask import Flask, render_template, request
from flask_api import status
import json
from util.sql import SnekDB

from pathlib import Path
pool_path = Path().resolve().parent


def parse_pool():

    with open(pool_path / 'config/pool.json') as data_file:
        d = json.load(data_file)
    with open(pool_path / 'config/networks.json') as network_file:
        n = json.load(network_file)
    return d, n


def get_client(ip="localhost"):
    port = network[data['network']]['port']
    return ArkClient('http://{0}:{1}/api/'.format(ip, port))


app = Flask(__name__)


@app.route('/')
def index():    
    s = {} 
    pkey = data['pubkey']
    dstats = client.delegates.get(pkey)

    s['forged'] = dstats['data']['blocks']['produced']
    s['missed'] = dstats['data']['blocks']['missed']
    s['rank'] = dstats['data']['rank']
    s['productivity'] = dstats['data']['production']['productivity']
    if data['network'] in ['ark_mainnet', 'ark_devnet']:
        if s['rank'] <= 51:
            s['forging'] = 'Forging'
        else:
            s['forging'] = 'Standby'

    # s['votes'] = dstats['data']['votes']
    snekdb = SnekDB(data['dbusername'])
    voter_data = snekdb.voters().fetchall()
    s['votes'] = len(voter_data)
    
    if poolVersion == "original":
        return render_template('index.html', node=s, row=voter_data, n=navbar)
    else:
        return render_template('geops_index.html', node=s, row=voter_data, n=navbar)


@app.route('/payments')
def payments():
    snekdb = SnekDB(data['dbusername'])
    data_out = snekdb.transactions().fetchall()
    tx_data = []
    for i in data_out:
        data_list = [i[0], int(i[1]), i[2], i[3]]
        tx_data.append(data_list)
    
    if poolVersion == 'original':
       return render_template('payments.html', row=tx_data, n=navbar)
    else:
       return render_template('geop_payments.html', row=tx_data, n=navbar)
        

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


if __name__ == '__main__':
    data, network = parse_pool()
    #snekdb = SnekDB(data['dbusername'])
    webhookToken = data['webhook_token']
    poolVersion = data['pool_version']
    first, second = webhookToken[:len(webhookToken) // 2], webhookToken[len(webhookToken) // 2:]
    client = get_client()
    navbar = {
       'dname': data['delegate'],
       'proposal': data['proposal'],
       'explorer': data['explorer'],
       'coin': data['coin']}
    
    app.run(host=data['pool_ip'], port=data['pool_port'])
