import argparse
import json
import os
import shutil
from enum import Enum
from json import JSONEncoder
from typing import Any, Dict

import sqlalchemy.orm as orm
from addresses import get_airdrop_addresses
from csv_parser import parse_vestings_csv
from database import VestingModel, create_db, get_db
from eth_typing import ChecksumAddress
from hexbytes import HexBytes
from proof_generator import generate_and_print_root, generate_and_save_proofs
from web3 import Web3


class VestingData:
    def __init__(
        self,
        tag: str,
        account: ChecksumAddress,
        chainId: int,
        contract: ChecksumAddress,
        vestingId: str,
        durationWeeks: int,
        startDate: int,
        amount: str,
        curve: int,
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

    def __str__(self) -> str:
        return f"{self.tag} - {self.account} - {self.contract}"

    def __repr__(self) -> str:
        return str(self)


class VestingDataWithProof(VestingData):
    def __init__(
        self,
        **kwargs,
    ):
        self.proof: str = kwargs.pop("proof")
        super().__init__(**kwargs)


class VestingEncoder(JSONEncoder):
    def default(self, o):
        d = dict(o.__dict__)
        for k, v in list(d.items()):
            if v is None:
                del d[k]

        return d


class Export(Enum):
    none = "none"
    snapshot = "snapshot"
    allocations = "allocations"

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(s):
        try:
            return Export[s]
        except KeyError:
            raise ValueError()

    @staticmethod
    def argparse(s):
        try:
            return Export[s.lower()]
        except KeyError:
            return s


def prepare_db(db_file):
    print(80 * "-")
    print("Creating database")

    if not os.path.exists(os.path.dirname(db_file)):
        os.makedirs(os.path.dirname(db_file))

    create_db(db_file)


def process_vestings(
    db: orm.Session, chain_id: int, verbose: bool, start_date: int, duration: int
):
    for tag in ("user", "user_v2", "ecosystem"):
        parse_vestings_csv(db, tag, chain_id, verbose, start_date, duration)


def process_investor_vestings(
    db: orm.Session, chain_id: int, verbose: bool, start_date: int, duration: int
):
    parse_vestings_csv(db, "investor", chain_id, verbose, start_date, duration)


def generate_proofs(db_file: str, chain_id: int, verbose: bool):
    for tag in ("user", "user_v2", "ecosystem"):
        generate_and_save_proofs(db_file, tag, chain_id, verbose)


def generate_roots(db: orm.Session, chain_id: int):
    for tag in ("user", "user_v2", "ecosystem"):
        generate_and_print_root(db, tag, chain_id)


def export_data(
    db: orm.Session, chain_id, output_directory, verbose, export_type=Export.snapshot
):
    def map_proof(proof) -> str:
        return HexBytes(proof.proof).hex()

    def map_vesting(model):
        contract = get_airdrop_addresses(chain_id)[model.type]

        vesting_data = VestingData(
            tag=model.type,
            account=Web3.to_checksum_address(model.owner),
            chainId=chain_id,
            contract=Web3.to_checksum_address(contract),
            vestingId=model.vesting_id,
            durationWeeks=model.duration_weeks,
            startDate=model.start_date,
            amount=model.amount,
            curve=model.curve_type,
        )

        return vesting_data

    def map_vesting_with_proof(model):
        contract = get_airdrop_addresses(chain_id)[model.type]

        vesting_data = VestingDataWithProof(
            tag=model.type,
            account=model.owner,
            chainId=chain_id,
            contract=Web3.to_checksum_address(contract),
            vestingId=model.vesting_id,
            durationWeeks=model.duration_weeks,
            startDate=model.start_date,
            amount=model.amount,
            curve=model.curve_type,
            proof=list(map(map_proof, model.proofs)),
        )

        return vesting_data

    print(80 * "-")
    print(f"Exporting vestings ({export_type})")
    if verbose:
        print(80 * "-")

    export_directory = f"{output_directory}/{chain_id}"
    if export_type == Export.snapshot:
        if os.path.exists(f"{export_directory}/snapshot-allocations-data.json"):
            os.remove(f"{export_directory}/snapshot-allocations-data.json")
    else:
        if os.path.exists(f"{export_directory}"):
            shutil.rmtree(f"{export_directory}")

    if not os.path.exists(f"{export_directory}"):
        os.makedirs(f"{export_directory}")
        print(f"Exporting data to {export_directory}")

    vestings = list(
        map(
            map_vesting_with_proof
            if export_type == Export.allocations
            else map_vesting,
            db.query(VestingModel)
            .where(VestingModel.chain_id == chain_id)
            .order_by(VestingModel.owner),
        )
    )

    account_with_vestings: Dict[ChecksumAddress, Any] = {}
    for vesting in vestings:
        account_with_vestings.setdefault(vesting.account, []).append(vesting)

    for account, vesting_array in account_with_vestings.items():
        if verbose:
            print(f"Writing {account} vestings to file")
        if export_type != Export.snapshot:
            print(vesting_array)
            with open(f"{export_directory}/{account}.json", "w") as file:
                file.write(json.dumps(vesting_array, indent=4, cls=VestingEncoder))

    if export_type == Export.snapshot:
        with open(f"{export_directory}/snapshot-allocations-data.json", "w") as file:
            file.write(
                json.dumps(
                    list(account_with_vestings.values()), indent=4, cls=VestingEncoder
                )
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vesting data converter and exporter.")

    parser.add_argument(
        "--chain-id", dest="chain_id", help="chain id", required=True, type=int
    )

    parser.add_argument(
        "--output-directory",
        dest="output_dir",
        default="../data/allocations/",
        help="output directory",
        required=False,
    )

    parser.add_argument(
        "--db-file",
        dest="db_file",
        default="intermediates/allocations.db",
        required=False,
        help="path to a database file",
    )

    parser.add_argument(
        "--clear-db",
        dest="clear_db",
        action="store_const",
        const=True,
        default=False,
        help="clear database",
        required=False,
    )

    parser.add_argument(
        "--start-date",
        dest="start_date",
        help="start date timestamp",
        required=False,
        type=int,
    )

    parser.add_argument(
        "--duration",
        dest="duration",
        help="duration in weeks",
        required=False,
        type=int,
    )

    parser.add_argument(
        "--process-vestings",
        dest="process_vestings",
        action="store_const",
        const=True,
        default=False,
        help="process vestings",
        required=False,
    )

    parser.add_argument(
        "--process-investor-vestings",
        dest="process_investor_vestings",
        action="store_const",
        const=True,
        default=False,
        help="process investor vestings",
        required=False,
    )

    parser.add_argument(
        "--generate-proofs",
        dest="generate_proofs",
        action="store_const",
        const=True,
        default=False,
        help="generate proofs",
        required=False,
    )

    parser.add_argument(
        "--generate-root",
        dest="generate_root",
        action="store_const",
        const=True,
        default=False,
        help="generate root",
        required=False,
    )

    parser.add_argument(
        "--export",
        type=Export.argparse,
        choices=list(Export),
        dest="export",
        default=Export.none,
        help="export type (default none)",
        required=False,
    )

    parser.add_argument(
        "--verbose",
        dest="verbose",
        action="store_const",
        const=True,
        default=False,
        help="verbose",
        required=False,
    )

    args = parser.parse_args()

    if args.clear_db:
        if os.path.exists(args.db_file):
            os.remove(args.db_file)
        prepare_db(args.db_file)

    if not os.path.exists(args.db_file):
        prepare_db(args.db_file)

    db = next(get_db(args.db_file))

    if args.process_vestings:
        process_vestings(
            db, args.chain_id, args.verbose, args.start_date, args.duration
        )

    if args.process_investor_vestings:
        process_investor_vestings(
            db, args.chain_id, args.verbose, args.start_date, args.duration
        )

    if args.generate_root:
        generate_roots(db, args.chain_id)
    else:
        if args.generate_proofs:
            generate_proofs(args.db_file, args.chain_id, args.verbose)
        if args.export != Export.none:
            export_data(
                db,
                args.chain_id,
                args.output_dir,
                args.verbose,
                args.export,
            )
