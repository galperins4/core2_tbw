import json
import math
import requests
import time
from lowercase_booleans import false


class Exchange:
    def __init__(self, database, config):
        self.config = config
        self.database = database
        self.atomic = 100000000

        
    def truncate(self,f, n):
        return math.floor(f * 10 ** n) / 10 ** n
   

    def exchange_select(self, index, address, amount, provider):
        if provider == "ChangeNow":
            pay = self.process_changenow_exchange(index,address,amount)
        elif provider == "SimpleSwap":
            pay = self.process_simpleswap_exchange(index,address,amount)
        else:
            pay = address
        time.sleep(5)
        return pay
    
    def process_simpleswap_exchange(self, index, address, amount):
        fixed = false
        print("Processing Exchange")
        amount = self.truncate((amount / self.atomic),4)
        print("Exchange Amount:", amount)
        url = 'https://t1mi6dwix2.execute-api.us-west-2.amazonaws.com/Test/exchange'
        data_in = {"fixed": fixed,
                   "currency_from": self.config.convert_from[index],
                   "currency_to": self.config.convert_to[index],
                   "address_to": self.config.address_to[index],
                   "amount": str(amount),
                   "user_refund_address":address}
        
        res_bytes={}
        res_bytes['data'] = json.dumps(data_in).encode('utf-8')
        
        try:
            r = requests.get(url, params=res_bytes)
            if r.json()['status'] == "success":
                payin_address = r.json()['payinAddress']
                exchangeid = r.json()['exchangeId']
                self.database.storeExchange(address, payin_address, self.config.address_to[index], amount, exchangeid)
                print("Exchange Success") 
            else:
                payin_address = address
                print("Exchange Fail")
        except:
            payin_address = address
            print("Exchange Fail")
    
        print("Pay In Address", payin_address)
        return payin_address
    
    
    def process_changenow_exchange(self, index, address, amount):
        print("Processing Exchange")
        amount = self.truncate((amount / self.atomic),4)
        print("Exchange Amount:", amount)
        url = 'https://mkcnus24ib.execute-api.us-west-2.amazonaws.com/Test/exchange'
        data_in = {"fromCurrency": self.config.convert_from[index],
                   "toCurrency": self.config.convert_to[index],
                   "toNetwork": self.config.network_to[index],
                   "address": self.config.address_to[index],
                   "fromAmount": str(amount),
                   "refundAddress":address}
        try:
            r = requests.get(url, params=data_in)
            if r.json()['status'] == "success":
                payin_address = r.json()['payinAddress']
                exchangeid = r.json()['exchangeId']
                self.database.storeExchange(address, payin_address, self.config.address_to[index], amount, exchangeid)
                print("Exchange Success") 
            else:
                payin_address = address
                print("Exchange Fail")
        except:
            payin_address = address
            print("Exchange Fail")
    
        return payin_address
