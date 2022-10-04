import sqlalchemy.orm as orm
from database import VestingModel
from constants import *
import csv
from dateutil.parser import parse
from vesting import Vesting
from web3 import Web3


def parse_vestings_csv(db: orm.Session, type, chain_id, verbose):

    vesting_file = f"assets/{chain_id}/{type}_vestings.csv" if type == "investor" else f"assets/{chain_id}/{type}_airdrop.csv"

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
            if "duration" in row.keys():
                duration_weeks = row["duration"]
            else:
                duration_weeks = 416

            start_date: int
            if "startDate" in row.keys():
                start_date = parse(row["startDate"]).timestamp()
            else:
                start_date = parse("2018-09-27T10:00:00+00:00").timestamp()

            amount = row["amount"]

            curve_type = 0

            calculated_vesting_id: str

            vesting = Vesting(None, type, owner, curve_type, duration_weeks, start_date, amount, None)

            if type == "investor":
                calculated_vesting_id = vesting.calculateHash(MAINNET_INVESTOR_AIRDROP_ADDRESS, chain_id)
            else:
                user_airdrop_address = MAINNET_USER_AIRDROP_ADDRESS if chain_id == 1 else RINKEBY_USER_AIRDROP_ADDRESS
                ecosystem_airdrop_address = MAINNET_ECOSYSTEM_AIRDROP_ADDRESS if chain_id == 1 else RINKEBY_ECOSYSTEM_AIRDROP_ADDRESS
                calculated_vesting_id = vesting.calculateHash(user_airdrop_address, chain_id) if type == "user" \
                    else vesting.calculateHash(ecosystem_airdrop_address, chain_id)

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
                start_date=start_date,
                amount=amount
            )

            vesting_models.append(vesting_model)

            if verbose:
                print(f"[{type}] {owner}: {vesting_id}")

            line_count += 1

        db.bulk_save_objects(vesting_models)
        db.commit()

        print(f'Processed {line_count} {type} vestings.')


def convert_vestings_csv(input_file: str, output_file: str):

    with open(input_file, mode='r') as ifile:

        csv_reader = csv.DictReader(ifile)
        line_count = 0

        with open(output_file, mode='w') as ofile:

            for row in csv_reader:

                if line_count == 0:
                    ofile.write("owner,duration,startDate,amount\n")
                    line_count += 1
                else:
                    ofile.write("\n")

                owner = Web3.toChecksumAddress(row["safe_address"])
                duration = 416
                start_date = "2018-07-14T10:00:00+00:00"
                amount = Web3.toWei(row["tokens"], "ether")

                ofile.write(f"{owner},{duration},{start_date},{amount}")

                line_count += 1
