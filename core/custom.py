from ark import ArkClient
from flask import Flask, jsonify, request
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


@app.route('/updateShare', methods=['POST'])
def share():
    req_data = request.get_json()
    address = req_data['address']
    new_share = req_data["share"]
    snekdb.updateVoterShare(address, new_share)

    msg = {"success": "share updated"}
    return jsonify(msg)


if __name__ == '__main__':
    data, network = parse_pool()
    snekdb = SnekDB(data['dbusername'])
    client = get_client()
    app.run(host=data['pool_ip'], port=data['custom_port'])
