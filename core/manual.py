#!/usr/bin/env python
from snek.snek import SnekDB
from snek.ark import ArkDB
from tbw import parse_config

atomic = 100000000
transaction_fee = .1 * atomic

def get_dbname():
    ark_fork = ['ark','dark','kapu','dkapu','persona-t','ripa', 'persona']
    if  data['network'] in ark_fork:
        uname = data['dbusername']
    else:
        uname = network[data['network']]['db_user']
        
    return uname

def del_address(addr):
    msg = "default"
    
    for k,v in data['pay_addresses'].items():
        if addr == v:
            msg = k + " - True Block Weight"
    
    return msg

def process_voter_pmt(min):
    # process voters 
    voters = snekdb.voters().fetchall()
    for row in voters:
        if row[1] > min:               
               
            msg = data["voter_msg"]
            
            if data['cover_tx_fees'] == "Y":
                # update staging records
                snekdb.storePayRun(row[0], row[1], msg)
                # adjust sql balances
                snekdb.updateVoterPaidBalance(row[0])
            
            else:
                net = row[1] - transaction_fee
                #only pay if net payment is greater than 0, accumulate rest
                if net > 0:
                    snekdb.storePayRun(row[0], net, msg)
                    snekdb.updateVoterPaidBalance(row[0])
                
def fixed_deal():
    res = 0
    private_deals = data['fixed_deal_amt']
    
    # check to make sure fixed payment addresses haven't unvoted 
    fix_check = arkdb.voters()
    tmp = {}
    for i in fix_check:
        tmp[i[0]] = i[1]
    
    for k,v in private_deals.items():
        if k in tmp.keys() and tmp[k]>0:
            msg = "Goose Voter - True Block Weight-F"
            # update staging records
            fix = v * atomic
            if data['cover_tx_fees'] == 'Y':
                snekdb.storePayRun(k, fix, msg)
                #accumulate fixed deals balances
                res += (fix + transaction_fee)
            
            else:
                net_fix = fix - transaction_fee
                snekdb.storePayRun(k, net_fix, msg)
                #accumulate fixed deals balances
                res += (net_fix)
            
    return res

def process_delegate_pmt(fee, adjust):
    # process delegate first
    delreward = snekdb.rewards().fetchall()        
    for row in delreward:
        if row[0] == data['pay_addresses']['reserve']:
            
            #adjust reserve payment by factor to account for not all tx being paid due to tx fees or min payments
            del_pay_adjust = int(row[1]*adjust)
            
            if data['fixed_deal'] == 'Y':
                amt = fixed_deal()
                if data['cover_tx_fees'] == 'Y':
                    totalFees = amt + fee
                else:
                    totalFees = amt
                
                net_pay = del_pay_adjust - totalFees
            
            else:
                if data['cover_tx_fees'] == 'Y':
                    net_pay = del_pay_adjust - fee
                else:
                    net_pay = del_pay_adjust - transaction_fee
    
            if net_pay <= 0:
                # delete staged payments to prevent duplicates
                snekdb.deleteStagedPayment()
                
                print("Not enough in reserve to cover transactions")
                print("Update interval and restart")
                quit()
                
            # update staging records
            snekdb.storePayRun(row[0], net_pay, del_address(row[0]))
            
            #adjust sql balances
            snekdb.updateDelegatePaidBalance(row[0], del_pay_adjust)
                
        else:
            if data['cover_tx_fees'] == 'N':
                # update staging records
                net = row[1] - transaction_fee
                if net > 0:
                    snekdb.storePayRun(row[0], net, del_address(row[0]))
                    # adjust sql balances
                    snekdb.updateDelegatePaidBalance(row[0], row[1])
                
            else: 
                if row[1] > 0:
                    snekdb.storePayRun(row[0], row[1], del_address(row[0]))
                    # adjust sql balances
                    snekdb.updateDelegatePaidBalance(row[0], row[1])

def payout():
    min = int(data['min_payment'] * atomic)

    # count number of transactions greater than payout threshold
    d_count = len([j for j in snekdb.rewards() if j[1]>0])
    
    #get total possible payouts before adjusting for accumulated payments
    t_count = len([i for i in snekdb.voters() if i[1]>0])
    
    if data['cover_tx_fees'] == 'Y':
        v_count = len([i for i in snekdb.voters() if i[1]>min])
    else:
        v_count = len([i for i in snekdb.voters() if (i[1]>min and (i[1]-transaction_fee)>0)])
    
    adj_factor = v_count / t_count
                   
    if v_count>0:
        print('Payout started!')
        
        tx_count = v_count+d_count
        # calculate tx fees needed to cover run in satoshis
        tx_fees = tx_count * int(transaction_fee)
    
        # process delegate rewards
        process_delegate_pmt(tx_fees, adj_factor)
        
        # process voters 
        process_voter_pmt(min)

if __name__ == '__main__':
    data, network = parse_config()
    snekdb = SnekDB(data['dbusername'])
    
    username = get_dbname()
    arkdb = ArkDB(network[data['network']]['db'], username, network[data['network']]['db_pw'], data['publicKey'])
    payout()
