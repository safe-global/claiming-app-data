from hexbytes import HexBytes
from eth_abi import abi
from eth_abi.packed import encode_packed
from web3 import Web3


VESTING_TYPEHASH = HexBytes("0x43838b5ce9ca440d1ac21b07179a1fdd88aa2175e5ea103f6e37aa6d18ce78ad")

DOMAIN_SEPARATOR_TYPEHASH = HexBytes("0x47e79534a245952e8b16893a336b85a3d9ea9fa8c573f3d803afb92a79469218")

EMPTY_HASH = Web3.solidity_keccak(['bytes'], [bytes(HexBytes("0x"))])


class Vesting:

    def __init__(self, id: str, type, account, curveType, durationWeeks, startDate: int, amount, proof: list):
        self.id = id
        self.type = type
        self.account = account
        self.curveType = curveType
        self.durationWeeks = durationWeeks
        self.startDate = startDate
        self.amount = amount
        self.proof = proof

    def calculateHash(self, airdrop_address, chain_id):
        domain_separator = Web3.solidity_keccak(
            ['bytes'],
            [
                abi.encode(
                    ('bytes32', 'uint256', 'address'),
                    (bytes(DOMAIN_SEPARATOR_TYPEHASH), chain_id, airdrop_address.hex())
                )
            ]
        )

        vesting_data_hash = Web3.solidity_keccak(
            ['bytes'],
            [
                abi.encode(
                    ('bytes32', 'address', 'uint8', 'bool', 'uint16', 'uint64', 'uint128'),
                    (bytes(VESTING_TYPEHASH), self.account, self.curveType, False,
                     int(self.durationWeeks), int(self.startDate), int(self.amount))
                )
            ]
        )

        vesting_id = Web3.solidity_keccak(
            ['bytes'],
            [
                encode_packed(
                    ('bytes1', 'bytes1', 'bytes', 'bytes'),
                    (HexBytes(0x19), HexBytes(0x01), domain_separator, vesting_data_hash)
                )
            ]
        )

        return HexBytes(vesting_id).hex()
