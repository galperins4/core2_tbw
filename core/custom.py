from ark import ArkClient
from flask import Flask, jsonify
import json
from snek.snek import SnekDB

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


@app.route('/updateShare', methods=['POST'])
def share():
    snekdb = SnekDB(data['dbusername'])
    req_data = request.get_json()
    address = req_data['address']
    newShare = req_data["share"]
    snekdb.updateVoterShare(address, newShare)

    msg = {"success": "share updated"}
    return jsonify(msg)


if __name__ == '__main__':
    data, network = parse_pool()
    snekdb = SnekDB(data['dbusername'])
    client = get_client()
    app.run(host=data['pool_ip'], port=5002)
