import sqlalchemy.orm as orm
from database import VestingModel, ProofModel
import merkle_proof
from joblib import Parallel, delayed
from database import get_db


def generate_and_safe_proof_for_vesting(db_file, vesting_ids, vesting_id):

    db = next(get_db(db_file))

    proof, root = merkle_proof.generate(vesting_ids, vesting_id)
    proof_index = 0
    for part in proof:
        proof_model = ProofModel(
            vesting_id=vesting_id,
            proof_index=proof_index,
            proof=part
        )
        db.add(proof_model)
        db.commit()
        db.refresh(proof_model)
        proof_index += 1

    print(f"{proof}")


def generate_and_save_proofs(db_file, type, chain_id):

    print(80 * "-")
    print(f"Generating {type} vestings proofs")
    print(80 * "-")

    db = next(get_db(db_file))
    vestings = db.query(VestingModel).filter(VestingModel.type == type and VestingModel.chain_id == chain_id)
    vesting_ids = list(map(lambda vesting: vesting.vesting_id, vestings))

    Parallel(n_jobs=-1)((delayed(generate_and_safe_proof_for_vesting)(db_file, vesting_ids, vesting_id) for vesting_id in vesting_ids))


def generate_and_print_root(db: orm.Session, type, chain_id):

    print(80 * "-")
    print(f"Generating {type} vestings root")
    print(80 * "-")

    vestings = db.query(VestingModel).filter(VestingModel.type == type and VestingModel.chain_id == chain_id)
    vesting_ids = list(map(lambda vesting: vesting.vesting_id, vestings))

    root = merkle_proof.generate_root(vesting_ids)
    print(f"{type} root: {root}")
