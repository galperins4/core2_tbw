from flask import Flask, request
from flask_api import status
from tbw import parse_config
from util.sql import SnekDB
import json

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    hook_data = json.loads(request.data)
    authorization = request.headers['Authorization']
    token = authorization+second

    if token == webhookToken:
        # do something with the data like store in database
        block = [hook_data['data']['id'], hook_data['data']['timestamp'], hook_data['data']['reward'],
                 hook_data['data']['totalFee'], hook_data['data']['height']]

        # store block to get allocated by tbw
        snekdb.storeBlocks(block)

        return "OK"

    # Token does not match
    return '', status.HTTP_401_UNAUTHORIZED


if __name__ == '__main__':
    data, network = parse_config()
    snekdb = SnekDB(data['dbusername'])
    webhookToken = data['webhook_token']

    first, second = webhookToken[:len(webhookToken)//2], webhookToken[len(webhookToken)//2:]

    app.run(host=data['webhook_ip'], port=data['webhook_port'])
