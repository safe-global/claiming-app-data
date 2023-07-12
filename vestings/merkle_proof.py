from typing import List

from eth_typing import HexStr
from hexbytes import HexBytes
from web3 import Web3

EMPTY_HASH = HexBytes(Web3.solidity_keccak(["bytes"], [bytes(HexBytes("0x"))])).hex()


def combine_and_hash(leaf1: str | bytes, leaf2: str | bytes) -> HexStr:
    return Web3.keccak(HexBytes(leaf1) + HexBytes(leaf2)).hex()


def generate_vestings_tree(elements: List[HexStr]) -> List[List[HexStr]]:
    """
    :param elements:
    :type elements:
    :return: Merkle tree from a list of elements
    """
    previous_level = list(elements)
    levels: List[List[str]] = [previous_level]
    while len(previous_level) > 1:
        current_level: List[HexStr] = []
        previous_level_len = len(previous_level)
        for i in range(0, previous_level_len, 2):
            leaf1 = previous_level[i]
            # If there's no leaf2, use an empty hash
            leaf2 = previous_level[i + 1] if i + 1 < previous_level_len else EMPTY_HASH
            # Leaf1 must be smaller than leaf2, if not swap them
            if HexBytes(leaf1) > HexBytes(leaf2):
                leaf1, leaf2 = leaf2, leaf1
            current_level.append(combine_and_hash(leaf1, leaf2))
        levels.append(current_level)
        previous_level = current_level

    return levels


def extract_proofs(vestings_tree: List[List[HexStr]], element: HexStr) -> List[HexStr]:
    if not vestings_tree:
        raise ValueError("Vesting tree cannot be empty")

    # ValueError is raised if element is not found
    element_index = vestings_tree[0].index(element)

    proof: List[HexStr] = []
    for current_level in vestings_tree[:-1]:
        # If element in pair position, get next leaf, or EMPTY_HASH if there's not
        # If element not in pair position, get previous leaf
        if element_index % 2 == 0:
            if element_index + 1 >= len(current_level):
                proof.append(EMPTY_HASH)
            else:
                proof.append(current_level[element_index + 1])
        else:
            proof.append(current_level[element_index - 1])
        element_index //= 2

    return proof


def generate_root(elements: List[HexStr]):
    vestings_tree = generate_vestings_tree(elements)
    return vestings_tree[-1][0]
