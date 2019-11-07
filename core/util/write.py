import os
import json
from Naked.toolshed.shell import muterun_js

class JsWrite():
    
    def write(network, passphrase, secondphrase, publickey, recipientid, nonce, vendor, amount, fee):
        f = open("tx.js", "a")
        f.writelines("const fs = require('fs')\n")
        f.writelines("const { Transactions, Managers } = require('@arkecosystem/crypto');\n")
        f.writelines("Managers.configManager.getMilestone().aip11 = true\n")
        f.writelines("Managers.configManager.config.network.pubKeyHash = "+network+";\n")
        f.writelines("var tx = Transactions.BuilderFactory.transfer().network("+network+").nonce("+nonce+").senderPublicKey("+publickey+").recipientId("+recipientid+").fee("+fee+").amount("+amount+").expiration(0).vendorField("+vendor+")\n")
        f.writelines("tx.sign("+passphrase+");\n")
        f.writelines("var jsonData = tx.build().toJson()\n")
        f.writelines("var jsonContent = JSON.stringify(jsonData);\n")
        f.writelines("fs.writeFile('output.json', jsonContent, 'utf8', function (err) {\n")
        f.writelines("    if (err) {\n")
        f.writelines(" console.log('An error occured while writing JSON Object to File.');\n")
        f.writelines(" return console.log(err);\n")
        f.writelines("    }\n")
        f.writelines("});\n")
        f.close()
        
    
    def run():
        response = muterun_js('tx.js')
        filename = 'output.json'

        if filename:
            with open(filename, 'r') as f:
            datastore = json.load(f)
        return datastore
          
    def delete():
        os.remove('output.json')
        os.remove('tx.js')
