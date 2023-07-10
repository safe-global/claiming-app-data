from typing import Any, List, Optional

from constants import DOMAIN_SEPARATOR_TYPEHASH, VESTING_TYPEHASH
from eth_abi import abi
from eth_abi.packed import encode_packed
from eth_typing import ChecksumAddress, HexStr
from hexbytes import HexBytes
from web3 import Web3


class Vesting:
    def __init__(
        self,
        id: Optional[HexStr],
        type: str,
        account: ChecksumAddress,
        curveType: int,
        durationWeeks: int,
        startDate: int,
        amount: str,  # Sqlite cannot handle integers this long
        proof: Optional[List[Any]],
    ):
        self.id = id
        self.type = type
        self.account = account
        self.curveType = curveType
        self.durationWeeks = durationWeeks
        self.startDate = startDate
        self.amount = amount
        self.proof = proof

    def calculateHash(self, airdrop_address: ChecksumAddress, chain_id: int) -> HexStr:
        domain_separator = Web3.solidity_keccak(
            ["bytes"],
            [
                abi.encode(
                    ("bytes32", "uint256", "address"),
                    (DOMAIN_SEPARATOR_TYPEHASH, chain_id, airdrop_address),
                )
            ],
        )

        vesting_data_hash = Web3.solidity_keccak(
            ["bytes"],
            [
                abi.encode(
                    (
                        "bytes32",
                        "address",
                        "uint8",
                        "bool",
                        "uint16",
                        "uint64",
                        "uint128",
                    ),
                    (
                        VESTING_TYPEHASH,
                        self.account,
                        self.curveType,
                        False,
                        self.durationWeeks,
                        self.startDate,
                        int(self.amount),
                    ),
                )
            ],
        )

        vesting_id = Web3.solidity_keccak(
            ["bytes"],
            [
                encode_packed(
                    ("bytes1", "bytes1", "bytes", "bytes"),
                    (
                        HexBytes(0x19),
                        HexBytes(0x01),
                        domain_separator,
                        vesting_data_hash,
                    ),
                )
            ],
        )

        return HexBytes(vesting_id).hex()
