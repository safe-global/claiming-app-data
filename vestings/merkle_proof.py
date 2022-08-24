import math
import sys
from hexbytes import HexBytes
from eth_abi import abi
from web3 import Web3


EMPTY_HASH = Web3.solidityKeccak(['bytes'], [bytes(HexBytes("0x"))])


def combine_and_hash(leaf1: str, leaf2: str):
    combined_hash = Web3.solidityKeccak(
        ['bytes'],
        [
            abi.encode(
                ('bytes32', 'bytes32'),
                (bytes(HexBytes(leaf1)), bytes(HexBytes(leaf2)))
            )
        ]
    )
    return HexBytes(combined_hash).hex()


def generate(input, element=None):

    proof = []
    elements = input.copy()
    count = len(elements)

    while count > 1:
        for i in range(count):
            if i % 2 != 0:
                continue
            leaf1 = elements[i]
            leaf2 = EMPTY_HASH
            if i + 1 < count:
                leaf2 = elements[i + 1]
            if leaf1 == element:
                proof.append(leaf2)
                elements[int(i / 2)] = element
            elif leaf2 == element:
                proof.append(leaf1)
                elements[int(i / 2)] = element
            else:
                if int.from_bytes(bytes(HexBytes(leaf1)), sys.byteorder) < int.from_bytes(bytes(HexBytes(leaf2)), sys.byteorder):
                    elements[int(i / 2)] = combine_and_hash(leaf1, leaf2)
                else:
                    elements[int(i / 2)] = combine_and_hash(leaf2, leaf1)

        count = math.ceil(count / 2)

    return proof, elements[0]
