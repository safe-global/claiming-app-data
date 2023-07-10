import os

import sqlalchemy
import sqlalchemy.ext.declarative as declarative
import sqlalchemy.orm as orm
from sqlalchemy import Column, ForeignKey, Integer, String

Base = declarative.declarative_base()


class VestingModel(Base):
    __tablename__ = "vestings"

    vesting_id = Column(String, primary_key=True, index=True)
    chain_id = Column(Integer)
    type = Column(String)
    owner = Column(String)
    curve_type = Column(Integer)
    duration_weeks = Column(Integer)
    start_date = Column(Integer)  # DateTime looses zone info
    amount = Column(String)

    proofs = orm.relationship("ProofModel", backref="vestings")


class ProofModel(Base):
    __tablename__ = "proofs"

    vesting_id = Column(
        String, ForeignKey("vestings.vesting_id"), primary_key=True, index=True
    )
    proof_index = Column(Integer, primary_key=True)
    proof = Column(String)
    vesting = orm.relationship("VestingModel", back_populates="proofs", viewonly=True)


def get_db_url(db_file: str) -> str:
    return f"sqlite:///{db_file}"


def create_db(db_file: str):
    db_url = get_db_url(db_file)
    engine = sqlalchemy.create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)


def get_db(db_file: str):
    db_url = get_db_url(db_file)
    engine = sqlalchemy.create_engine(db_url, connect_args={"check_same_thread": False})
    LocalSession = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()


def prepare_db(db_file):
    print(80 * "-")
    print("Creating database")

    if not os.path.exists(os.path.dirname(db_file)):
        os.makedirs(os.path.dirname(db_file))

    create_db(db_file)
