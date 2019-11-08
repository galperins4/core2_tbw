import os
import json
from Naked.toolshed.shell import muterun_js

class JsWrite:
    
    def __init__(self, p):
        self.path = p+'/core/'
    
    def write(self, network, passphrase, secondphrase, publickey, recipientid, nonce, vendor, amount, fee):
        f = open("tx.js", "w")
        f.writelines("const fs = require('fs')\n")
        f.writelines("const { Transactions, Managers } = require('@arkecosystem/crypto');\n")
        f.writelines("Managers.configManager.getMilestone().aip11 = true\n")
        f.writelines("Managers.configManager.config.network.pubKeyHash = "+network+";\n")
        f.writelines("var tx = Transactions.BuilderFactory.transfer().network("+network+").nonce("+nonce+").senderPublicKey('"+publickey+"').recipientId('"+recipientid+"').fee("+fee+").amount("+amount+").expiration(0).vendorField('"+vendor+"')\n")
        f.writelines("tx.sign('"+passphrase+"');\n")
        if secondphrase is not None:
            f.writelines("    tx.secondSign('"+secondphrase+"');\n")
        f.writelines("var jsonData = tx.build().toJson()\n")
        f.writelines("console.log(JSON.stringify(jsonData));\n")
        f.close()
        
    
    def run(self):
        f = self.path+'tx.js'
        response = muterun_js(f)
        if response.exitcode == 0:
            os.remove(f)
            return json.loads(response.stdout.decode('utf-8'))
        else:
            sys.stderr.write(response.stderr.decode('utf-8'))
