import sqlalchemy.orm as orm
from database import VestingModel
from constants import *
import csv
from dateutil.parser import parse
from vesting import Vesting
from web3 import Web3


def parse_vestings_csv(db: orm.Session, type, chain_id, verbose, start_date, duration):

    vesting_file = {
        "user": f"assets/{chain_id}/user_airdrop.csv",
        "ecosystem": f"assets/{chain_id}/ecosystem_airdrop.csv",
        "investor": f"assets/{chain_id}/investor_vestings.csv",
    }.get(type)
    if not vesting_file:
        raise ValueError(f"Not a valid vestings type: {type}")

    with open(vesting_file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0

        print(80 * "-")
        print(f"Processing {type} vestings")
        print(80 * "-")

        vesting_models = []

        for row in csv_reader:

            owner = Web3.toChecksumAddress(row["owner"])

            duration_weeks: int
            if duration is not None:
                duration_weeks = duration
            else:
                if "duration" in row.keys():
                    duration_weeks = row["duration"]
                else:
                    duration_weeks = 416

            start_date_timestamp: int
            if start_date is not None:
                start_date_timestamp = start_date
            else:
                if "startDate" in row.keys():
                    start_date_timestamp = parse(row["startDate"]).timestamp()
                else:
                    start_date_timestamp = parse("2018-09-27T10:00:00+00:00").timestamp()

            amount = row["amount"]

            curve_type = 0

            vesting = Vesting(None, type, owner, curve_type, duration_weeks, start_date_timestamp, amount, None)

            airdrop_address = {
                "user": {
                    1: MAINNET_USER_AIRDROP_ADDRESS,
                    4: RINKEBY_USER_AIRDROP_ADDRESS,
                    5: GOERLI_USER_AIRDROP_ADDRESS
                }[chain_id],
                "ecosystem": {
                    1: MAINNET_ECOSYSTEM_AIRDROP_ADDRESS,
                    4: RINKEBY_ECOSYSTEM_AIRDROP_ADDRESS,
                    5: GOERLI_ECOSYSTEM_AIRDROP_ADDRESS
                }[chain_id],
                "investor": {
                    1: MAINNET_INVESTOR_VESTING_POOL_ADDRESS,
                    5: GOERLI_INVESTOR_VESTING_POOL_ADDRESS
                }[chain_id]
            }[type]
            
            calculated_vesting_id = vesting.calculateHash(airdrop_address, chain_id)

            vesting_id: str

            if "vestingId" in row.keys():
                vesting_id = row["vestingId"]
                if vesting_id != calculated_vesting_id:
                    raise ValueError("provided and calculated vesting id do not match!")
            else:
                vesting_id = calculated_vesting_id

            vesting_model = VestingModel(
                vesting_id=vesting_id,
                chain_id=chain_id,
                type=type,
                owner=owner,
                curve_type=curve_type,
                duration_weeks=duration_weeks,
                start_date=start_date_timestamp,
                amount=amount
            )

            vesting_models.append(vesting_model)

            if verbose:
                print(f"[{type}] {owner}: {vesting_id}")

            line_count += 1

        db.bulk_save_objects(vesting_models)
        db.commit()

        print(f'Processed {line_count} {type} vestings.')
