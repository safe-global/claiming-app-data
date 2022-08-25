import sqlalchemy.orm as orm
from database import VestingModel, ProofModel
import merkle_proof


def generate_and_add_proof(db: orm.Session, type):

    print(80 * "-")
    print(f"Generating {type} vestings proofs")
    print(80 * "-")

    vestings = db.query(VestingModel).filter(VestingModel.type == type)
    vesting_ids = list(map(lambda vesting: vesting.vesting_id, vestings))

    i = 0
    for vesting in vestings:

        proof, root = merkle_proof.generate(vesting_ids, vesting.vesting_id)

        proof_index = 0
        for part in proof:

            proof_model = ProofModel(
                vesting_id=vesting.vesting_id,
                proof_index=proof_index,
                proof=part
            )

            db.add(proof_model)
            db.commit()
            db.refresh(proof_model)

            proof_index += 1

        i = i + 1
        print(f"{i}: {proof}")
