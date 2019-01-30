from flask import Flask, jsonify, request
import json
from util.sql import SnekDB
from util.util import Util

from pathlib import Path
pool_path = Path().resolve().parent

app = Flask(__name__)


@app.route('/updateShare', methods=['POST'])
def share():
    req_data = request.get_json()
    address = req_data['address']
    new_share = req_data["share"]
    snekdb = SnekDB(data['dbusername'])
    snekdb.updateVoterShare(address, new_share)

    msg = {"success": "share updated"}
    return jsonify(msg)


if __name__ == '__main__':
    u = Util()
    data, network = u.parse_pool()
    app.run(host=data['pool_ip'], port=data['custom_port'])
