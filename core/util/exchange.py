import json
import math
import requests
from lowercase_booleans import false


class Exchange:
    def __init__(self, database, config):
        self.config = config
        self.database = database
        #self.provider = "ChangeNow"
        self.provider = self.config.provider
        self.atomic = 100000000

        
    def truncate(self,f, n):
        return math.floor(f * 10 ** n) / 10 ** n
   

    def exchange_select(self, address, amount):
        if self.provider == "ChangeNow":
            pay = self.process_changenow_exchange(address,amount)
        elif self.provider == "SimpleSwap":
            pay = self.process_simpleswap_exchange(address,amount)
        else:
            pay = address
            
        return pay
    
    def process_simpleswap_exchange(self, address, amount):
        fixed = false
        print("Processing Exchange")
        print("Original Amount", amount)
        amount = self.truncate((amount / self.atomic),4)
        print("Exchange Amount:", amount)
        url = 'https://t1mi6dwix2.execute-api.us-west-2.amazonaws.com/Test/exchange'
        data_in = {"fixed": fixed,
                   "currency_from": self.config.convert_from,
                   "currency_to": self.config.convert_to,
                   "address_to": self.config.address_to,
                   "amount": str(amount),
                   "user_refund_address":address}
        
        res_bytes={}
        res_bytes['data'] = json.dumps(data_in).encode('utf-8')
        
        try:
            r = requests.get(url, params=res_bytes)
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
