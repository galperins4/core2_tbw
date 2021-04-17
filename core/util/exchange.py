import math
import requests


class Exchange:
    def __init__(self, database, config):
        self.provider = "ChangeNow"
        self.config = config
        self.database = database
        self.atomic = 100000000

        
    def truncate(self,f, n):
        return math.floor(f * 10 ** n) / 10 ** n
   

    def exchange_select(self, address, amount):
        if self.provider == "ChangeNow":
            pay = self.process_changenow_exchange(address,amount)
            return pay
        else:
            pass
    
    
    def process_changenow_exchange(self, address, amount):
        print("Processing Exchange")
        print("Original Amount", amount)
        amount = self.truncate((amount / self.atomic),4)
        print("Exchange Amount:", amount)
        url = 'https://mkcnus24ib.execute-api.us-west-2.amazonaws.com/Test/exchange'
        data_in = {"fromCurrency": self.config.convert_from,
                   "toCurrency": self.config.convert_to,
                   "toNetwork": self.config.network_to,
                   "address": self.config.address_to,
                   "fromAmount": str(amount),
                   "refundAddress":address}
        try:
            r = requests.get(url, params=data_in)
            if r.json()['status'] == "success":
                payin_address = r.json()['payinAddress']
                exchangeid = r.json()['exchangeId']
                self.database.storeExchange(address, payin_address, self.config.address_to, amount, exchangeid)
                print("Exchange Success")   
        except:
            payin_address = address
            print("Exchange Fail")
    
        print("Pay In Address", payin_address)
        return payin_address
