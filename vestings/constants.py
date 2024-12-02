from hexbytes import HexBytes
from web3 import Web3

VESTING_TYPEHASH = HexBytes(
    "0x43838b5ce9ca440d1ac21b07179a1fdd88aa2175e5ea103f6e37aa6d18ce78ad"
)

DOMAIN_SEPARATOR_TYPEHASH = HexBytes(
    "0x47e79534a245952e8b16893a336b85a3d9ea9fa8c573f3d803afb92a79469218"
)

EMPTY_HASH = Web3.solidity_keccak(["bytes"], [bytes(HexBytes("0x"))])


MAINNET_USER_AIRDROP_ADDRESS = HexBytes("0xA0b937D5c8E32a80E3a8ed4227CD020221544ee6")
MAINNET_USER_V2_AIRDROP_ADDRESS = HexBytes("0xC0fde70A65C7569Fe919bE57492228DEE8cDb585")
MAINNET_ECOSYSTEM_AIRDROP_ADDRESS = HexBytes(
    "0x29067F28306419923BCfF96E37F95E0f58ABdBBe"
)
MAINNET_INVESTOR_VESTING_POOL_ADDRESS = HexBytes(
    "0x96B71e2551915d98d22c448b040A3BC4801eA4ff"
)

GOERLI_USER_AIRDROP_ADDRESS = HexBytes("0x07dA2049Fa8127eF6280631BCbc56881d764C8Ee")
GOERLI_USER_V2_AIRDROP_ADDRESS = HexBytes("0x1f2c168de487EFf61829CEAe9319855eb432Ae4E")
GOERLI_ECOSYSTEM_AIRDROP_ADDRESS = HexBytes(
    "0xEc6449091Ae23A92f856702F9452011E31E66C63"
)
GOERLI_INVESTOR_VESTING_POOL_ADDRESS = HexBytes(
    "0x47462A673F217997c750B8bc245895019dB1b237"
)

SEPOLIA_USER_AIRDROP_ADDRESS = HexBytes("0x8e661666D92EAa7A8f927E0E823379db9E02067c")
SEPOLIA_USER_V2_AIRDROP_ADDRESS = HexBytes("0x0B706f61892184E995275F6adb70DB92fF037aB2")
SEPOLIA_ECOSYSTEM_AIRDROP_ADDRESS = HexBytes(
    "0x0Fd0433C6AEa80874a23ebBE4F20bC786A314651"
)
SEPOLIA_INVESTOR_VESTING_POOL_ADDRESS = HexBytes(
    "0x2DaEFe033641eb0bB61fca1C01a01271A32221B9"
)
SEPOLIA_SAP_BOOSTED_AIRDROP_ADDRESS = HexBytes(
    "0xEB6A2bc76E338453A3130C6845c7914369Ccaf47"
)
SEPOLIA_SAP_UNBOOSTED_AIRDROP_ADDRESS = HexBytes(
    "0xd73f11388bC7448523c731c35a594e6C745DB3Fc"
)
