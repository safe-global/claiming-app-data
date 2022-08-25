import os
import shutil
import json
from json import JSONEncoder
from datetime import datetime
import time
from hexbytes import HexBytes
from database import get_db, create_db, VestingModel, ProofModel
import sqlalchemy.orm as orm
from csv_parser import parse_vestings_csv
from proof_generator import generate_and_add_proof
from vesting import Vesting


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


def export_data(db: orm.Session):

    class VestingData:
        def __init__(self, user, ecosystem):
            self.user = user
            self.ecosystem = ecosystem

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
        vesting = Vesting(
            id=model.vesting_id,
            type=model.type,
            account=model.owner,
            curveType=model.curve_type,
            durationWeeks=model.duration_weeks,
            startDate=time.mktime(datetime.timetuple(model.start_date)),
            amount=model.amount,
            proof=list(map(map_proof, model.proofs))
        )
        return vesting

    print(80 * "-")
    print(f"Exporting vestings")
    print(80 * "-")

    if os.path.exists("../resources/data/allocations"):
        shutil.rmtree("../resources/data/allocations")

    if not os.path.exists("../resources/data/allocations"):
        os.makedirs("../resources/data/allocations")

    vestings = list(map(map_vesting, db.query(VestingModel).order_by(VestingModel.owner)))

    i = 0
    while i < len(vestings):

        vesting1 = vestings[i]
        vesting2 = None

        if i + 1 < len(vestings):
            vesting = vestings[i + 1]
            if vesting.account == vesting1.account:
                vesting2 = vesting
                i = i + 1

        vesting_data = VestingData(
            user=vesting1 if vesting1.type == "user" else vesting2,
            ecosystem=vesting2 if vesting1.type == "user" else vesting1
        )

        if vesting_data.user:
            vesting_data.user.type = None
        if vesting_data.ecosystem:
            vesting_data.ecosystem.type = None

        print(f"Writing {vesting1.account} vesting to file")
        with open(f"../resources/data/allocations/{vesting1.account}.json", "w") as file:
            file.write(json.dumps(vesting_data, indent=4, cls=VestingEncoder))

        i = i + 1


if __name__ == '__main__':

    db = prepare_db()

    generate_vestings_data(db)

    export_data(db)


