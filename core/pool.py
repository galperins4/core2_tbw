from ark import ArkClient
from flask import Flask, render_template
import json
from util.sql import SnekDB

from pathlib import Path
pool_path = Path().resolve().parent

def parse_pool():

    with open(pool_path / 'config/pool.json') as data_file:
        data = json.load(data_file)
    with open(pool_path / 'config/networks.json') as network_file:
        network = json.load(network_file)
        
    return data, network

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
    if data['network'] in ['ark_mainnet','ark_devnet']:
        if s['rank'] <= 51:
            s['forging'] = 'Forging'
        else:
            s['forging'] = 'Standby'

    s['votes'] = dstats['data']['votes']
    
    voter_data = snekdb.voters().fetchall()
    
    return render_template('index.html', node=s, row=voter_data, n=navbar)

@app.route('/payments')
def payments():
    
    data_out = snekdb.transactions().fetchall()
    tx_data=[]
    for i in data_out:
        l = [i[0], int(i[1]), i[2], i[3]]
        tx_data.append(l)
 
    return render_template('payments.html', row=tx_data, n=navbar)

if __name__ == '__main__':
    data, network = parse_pool()
    snekdb = SnekDB(data['dbusername'])
    client = get_client()
    navbar = {
       'dname': data['delegate'],
       'proposal': data['proposal'],
       'explorer': data['explorer'],
       'coin': data['coin']}
    
    app.run(host=data['pool_ip'])
