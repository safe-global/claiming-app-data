from constants import *

def get_airdrop_addresses(chain_id):
    return {
        "user": {
            1: MAINNET_USER_AIRDROP_ADDRESS,
            4: RINKEBY_USER_AIRDROP_ADDRESS,
            5: GOERLI_USER_AIRDROP_ADDRESS
        }[chain_id],
        "user_v2": {
            1: MAINNET_USER_V2_AIRDROP_ADDRESS,
            4: RINKEBY_USER_V2_AIRDROP_ADDRESS,
            5: GOERLI_USER_V2_AIRDROP_ADDRESS
        }[chain_id],
        "ecosystem": {
            1: MAINNET_ECOSYSTEM_AIRDROP_ADDRESS,
            4: RINKEBY_ECOSYSTEM_AIRDROP_ADDRESS,
            5: GOERLI_ECOSYSTEM_AIRDROP_ADDRESS
        }[chain_id],
        "investor": {
            1: MAINNET_INVESTOR_VESTING_POOL_ADDRESS,
            5: GOERLI_INVESTOR_VESTING_POOL_ADDRESS
        }[chain_id]
    }