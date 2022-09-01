import os
import shutil
import json
from json import JSONEncoder
from database import get_db, create_db, VestingModel, ProofModel
import sqlalchemy.orm as orm
from csv_parser import parse_vestings_csv
from proof_generator import generate_and_add_proof
from constants import *
from web3 import Web3


def generate_vestings_data(db: orm.Session):
    parse_vestings_csv(db, "user")
    generate_and_add_proof(db, "user")
    parse_vestings_csv(db, "ecosystem")
    generate_and_add_proof(db, "ecosystem")


def prepare_db():
    print(80 * "-")
    print(f"Creating database")
    print(80 * "-")

    if os.path.exists("vestings.db"):
        os.remove("vestings.db")
    create_db()
    return next(get_db())


def export_data(db: orm.Session, separate_files=False):
    class VestingData:
        def __init__(
                self,
                account,
                chainId,
                contract,
                vestingId,
                durationWeeks,
                startDate,
                amount,
                curve
        ):
            self.account = account
            self.chainId = chainId
            self.contract = contract
            self.vestingId = vestingId
            self.durationWeeks = durationWeeks
            self.startDate = startDate
            self.amount = amount
            self.curve = curve

    class VestingDataWithProof:
        def __init__(
                self,
                tag,
                account,
                chainId,
                contract,
                vestingId,
                durationWeeks,
                startDate,
                amount,
                curve,
                proof
        ):
            self.tag = tag
            self.account = account
            self.chainId = chainId
            self.contract = contract
            self.vestingId = vestingId
            self.durationWeeks = durationWeeks
            self.startDate = startDate
            self.amount = amount
            self.curve = curve
            self.proof = proof

    class VestingEncoder(JSONEncoder):
        def default(self, o):

            d = dict(o.__dict__)
            for k, v in list(d.items()):
                if v is None:
                    del d[k]

            return d

    def map_proof(proof):
        return HexBytes(proof.proof).hex()

    def map_vesting(model):
        vesting_data = VestingData(
            account=Web3.toChecksumAddress(model.owner),
            chainId=4,
            contract=Web3.toChecksumAddress(
                ECOSYSTEM_AIRDROP_ADDRESS) if model.type == "ecosystem" else Web3.toChecksumAddress(
                USER_AIRDROP_ADDRESS),
            vestingId=model.vesting_id,
            durationWeeks=model.duration_weeks,
            startDate=model.start_date,
            amount=model.amount,
            curve=model.curve_type
        )
        return vesting_data

    def map_vesting_with_proof(model):
        vesting_data = VestingDataWithProof(
            tag=model.type,
            account=model.owner,
            chainId=4,
            contract=ECOSYSTEM_AIRDROP_ADDRESS if model.type == "ecosystem" else USER_AIRDROP_ADDRESS,
            vestingId=model.vesting_id,
            durationWeeks=model.duration_weeks,
            startDate=model.start_date,
            amount=model.amount,
            curve=model.curve_type,
            proof=list(map(map_proof, model.proofs))
        )
        return vesting_data

    print(80 * "-")
    print(f"Exporting vestings")
    print(80 * "-")

    if os.path.exists("../resources/data/allocations"):
        shutil.rmtree("../resources/data/allocations")

    if not os.path.exists("../resources/data/allocations"):
        os.makedirs("../resources/data/allocations")

    vestings = list(map(map_vesting_with_proof if separate_files else map_vesting, db.query(VestingModel).order_by(VestingModel.owner)))

    result = []

    i = 0
    while i < len(vestings):

        vesting_array = []

        vesting = vestings[i]

        print(f"Writing {vesting.account} vestings to file")

        vesting_array.append(vesting)

        j = i + 1
        while j < len(vestings) and vestings[j].account == vesting.account:
            vesting_array.append(vestings[j])
            j = j + 1

        if not separate_files:
            result.append(vesting_array)
        else:
            with open(f"../resources/data/allocations/{vesting.account}.json", "w") as file:
                file.write(json.dumps(vesting_array, indent=4, cls=VestingEncoder))
        i = j

    if not separate_files:
        with open(f"../resources/data/snapshot-allocations-test.json", "w") as file:
            file.write(json.dumps(result, indent=4, cls=VestingEncoder))


if __name__ == '__main__':
    db = prepare_db()

    db = next(get_db())

    generate_vestings_data(db)

    export_data(db, True)
