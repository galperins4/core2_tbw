#!/usr/bin/env python

from snek.snek import SnekDB
from snek.ark import ArkDB
import time
import json
from pathlib import Path
import os.path

tbw_path = Path().resolve().parent
atomic = 100000000
transaction_fee = .1 * atomic
transfer_size = 80

def parse_config():
    """
    Parse the config.json file and return the result.
    """
    with open(tbw_path / 'config/config.json') as data_file:
        data = json.load(data_file)
        
    with open(tbw_path / 'config/networks.json') as network_file:
        network = json.load(network_file)

    return data, network

def allocate(lb):
    
    # create temp log / export output for block  rewards
    log = {}
    rewards_check = 0
    voter_check = 0
    delegate_check = 0
    
    block_voters = get_voters()

    # get total votes
    approval = sum(int(item[1]) for item in block_voters)

    # get block reward
    block_reward = lb[2]
    fee_reward = lb[3]
    total_reward = block_reward+fee_reward

    # calculate delegate/reserve/other shares
    for k, v in data['keep'].items():
        if k == 'reserve':
            keep = (int(block_reward * v)) + fee_reward
        else:
            keep = (int(block_reward * v))

        # assign  shares to log and rewards tracking
        keep_addr = data['pay_addresses'][k]
        log[keep_addr] = keep
        snekdb.updateDelegateBalance(keep_addr, keep)
        
        # increment delegate_check for double check
        delegate_check += keep

    # calculate voter share
    vshare = block_reward * data['voter_share']

    # loop through the current voters and assign share
    for i in block_voters:

        # convert balance from str to int
        bal = int(i[1])

        # filter out 0 balances for processing
        if bal > 0:
            share_weight = bal / approval  # calc share rate
            
            # calculate block reward
            reward = int(share_weight * vshare)
            
            # populate log for block export records
            log[i[0]] = reward
            
            # update reserve from blacklist assign
            if i[0] == data["blacklist_assign"]:
                snekdb.updateDelegateBalance(i[0], reward)
            else:
                #add voter reward to sql database
                snekdb.updateVoterBalance(i[0], reward)

            # voter and rewards check
            voter_check += 1
            rewards_check += reward

    print(f"""Processed Block: {lb[4]}\n
    Voters processed: {voter_check}
    Total Approval: {approval}
    Voters Rewards: {rewards_check}
    Delegate Reward: {delegate_check}
    Voter + Delegate Rewards: {rewards_check + delegate_check}
    Total Block Rewards: {total_reward}""")

    #mark as processed
    snekdb.markAsProcessed(lb[4])

def manage_folders():
    sub_names = ["error"]
    for sub_name in sub_names:
        os.makedirs(os.path.join('output', sub_name), exist_ok=True)

def white_list(voters):
    w_adjusted_voters=[]
    for i in voters:
        if i[0] in data["whitelist_addr"]:
            w_adjusted_voters.append((i[0], i[1]))
            
    return w_adjusted_voters


def black_list(voters):
    #block voters and distribute to voters
    if data["blacklist"] == "block":
        bl_adjusted_voters = []
        for i in voters:
            if i[0] in data["blacklist_addr"]:
                bl_adjusted_voters.append((i[0], 0))
            else:
                bl_adjusted_voters.append((i[0], i[1]))
    
    #block voters and keep in reserve account
    elif data["blacklist"] == "assign":
        bl_adjusted_voters = []
        accum = 0
        
        for i in voters:
            if i[0] in data["blacklist_addr"]:
                accum += i[1]
            else:
                bl_adjusted_voters.append((i[0], i[1]))
        
        bl_adjusted_voters.append((data["blacklist_assign"], accum))

    else:
        bl_adjusted_voters = voters

    return bl_adjusted_voters

def voter_min(voters):
    min_wallet = int(data['vote_min'] * atomic)
    
    if min_wallet > 0:
        min_adjusted_voters = []
        for i in voters:
            if i[1] < min_wallet:
                min_adjusted_voters.append((i[0], 0))
            else:
                min_adjusted_voters.append((i[0],i[1]))
    else:
        min_adjusted_voters = voters
        
    return min_adjusted_voters

def voter_cap(voters):

    # cap processing
    max_wallet = int(data['vote_cap'] * atomic)
    
    if max_wallet > 0:
        cap_adjusted_voters = []
        for i in voters:
            if i[1] > max_wallet and i[0] != data["blacklist_assign"]:
                cap_adjusted_voters.append((i[0], max_wallet))
            else:
                cap_adjusted_voters.append((i[0],i[1]))
                
    else:
        cap_adjusted_voters = voters

    return cap_adjusted_voters

def anti_dilute(voters):
    # get unpaid balances and wallets
    b = snekdb.voters().fetchall()
    undilute =[]
    
    if b:
        
        unpaid= {}
        for i in b:
            unpaid[i[0]] = i[1]
    
        for j in voters:
            adj = j[1] + unpaid[j[0]]
            undilute.append((j[0], adj))
    
    else: 
        undilute = voters
    
    return undilute

