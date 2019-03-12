#!/usr/bin/env python
from util.sql import SnekDB
from util.ark import ArkDB
from util.dynamic import Dynamic
from util.util import Util
from pathlib import Path
import os.path
import time
import sys


tbw_path = Path().resolve().parent
atomic = 100000000


def allocate(lb):
    
    # create temp log / export output for block  rewards
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
            # fixed processing
            if i[0] in data['fixed'].keys():
                fixed_amt = data['fixed'][i[0]] * atomic
                reward = int(fixed_amt/data['interval'])
                treward = int(share_weight * vshare)
                remainder_reward = int(treward - reward)
                delegate_check += remainder_reward
            else:
                # get custom share rate if applicable
                custom_share = snekdb.getVoterShare(i[0]).fetchall()
                cshare = block_reward * custom_share[0][0]

                # get the difference between normal share and custom share
                if custom_share[0][0] == data['voter_share']:
                    reward = int(share_weight * vshare)
                    remainder_reward = 0
                else:
                    treward = int(share_weight * vshare)
                    reward = int(share_weight * cshare)
                    remainder_reward = int(treward - reward)
                    delegate_check += remainder_reward

            # update reserve from blacklist assign
            if i[0] == data["blacklist_assign"]:
                snekdb.updateDelegateBalance(i[0], reward)
            else:
                # add voter reward to sql database
                snekdb.updateVoterBalance(i[0], reward)
                snekdb.updateDelegateBalance(keep_addr, remainder_reward)

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

    # mark as processed
    snekdb.markAsProcessed(lb[4])


def white_list(voters):
    w_adjusted_voters = []
    for i in voters:
        if i[0] in data["whitelist_addr"]:
            w_adjusted_voters.append((i[0], i[1]))
            
    return w_adjusted_voters


def black_list(voters):
    # block voters and distribute to voters
    if data["blacklist"] == "block":
        bl_adjusted_voters = []
        for i in voters:
            if i[0] in data["blacklist_addr"]:
                bl_adjusted_voters.append((i[0], 0))
            else:
                bl_adjusted_voters.append((i[0], i[1]))
    
    # block voters and keep in reserve account
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
                min_adjusted_voters.append((i[0], i[1]))
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
                cap_adjusted_voters.append((i[0], i[1]))
                
    else:
        cap_adjusted_voters = voters

    return cap_adjusted_voters


def anti_dilute(voters):
    # get unpaid balances and wallets
    b_dilute = snekdb.voters().fetchall()
    undilute = []
    
    if b_dilute:
        
        unpaid = {}
        for i in b_dilute:
            unpaid[i[0]] = i[1]
    
        for j in voters:
            adj = j[1] + unpaid[j[0]]
            undilute.append((j[0], adj))
    
    else: 
        undilute = voters
    
    return undilute


def get_voters():

    # get voters
    #initial_voters = arkdb.voters()
    v = client.delegates.voter_balances(delegate_id=data["delegate"])['data']
    initial_voters = [(i,v[i]) for i in v]
    
    
    if data['whitelist'] == 'Y':
        bl = white_list(initial_voters)
    else:
        # process blacklist, voter cap, and voter min:
        bl_adjust = black_list(initial_voters)
        bl_adjust_two = voter_cap(bl_adjust)
        bl = voter_min(bl_adjust_two)
   
    snekdb.storeVoters(bl, data['voter_share'])
    
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
    
    for k, v in data['pay_addresses'].items():
        if addr == v:
            msg = k
    
    return msg


def process_voter_pmt(min_amt):
    # process voters 
    voters = snekdb.voters().fetchall()
    for row in voters:
        if row[1] > min_amt:
               
            msg = data["voter_msg"]
            
            if data['cover_tx_fees'] == "Y":
                # update staging records
                snekdb.storePayRun(row[0], row[1], msg)
                # adjust sql balances
                snekdb.updateVoterPaidBalance(row[0])
            
            else:
                net = row[1] - transaction_fee
                # only pay if net payment is greater than 0, accumulate rest
                if net > 0:
                    snekdb.storePayRun(row[0], net, msg)
                    snekdb.updateVoterPaidBalance(row[0])


