from flask import Flask, render_template
import json
from snek.snek import SnekDB
from park.park import Park

from pathlib import Path
pool_path = Path().resolve().parent

def parse_pool():

    with open(pool_path / 'config/pool.json') as data_file:
        data = json.load(data_file)
    with open(pool_path / 'config/networks.json') as network_file:
        network = json.load(network_file)
        
    return data, network

def get_network(d, n, ip="localhost"):

    return Park(
        ip,
        n[d['network']]['port'],
        n[d['network']]['nethash'],
        n[d['network']]['version']
    )

app = Flask(__name__)

@app.route('/')
def index():    
    s = {} 
    pkey = data['pubkey']
    params = {"publicKey": pkey}
    dstats = park.delegates().delegate(params)
    
    s['forged'] = dstats['delegate']['producedblocks']
    s['missed'] = dstats['delegate']['missedblocks']
    s['rank'] = dstats['delegate']['rate']
    s['productivity'] = dstats['delegate']['productivity']
    if data['network'] in ['ark','dark','kapu','dkapu','persona','persona-t']:
        if s['rank'] <= 51:
            s['forging'] = 'Forging'
        else:
            s['forging'] = 'Standby'
    elif data['network'] in ['lwf','lwf-t','oxy','oxy-t']:
        if s['rank'] <= 201:
            s['forging'] = 'Forging'
        else:
            s['forging'] = 'Standby'
    elif data['network'] in ['shift','shift-t','ripa', 'onz','onz-t']:
        if s['rank'] <= 101:
            s['forging'] = 'Forging'
        else:
            s['forging'] = 'Standby'

    s['votes'] = len(park.delegates().voters(pkey)['accounts'])
    
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
    park = get_network(data, network)
    navbar = {
       'dname': data['delegate'],
       'proposal': data['proposal'],
       'explorer': data['explorer'],
       'coin': data['coin']}
    
    app.run(host=data['pool_ip'])
