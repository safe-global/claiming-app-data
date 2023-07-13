import merkle_proof
import sqlalchemy.orm as orm
from database import ProofModel, VestingModel, get_db
from joblib import Parallel, delayed


def generate_and_safe_proof_for_vesting(
    db_file: str, vestings_tree, vesting_id, verbose
):
    db = next(get_db(db_file))

    proof = merkle_proof.extract_proof(vestings_tree, vesting_id)
    proof_index = 0

    proof_models = []
    for part in proof:
        proof_model = ProofModel(
            vesting_id=vesting_id, proof_index=proof_index, proof=part
        )
        proof_models.append(proof_model)
        proof_index += 1
    db.bulk_save_objects(proof_models)
    db.commit()

    if verbose:
        print(f"{proof}")


def generate_and_save_proofs(db_file: str, type: str, chain_id: int, verbose: bool):
    print(80 * "-")
    print(f"Generating {type} vestings proofs")
    if verbose:
        print(80 * "-")

    db = next(get_db(db_file))
    vestings = db.query(VestingModel).filter(
        VestingModel.type == type and VestingModel.chain_id == chain_id
    )
    vesting_ids = [vesting.vesting_id for vesting in vestings]
    vestings_tree = merkle_proof.generate_vestings_tree(vesting_ids)

    Parallel(n_jobs=1)(
        (
            delayed(generate_and_safe_proof_for_vesting)(
                db_file, vestings_tree, vesting_id, verbose
            )
            for vesting_id in vesting_ids
        )
    )


def generate_and_print_root(db: orm.Session, type: str, chain_id: int):
    print(80 * "-")
    print(f"Generating {type} vestings root")
    print(80 * "-")

    vestings = db.query(VestingModel).filter(
        VestingModel.type == type and VestingModel.chain_id == chain_id
    )
    vesting_ids = [vesting.vesting_id for vesting in vestings]

    if vesting_ids:
        root = merkle_proof.generate_root(vesting_ids)
        print(f"{type} root: {root}")
        required_number_tokens = sum(int(vesting.amount) for vesting in vestings)
        print(f"{type} required number of tokens: {required_number_tokens}")