def process_delegate_pmt(fee, adjust):
    # process delegate first
    delreward = snekdb.rewards().fetchall()        
    for row in delreward:
        if row[0] == data['pay_addresses']['reserve']:
            
            # adjust reserve payment by factor to account for not all tx being paid due to tx fees or min payments
            del_pay_adjust = int(row[1]*adjust)

            if data['cover_tx_fees'] == 'Y':
                net_pay = del_pay_adjust - fee
            else:
                net_pay = del_pay_adjust - transaction_fee
    
            if net_pay <= 0:
                # check if 100% share node
                if data['voter_share'] == 1.00 and data['cover_tx_fees'] == 'N':
                    # do nothing
                    pass
                else:
                    # delete staged payments to prevent duplicates
                    snekdb.deleteStagedPayment()
                
                    print("Not enough in reserve to cover transactions")
                    print("Update interval and restart")
                    quit()    
            else:
                # update staging records
                snekdb.storePayRun(row[0], net_pay, del_address(row[0]))
            
                # adjust sql balances
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
    minamt = int(data['min_payment'] * atomic)

    # count number of transactions greater than payout threshold
    d_count = len([j for j in snekdb.rewards() if j[1] > 0])
    
    # get total possible payouts before adjusting for accumulated payments
    t_count = len([i for i in snekdb.voters() if i[1] > 0])
    
    if data['cover_tx_fees'] == 'Y':
        v_count = len([i for i in snekdb.voters() if i[1] > minamt])
    else:
        v_count = len([i for i in snekdb.voters() if (i[1] > minamt and (i[1]-transaction_fee) > 0)])
    
    adj_factor = v_count / t_count
                   
    if v_count > 0:
        print('Payout started!')
        
        tx_count = v_count+d_count
        # calculate tx fees needed to cover run in satoshis
        tx_fees = tx_count * int(transaction_fee)
    
        # process delegate rewards
        process_delegate_pmt(tx_fees, adj_factor)
        
        # process voters 
        process_voter_pmt(minamt)


def interval_check(bc):
    if bc % data['interval'] == 0:
        # check if there is an unpaid balance for voters
        total = 0
        # get voter balances
        r = snekdb.voters()
        for row in r:
            total += row[1]
                
        print("Total Voter Unpaid:", total)
        
        if total > 0:
            return True
        else: 
            return False


def initialize():
    print("First time setup - initializing SQL database....")
    # initalize sqldb and arkdb connection object
    snekdb.setup()
    arkdb.open_connection()
    
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
    b_count = len(all_blocks)
    p_count = block_counter()
                
    print("Imported block count:", b_count)
    print("Processed block count:", p_count)
    
    # initialize voters and delegate rewards accounts
    get_voters()
    get_rewards()
    
    arkdb.close_connection()
    print("Initial Set Up Complete. Please re-run script!")
    quit()


def block_counter():
    c = snekdb.processedBlocks().fetchall()
    return len(c)


def share_change():
    # get old share rate
    old = float(input("Enter old share rate in the following format (0.xx): "))
    #get voters
    v = snekdb.voters().fetchall()
    for i in v:
        # look for matches on old value
        if i[3] == old:
            #update share rate
            snekdb.updateVoterShare(i[0],data['voter_share'])
    quit()

if __name__ == '__main__':

    u = Util()
    # get config data
    data, network = u.parse_configs()
    client = u.get_client()

    dynamic = Dynamic(data['dbusername'], data['voter_msg'])
    transaction_fee = dynamic.get_dynamic_fee()
    
    # initialize db connection
    # get database
    arkdb = ArkDB(network[data['network']]['db'], data['dbusername'], network[data['network']]['db_pw'],
                  data['publicKey'])
    
    # check to see if ark.db exists, if not initialize db, etc
    if os.path.exists(tbw_path / 'ark.db') is False:
        snekdb = SnekDB(data['dbusername'])
        initialize()
    
    # check for new rewards accounts to initialize if any changed
    snekdb = SnekDB(data['dbusername'])
    get_rewards()

    # set block count        
    block_count = block_counter()

    # no arguments - run as normal
    if len(sys.argv) == 1:
        # processing loop
        while True:
            arkdb.open_connection()
            # get last height imported
            l_height = snekdb.lastBlock().fetchall()
            blocks = arkdb.blocks(h=l_height[0][0])
        
            # store blocks
            snekdb.storeBlocks(blocks)

            # check for unprocessed blocks
            unprocessed = snekdb.unprocessedBlocks().fetchall()
          
            # query not empty means unprocessed blocks
            if unprocessed:
                for b in unprocessed:
                
                    # allocate
                    allocate(b)
                    # get new block count
                    block_count = block_counter()
                
                    # increment count
                    print('\n')
                    print(f"Current block count : {block_count}")

                    check = interval_check(block_count)
                    if check:
                        payout()

                    print('\n' + 'Waiting for the next block....' + '\n')
                    # sleep 2 seconds between allocations
                    time.sleep(2)

            arkdb.close_connection()
            # pause 30 seconds between runs
            time.sleep(data["block_check"])
    else:
        # some options passed
        option = sys.argv[1]
        if option == "--shareChange":
            share_change()
        else:
            print("Flag input not recognized. Closing script")
        quit()
