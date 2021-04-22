from config.config import Config
from network.network import Network
from util.sql import SnekDB
from util.exchange import Exchange
from util.util import Util

if __name__ == '__main__':
   
    data = Config()
    network = Network(data.network)
    u = Util(data.network)
    snekdb = SnekDB(data.database_user, data.network, data.delegate)
    exchange = Exchange(snekdb, data)
    
    addresses = [i for i in data.convert_address]
    
    for i in addresses:
        amount = 50000000000
        if i in data.convert_address:
            index = data.convert_address.index(i)
            pay_in = exchange.exchange_select(index, i, amount,data.provider[index])
            
            #delete exchange record
            new_amount = exchange.truncate(amount/data.atomic,4)
            snekdb.deleteTestExchange(i,pay_in,new_amount)
