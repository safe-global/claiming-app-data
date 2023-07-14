from typing import Dict

from constants import (
    GOERLI_ECOSYSTEM_AIRDROP_ADDRESS,
    GOERLI_INVESTOR_VESTING_POOL_ADDRESS,
    GOERLI_USER_AIRDROP_ADDRESS,
    GOERLI_USER_V2_AIRDROP_ADDRESS,
    MAINNET_ECOSYSTEM_AIRDROP_ADDRESS,
    MAINNET_INVESTOR_VESTING_POOL_ADDRESS,
    MAINNET_USER_AIRDROP_ADDRESS,
    MAINNET_USER_V2_AIRDROP_ADDRESS,
)
from hexbytes import HexBytes
from vesting import VestingType


def get_airdrop_addresses(chain_id: int) -> Dict[str, Dict[int, HexBytes]]:
    return {
        VestingType.USER: {
            1: MAINNET_USER_AIRDROP_ADDRESS,
            5: GOERLI_USER_AIRDROP_ADDRESS,
        }[chain_id],
        VestingType.USER_V2: {
            1: MAINNET_USER_V2_AIRDROP_ADDRESS,
            5: GOERLI_USER_V2_AIRDROP_ADDRESS,
        }[chain_id],
        VestingType.ECOSYSTEM: {
            1: MAINNET_ECOSYSTEM_AIRDROP_ADDRESS,
            5: GOERLI_ECOSYSTEM_AIRDROP_ADDRESS,
        }[chain_id],
        VestingType.INVESTOR: {
            1: MAINNET_INVESTOR_VESTING_POOL_ADDRESS,
            5: GOERLI_INVESTOR_VESTING_POOL_ADDRESS,
        }[chain_id],
    }
