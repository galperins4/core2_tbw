from config.config import Config
from flask import Flask, jsonify, request
from network.network import Network
from util.sql import SnekDB
from util.util import Util


app = Flask(__name__)


@app.route('/updateShare', methods=['POST'])
def share():
    req_data = request.get_json()
    address = req_data['address']
    new_share = req_data["share"]
    snekdb = SnekDB(data.database_user, data.network, data.delegate)
    snekdb.updateVoterShare(address, new_share)

    msg = {"success": "share updated"}
    return jsonify(msg)


if __name__ == '__main__':
    data = Config()
    network = Network(data.network)
    u = Util(data.network)
    app.run(host=data.pool_ip, port=data.custom_port)
