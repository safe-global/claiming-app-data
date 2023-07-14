import argparse
import json
import os
import time
from typing import Dict, List

from csv_parser import parse_vestings_csv
from eth_typing import ChecksumAddress
from merkle_proof import extract_proofs, generate_vestings_tree
from vesting import EnhancedJSONEncoder, Vesting


def export_data(chain_id: int, output_dir: str) -> Dict[ChecksumAddress, List[Vesting]]:
    vesting_type_with_vestings = parse_vestings_csv(chain_id)
    vesting_type_with_vesting_tree = {}
    account_with_vestings = {}

    for vesting_type, vestings in vesting_type_with_vestings.items():
        vesting_ids = []
        # As we have to iterate vestings to get the ids, we also use that loop
        # to build a dictionary with vestings grouped by account
        for vesting in vestings:
            vesting_ids.append(vesting.vestingId)
            account_with_vestings.setdefault(vesting.account, []).append(vesting)
        vesting_tree = generate_vestings_tree(vesting_ids)
        vesting_type_with_vesting_tree[vesting_type] = vesting_tree
        print(vesting_type, "root", vesting_tree[-1][0])

    for account, vestings in account_with_vestings.items():
        for vesting in vestings:
            vesting.proof = extract_proofs(
                vesting_type_with_vesting_tree[vesting.tag], vesting.vestingId
            )
        with open(f"{output_dir}/{account}.json", "w") as file:
            file.write(json.dumps(vestings, indent=4, cls=EnhancedJSONEncoder))

    with open(f"{output_dir}/snapshot-allocations-data.json", "w") as file:
        file.write(
            json.dumps(
                list(account_with_vestings.values()), indent=4, cls=EnhancedJSONEncoder
            )
        )
    return account_with_vestings


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vesting data converter and exporter.")

    parser.add_argument(
        "--chain-id", dest="chain_id", help="chain id", required=True, type=int
    )

    parser.add_argument(
        "--output-directory",
        dest="output_dir",
        default="/tmp/",
        help="output directory",
        required=False,
    )

    args = parser.parse_args()

    start_time = time.time()
    chain_id = args.chain_id
    output_dir = f"{args.output_dir}/{chain_id}"
    os.makedirs(output_dir, exist_ok=True)
    export_data(chain_id, output_dir)
    print("Elapsed", time.time() - start_time, "seconds")