def get_voters():

    #get voters
    initial_voters = arkdb.voters()
    
    if data['whitelist'] == 'Y':
        bl = white_list(initial_voters)
    else:
        #process blacklist, voter cap, and voter min:
        bl_adjust = black_list(initial_voters)
        bl_adjust_two = voter_cap(bl_adjust)
        bl = voter_min(bl_adjust_two)
   
    snekdb.storeVoters(bl)    
    
    # anti-dulition
    block_voters = anti_dilute(bl)
    
    return block_voters

def get_rewards():
    
    rewards = []
    for k, v in data['pay_addresses'].items():
        rewards.append(v)
    
    snekdb.storeRewards(rewards) 

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
                #net = row[1] - get_del_fee(delegate_tx_fee)
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
                #res += (fix + get_del_fee(delegate_tx_fee))
            
            else:
                net_fix = fix - transaction_fee
                #net_fix = fix - get_del_fee(delegate_tx_fee)
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
                    #net_pay = del_pay_adjust - get_del_fee(delegate_tx_fee)
    
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
                #net = row[1] - get_del_fee(delegate_tx_fee)
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
        #v_count = len([i for i in snekdb.voters() if (i[1]>min and (i[1]-get_del_fee(delegate_tx_fee))>0)])
    
    adj_factor = v_count / t_count
                   
    if v_count>0:
        print('Payout started!')
        
        tx_count = v_count+d_count
        # calculate tx fees needed to cover run in satoshis
        tx_fees = tx_count * int(transaction_fee)
        #tx_fees = tx_count * get_del_fee(delegate_tx_fee)
    
        # process delegate rewards
        process_delegate_pmt(tx_fees, adj_factor)
        
        # process voters 
        process_voter_pmt(min)

def interval_check(bc):
    if bc % data['interval'] == 0:
        # check if there is an unpaid balance for voters
        total = 0
        # get voter balances
        r = snekdb.voters()
        for row in r:
            total += row[1]
                
        print("Total Voter Unpaid:",total)
        
        if total > 0:
            return True
        else: 
            return False
        
def initialize():
    print("First time setup - initializing SQL database....")
    # initalize sqldb object
    snekdb.setup()
    
    # connect to DB and grab all blocks
    print("Importing all prior forged blocks...")
    all_blocks = arkdb.blocks("yes")
        
    # store blocks
    print("Storing all historical blocks and marking as processed...")
    snekdb.storeBlocks(all_blocks)
        
    # mark all blocks as processed
    for row in all_blocks:
        if row[4] <= data['start_block']:
            snekdb.markAsProcessed(row[4])
        
    # set block count to rows imported
    block_count = len(all_blocks)
    p_count = block_counter()
                
    print("Imported block count:", block_count)
    print("Processed block count:", p_count)
    
    # initialize voters and delegate rewards accounts
    get_voters()
    get_rewards()
    
    print("Initial Set Up Complete. Please re-run script!")
    quit()

def block_counter():
    c = snekdb.processedBlocks().fetchall()
    return len(c)

def get_del_fee(c):
    s = v_msg + transfer_size
    f = int(s*c*atomic)
    return f

if __name__ == '__main__':
    # check for folders needed
    manage_folders()  
    
    # get config data
    data, network = parse_config()
    global delegate_tx_fee
    global v_msg
    
    delegate_tx_fee = data['override_fee']
    v_msg = len(data['voter_msg'])

    # initialize db connection
    
    #check for special usernames needed for lisk forks
    arkdb = ArkDB(network[data['network']]['db'], data['dbusername'], network[data['network']]['db_pw'], data['publicKey'])
    
    # check to see if ark.db exists, if not initialize db, etc
    if os.path.exists(tbw_path / 'ark.db') == False:    
        snekdb = SnekDB(data['dbusername'])
        initialize()
    
    # check for new rewards accounts to initialize if any changed
    snekdb = SnekDB(data['dbusername'])
    get_rewards()

    # set block count        
    block_count = block_counter()

    # processing loop
    while True:
        # get last 50 blocks
        blocks = arkdb.blocks()
        # store blocks
        snekdb.storeBlocks(blocks)
        # check for unprocessed blocks
        unprocessed = snekdb.unprocessedBlocks().fetchall()
          
        # query not empty means unprocessed blocks
        if unprocessed:
            for b in unprocessed:
                
                #allocate
                allocate(b)
                #get new block count
                block_count = block_counter()
                
                #increment count
                print('\n')
                print(f"Current block count : {block_count}")

                check = interval_check(block_count)
                if check:
                    payout()
                     
                print('\n' + 'Waiting for the next block....' + '\n')
                # sleep 5 seconds between allocations
                time.sleep(5)

        # pause 30 seconds between runs
        time.sleep(data["block_check"])
