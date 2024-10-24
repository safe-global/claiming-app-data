import csv
import os
from typing import Dict, List

from addresses import get_airdrop_addresses
from dateutil.parser import parse
from vesting import Vesting, VestingType
from web3 import Web3

CURRENT_DIRECTORY = os.path.dirname(__file__)


def read_vesting_file(
    vesting_file: str, chain_id: int, vesting_type: VestingType
) -> List[Vesting]:
    vestings: List[Vesting] = []
    airdrop_address = Web3.to_checksum_address(
        get_airdrop_addresses(chain_id)[vesting_type]
    )
    with open(vesting_file, mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file)

        print(80 * "-")
        print(f"Processing {vesting_type.name} vestings")

        for row in csv_reader:
            owner = Web3.to_checksum_address(row["owner"])
            duration_weeks: int
            start_date_timestamp: int

            if "duration" in row.keys():
                duration_weeks = int(row["duration"])
            else:
                if vesting_type in (VestingType.USER_V2, VestingType.INVESTOR):
                    duration_weeks = 208
                else:
                    duration_weeks = 416

            if "startDate" in row.keys():
                start_date_timestamp = int(parse(row["startDate"]).timestamp())
            else:
                if vesting_type == VestingType.USER_V2:
                    start_date_timestamp = int(
                        parse("2022-09-01T10:00:00+00:00").timestamp()
                    )
                elif vesting_type == VestingType.INVESTOR:
                    start_date_timestamp = int(
                        parse("2022-10-01T10:00:00+00:00").timestamp()
                    )
                else:
                    start_date_timestamp = int(
                        parse("2018-07-14T00:00:00+00:00").timestamp()
                    )

            # For user_v2, amount has decimals
            if vesting_type == VestingType.USER_V2:
                amount = str(Web3.to_wei(row["amount"], "ether"))
            else:
                amount = row["amount"]

            curve_type = 0

            vesting = Vesting(
                None,
                vesting_type,
                owner,
                airdrop_address,
                chain_id,
                curve_type,
                duration_weeks,
                start_date_timestamp,
                amount,
                [],
            )
            vestings.append(vesting)

            calculated_vesting_id = vesting.calculateHash()

            if "vestingId" in row.keys():
                vesting_id = row["vestingId"]
                if vesting_id != calculated_vesting_id:
                    raise ValueError("provided and calculated vesting id do not match!")

        print(f"Processed {len(vestings)} {vesting_type} vestings.")
        print(80 * "-")
        return vestings


def parse_vestings_csv(chain_id: int) -> Dict[VestingType, List[Vesting]]:
    vesting_type_with_vestings = {}
    for vesting_type in VestingType:
        vesting_file = {
            VestingType.USER: os.path.join(
                CURRENT_DIRECTORY, f"assets/{chain_id}/user_airdrop.csv"
            ),
            VestingType.USER_V2: os.path.join(
                CURRENT_DIRECTORY, f"assets/{chain_id}/user_airdrop_v2.csv"
            ),
            VestingType.ECOSYSTEM: os.path.join(
                CURRENT_DIRECTORY, f"assets/{chain_id}/ecosystem_airdrop.csv"
            ),
            VestingType.INVESTOR: os.path.join(
                CURRENT_DIRECTORY, f"assets/{chain_id}/investor_vestings.csv"
            ),
            VestingType.SAP_BOOSTED: os.path.join(
                CURRENT_DIRECTORY, f"assets/{chain_id}/sap_boosted_airdrop.csv"
            ),
            VestingType.SAP_UNBOOSTED: os.path.join(
                CURRENT_DIRECTORY, f"assets/{chain_id}/sap_unboosted_airdrop.csv"
            ),
        }.get(vesting_type)
        if not vesting_file:
            raise ValueError(f"Not a valid vestings type: {vesting_type}")

        if not os.path.exists(vesting_file):
            print(vesting_file, "does not exist")

        vesting_type_with_vestings[vesting_type] = read_vesting_file(
            vesting_file, chain_id, vesting_type
        )
    return vesting_type_with_vestings
