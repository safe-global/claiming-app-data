import sqlalchemy.orm as orm
from database import VestingModel
from constants import *
import csv
import datetime
from vesting import Vesting


def parse_vestings_csv(db: orm.Session, type):
    vesting_file: str

    if type == "user":
        vesting_file = 'assets/user_airdrop.csv'
    else:
        vesting_file = 'assets/ecosystem_airdrop.csv'

    with open(vesting_file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0

        print(80 * "-")
        print(f"Processing {type} vestings")
        print(80 * "-")

        for row in csv_reader:
            if line_count == 0:
                line_count += 1

            owner = row["owner"]
            duration_weeks = row["duration"]
            start_date = datetime.datetime.strptime(row["startDate"], "%Y-%m-%dT%H:%M:%S%z")
            amount = row["amount"]
            curve_type = 0

            vesting = Vesting(None, type, owner, curve_type, duration_weeks, start_date, amount, None)
            vesting_id = vesting.calculateHash(USER_AIRDROP_ADDRESS, 4) if type == "user" \
                else vesting.calculateHash(ECOSYSTEM_AIRDROP_ADDRESS, 4)

            vesting_model = VestingModel(
                vesting_id=vesting_id,
                type=type,
                owner=owner,
                curve_type=curve_type,
                duration_weeks=duration_weeks,
                start_date=start_date,
                amount=amount
            )

            db.add(vesting_model)
            db.commit()
            db.refresh(vesting_model)

            print(f"[{type}] {owner}: {vesting_id}")

            line_count += 1

        print(f'Processed {line_count} {type} vestings.')
