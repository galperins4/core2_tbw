if __name__ == '__main__':
   
    data = Config()
    network = Network(data.network)
    u = Util(data.network)
    snekdb = SnekDB(data.database_user, data.network, data.delegate)
    exchange = Exchange(snekdb, data)
    
    addresses = [i for i in data.convert_address]
    print(addresses)
    
    for i in addresses:
        if j in data.convert_address:
            index = data.convert_address[j]
            pay_in = exchange.exchange_select(index, i[1], i[2],data.provider[index])
