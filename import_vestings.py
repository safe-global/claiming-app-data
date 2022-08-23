import csv
import sqlite3

# to convert from csv date format to unix timestamp
import datetime

# to calculate vesting hash
from hexbytes import HexBytes
from web3 import Web3
from eth_abi import abi
from eth_abi.packed import encode_packed

import json
import os

# airdrop csv
# 0 - owner
# 1 - duration
# 2 - startDate
# 3 - amount

def import_airdrop(chain_id, contract, csvfilename):
    con = sqlite3.connect('claiming.sqlite')
    cur = con.cursor()

    with open(csvfilename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        # skip header row
        next(reader)

        for row in reader:
            owner, duration, start_date, amount = row
            start_date_timestamp = datetime.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S%z").timestamp()
            curve = 0 # linear
            managed = False
            vesting_id = vesting_hash(chain_id, contract, owner, curve, managed, duration, start_date_timestamp, amount)
            cur.execute('''
                INSERT OR REPLACE INTO vestings(
                    chain_id, contract, vesting_id, account, duration_weeks, start_date, amount, curve 
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?
                )
                ''',
                (chain_id, contract.lower(), vesting_id, owner.lower(), duration, start_date_timestamp, amount, curve))
            con.commit()

    con.close()


VESTING_TYPEHASH = HexBytes("0x43838b5ce9ca440d1ac21b07179a1fdd88aa2175e5ea103f6e37aa6d18ce78ad")
DOMAIN_SEPARATOR_TYPEHASH = HexBytes("0x47e79534a245952e8b16893a336b85a3d9ea9fa8c573f3d803afb92a79469218")


def vesting_hash(chain_id, contract, account, curve, managed, duration, start_date, amount):
    domain_separator = Web3.solidityKeccak(
        ['bytes'],
        [
            abi.encode(
                ('bytes32', 'uint256', 'address'),
                (bytes(DOMAIN_SEPARATOR_TYPEHASH), chain_id, contract)
            )
        ]
    )

    vesting_data_hash = Web3.solidityKeccak(
        ['bytes'],
        [
            abi.encode(
                ('bytes32', 'address', 'uint8', 'bool', 'uint16', 'uint64', 'uint128'),
                (bytes(VESTING_TYPEHASH), account, curve, managed,
                 int(duration), int(start_date), int(amount))
            )
        ]
    )

    vesting_id = Web3.solidityKeccak(
        ['bytes'],
        [
            encode_packed(
                ('bytes1', 'bytes1', 'bytes', 'bytes'),
                (HexBytes(0x19), HexBytes(0x01), domain_separator, vesting_data_hash)
            )
        ]
    )

    return HexBytes(vesting_id).hex()

# exports all accounts' allocations in a single jsonfile
def export_singlefile(jsonfile):
    con = sqlite3.connect('claiming.sqlite')
    cur_select = con.cursor()
    prev_account = None
    allocations = []
    with open(jsonfile, "w") as file:
        file.write("[\n")
        ## uncomment to select only accounts with several airdrops
        # sql = '''
        # SELECT a.chain_id, a.contract, a.vesting_id, a.account, a.duration_weeks, a.start_date, a.amount, a.curve
        # FROM vestings a
        # JOIN (
        #     SELECT account, COUNT(*)
        #     FROM vestings
        #     GROUP BY account
        #     HAVING count(*) > 1
        # ) b
        # ON a.account = b.account
        # ORDER BY a.account
        # '''

        sql = "SELECT chain_id, contract, vesting_id, account, duration_weeks, start_date, amount, curve FROM vestings ORDER BY account"

        for row in cur_select.execute(sql):
            chain_id, contract, vesting_id, account, duration_weeks, start_date, amount, curve = row
            allocation = {
                "account": account,
                "chainId": chain_id,
                "contract": contract,
                "vestingId": vesting_id,
                "durationWeeks": duration_weeks,
                "startDate": start_date,
                "amount": amount,
                "curve": curve
            }
            if account is None or account == prev_account:
                allocations.append(allocation)
            else:
                if allocations:
                    file.write(json.dumps(allocations, indent=4))
                    file.write(",\n")
                allocations = [allocation]

            prev_account = account

        # dump last allocation
        if allocations:
            file.write(json.dumps(allocations, indent=4))
            file.write("\n]\n")
    con.close()

# exports every account's allocations in a single json file named with account address in hex (not checksummed) inside a directory
def export_manyfiles(directory):
    con = sqlite3.connect('claiming.sqlite')
    cur_select = con.cursor()
    prev_account = None
    allocations = []
    ## uncomment to select only accounts with several airdrops
    # sql = '''
    # SELECT a.chain_id, a.contract, a.vesting_id, a.account, a.duration_weeks, a.start_date, a.amount, a.curve
    # FROM vestings a
    # JOIN (
    #     SELECT account, COUNT(*)
    #     FROM vestings
    #     GROUP BY account
    #     HAVING count(*) > 1
    # ) b
    # ON a.account = b.account
    # ORDER BY a.account
    # '''

    sql = "SELECT chain_id, contract, vesting_id, account, duration_weeks, start_date, amount, curve FROM vestings ORDER BY account"

    for row in cur_select.execute(sql):
        chain_id, contract, vesting_id, account, duration_weeks, start_date, amount, curve = row
        allocation = {
            "account": account,
            "chainId": chain_id,
            "contract": contract,
            "vestingId": vesting_id,
            "durationWeeks": duration_weeks,
            "startDate": start_date,
            "amount": amount,
            "curve": curve
        }

        if account is None or account == prev_account:
            # account address still the same, meaning it gets multiple allocations
            allocations.append(allocation)
        else:
            # dump allocations of the previous account
            if allocations:
                with open(os.path.join(directory, f"{prev_account}.json"), "w") as file:
                    json.dump(allocations, file, indent=4)

            allocations = [allocation]

        prev_account = account

    # dump last allocation
    if allocations:
        with open(os.path.join(directory, f"{prev_account}.json"), "w") as file:
            json.dump(allocations, file, indent=4)
    con.close()

if __name__ == '__main__':
    # import_airdrop(4, "0x6C6ea0B60873255bb670F838b03db9d9a8f045c4", 'resources/user_airdrop.csv')
    # import_airdrop(4, "0x82F1267759e9Bea202a46f8FC04704b6A5E2Af77", 'resources/ecosystem_airdrop.csv')
    export_singlefile('resources/data/allocations.json')
    export_manyfiles('resources/data/allocations')