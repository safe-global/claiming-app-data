import math
from hexbytes import HexBytes
from eth_abi import abi
from web3 import Web3


EMPTY_HASH = HexBytes(Web3.solidityKeccak(['bytes'], [bytes(HexBytes("0x"))])).hex()


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


def generate_vestings_tree(elements):
    count = len(elements)
    previous_level = elements.copy()
    levels: list(list(str)) = [previous_level]
    while count > 1:
        current_level = []
        i = 0
        while i < count:
            leaf1 = previous_level[i]
            leaf2 = EMPTY_HASH if i + 1 >= count else previous_level[i + 1]
            if int.from_bytes(bytes(HexBytes(leaf1)), byteorder='big', signed=False) < int.from_bytes(bytes(HexBytes(leaf2)), byteorder='big', signed=False):
                current_level.append(combine_and_hash(leaf1, leaf2))
            else:
                current_level.append(combine_and_hash(leaf2, leaf1))
            i = i + 2
        count = math.ceil(count / 2)
        previous_level = current_level.copy()
        levels.append(previous_level)

    return levels


def extract_proof(vestings_tree, element):
    proof = []
    current_level_index = 0
    element_index = vestings_tree[current_level_index].index(element)

    level_count = len(vestings_tree)
    while current_level_index < level_count - 1:
        current_level = vestings_tree[current_level_index]
        if element_index % 2 == 0:
            if element_index + 1 >= len(current_level):
                proof.append(EMPTY_HASH)
            else:
                proof.append(current_level[element_index + 1])
        else:
            proof.append(current_level[element_index - 1])
        element_index = math.floor(element_index / 2)
        current_level_index = current_level_index + 1

    return proof


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
                if int.from_bytes(bytes(HexBytes(leaf1)), byteorder='big', signed=False) < int.from_bytes(bytes(HexBytes(leaf2)), byteorder='big', signed=False):
                    elements[int(i / 2)] = combine_and_hash(leaf1, leaf2)
                else:
                    elements[int(i / 2)] = combine_and_hash(leaf2, leaf1)

        count = math.ceil(count / 2)

    return proof, elements[0]


def generate_root(input):
    proof, root = generate(input)
    return root
