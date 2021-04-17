import math
import requests


class Exchange:
    def __init__(self, config, provider):
        self.provider = provider
        self.config = config
        self.atomic = 100000000

    def truncate(self,f, n):
        return math.floor(f * 10 ** n) / 10 ** n
    
    def process_changenow_exchange(self, address, amount):
        print("Processing Exchange")
        print("Original Amount", amount)
        amount = truncate((amount / self.atomic),4)
        print("Exchange Amount:", amount)
        url = 'https://mkcnus24ib.execute-api.us-west-2.amazonaws.com/Test/exchange'
        data_in = {"fromCurrency": data.convert_from,
                   "toCurrency": data.convert_to,
                   "toNetwork": data.network_to,
                   "address": data.address_to,
                   "fromAmount": str(amount),
                   "refundAddress":address}
        try:
            r = requests.get(url, params=data_in)
            if r.json()['status'] == "success":
                payin_address = r.json()['payinAddress']
                exchangeid = r.json()['exchangeId']
                snekdb.storeExchange(address, payin_address, data.address_to, amount, exchangeid)
                print("Exchange Success")   
        except:
            payin_address = address
            print("Exchange Fail")
    
        print("Pay In Address", payin_address)
        return payin_address
