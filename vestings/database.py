import sqlalchemy
from sqlalchemy import Integer, String, DateTime
from sqlalchemy import Column, ForeignKey
import sqlalchemy.ext.declarative as declarative
import sqlalchemy.orm as orm


DB_URL = "sqlite:///./vestings.db"

Base = declarative.declarative_base()


class VestingModel(Base):

    __tablename__ = "vestings"

    vesting_id = Column(String, primary_key=True, index=True)
    type = Column(String)
    owner = Column(String)
    curve_type = Column(Integer)
    duration_weeks = Column(Integer)
    start_date = Column(DateTime)
    amount = Column(String)

    proofs = orm.relationship("ProofModel",  backref="vestings")


class ProofModel(Base):

    __tablename__ = "proofs"

    vesting_id = Column(String, ForeignKey("vestings.vesting_id"), primary_key=True, index=True)
    proof_index = Column(Integer, primary_key=True)
    proof = Column(String)
    vesting = orm.relationship("VestingModel",  back_populates="proofs", viewonly=True)


engine = sqlalchemy.create_engine(DB_URL, connect_args={"check_same_thread": False})
LocalSession = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_db():
    return Base.metadata.create_all(bind=engine)


def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()

