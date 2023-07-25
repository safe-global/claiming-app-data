import json
import unittest

from exporter import export_data
from merkle_proof import generate_vestings_tree
from vesting import EnhancedJSONEncoder


class MerkleProof(unittest.TestCase):
    def test_generate_vestings_tree(self):
        vesting_ids = [
            "0x0bc121ea154e47d0063bad16094eb059a976cfbe12ddfb42630caf54470d0576",
            "0xfadc222cbc6172cbe6d44543a77e01a38a3170e3da59f0f7c356656db0897e70",
            "0xf81eeda6b8fb704419bd279af9dadb1dc48ab2ddfc15942d8c652a5113b3de8a",
            "0x95c228464f66c4e29b5dd7f1233f6d9fba426fc04e00760de2f27e0715cb37b9",
            "0x4363a7c29b58c18ba8bd74ae1cf7c795eaa3e71272702e1ba028507ff088cabf",
            "0xb53e8f2d59a07aa04426115028a2d574729491f19326f27ca2085f0182382c4e",
            "0x76699f526e8c062cc9db2004f7f3130a911208b3a18fc575760f830a73479011",
            "0x1d410293e77b8b9635316dc45340a45ba675215f47dd873692e172887ce18fea",
            "0x4a8ee402c4c5e0623fcc3f66d26822d8a2b64859118e34e60256facf53ec7aae",
            "0x8e1eacc21f12337449d4009f93f155a195ac288bb9757a54a42be7327e31c3d0",
            "0x499b76adff3029de4e45001805bdd152684802bd718530311f1f214775ff967d",
            "0x75fe15f5bd33b55da05fdbf9bb7a0c5d0871d6f1b403c2a77710255509d4fd19",
            "0x68889372f57b080ca94752fd9c2710688e5863c263db93079fb6788f370d5e02",
            "0x4174dab97a4d58a2e0af15f266a448d6e4ee3b05ba9286208e48dc4758143454",
            "0x607184dd0e3695e6f51010b962714cb98c22f1c04be37868f4e1ca895e90dee3",
            "0xcf45b25e0414fdc035c651dd5a48e2120042086fad75725de4267353cbcafc70",
            "0xc1b4e976c685a843eb9b5ab54acada4c84f99d826389febf7d8230781769d1b1",
            "0xdd851a4e3d5dce08b8c32283367e616cbe3e2597b4175f48e79d0fcdc52022cd",
            "0x9da6d0e0bba07a8272a1e116f91c4e68a843711988194234ac1727fcc3cd0e4f",
            "0xf319f89a154229fe403f494e46697710801f05a97587e3899e2f400edb1ced11",
        ]
        expected_vesting_tree = [
            [
                "0x0bc121ea154e47d0063bad16094eb059a976cfbe12ddfb42630caf54470d0576",
                "0xfadc222cbc6172cbe6d44543a77e01a38a3170e3da59f0f7c356656db0897e70",
                "0xf81eeda6b8fb704419bd279af9dadb1dc48ab2ddfc15942d8c652a5113b3de8a",
                "0x95c228464f66c4e29b5dd7f1233f6d9fba426fc04e00760de2f27e0715cb37b9",
                "0x4363a7c29b58c18ba8bd74ae1cf7c795eaa3e71272702e1ba028507ff088cabf",
                "0xb53e8f2d59a07aa04426115028a2d574729491f19326f27ca2085f0182382c4e",
                "0x76699f526e8c062cc9db2004f7f3130a911208b3a18fc575760f830a73479011",
                "0x1d410293e77b8b9635316dc45340a45ba675215f47dd873692e172887ce18fea",
                "0x4a8ee402c4c5e0623fcc3f66d26822d8a2b64859118e34e60256facf53ec7aae",
                "0x8e1eacc21f12337449d4009f93f155a195ac288bb9757a54a42be7327e31c3d0",
                "0x499b76adff3029de4e45001805bdd152684802bd718530311f1f214775ff967d",
                "0x75fe15f5bd33b55da05fdbf9bb7a0c5d0871d6f1b403c2a77710255509d4fd19",
                "0x68889372f57b080ca94752fd9c2710688e5863c263db93079fb6788f370d5e02",
                "0x4174dab97a4d58a2e0af15f266a448d6e4ee3b05ba9286208e48dc4758143454",
                "0x607184dd0e3695e6f51010b962714cb98c22f1c04be37868f4e1ca895e90dee3",
                "0xcf45b25e0414fdc035c651dd5a48e2120042086fad75725de4267353cbcafc70",
                "0xc1b4e976c685a843eb9b5ab54acada4c84f99d826389febf7d8230781769d1b1",
                "0xdd851a4e3d5dce08b8c32283367e616cbe3e2597b4175f48e79d0fcdc52022cd",
                "0x9da6d0e0bba07a8272a1e116f91c4e68a843711988194234ac1727fcc3cd0e4f",
                "0xf319f89a154229fe403f494e46697710801f05a97587e3899e2f400edb1ced11",
            ],
            [
                "0xcd4a0913de9c67485269b8e8140d0173c03faa92845f1c58c0be66d004aae49b",
                "0xc0593546234da4d43cd12c20c953da8135567cbe4acaf090d3f93089c4c67bde",
                "0xfa05773e3ca886087349aecea74c48d6da4f3dbfa1f87a508dbe57b74bb63a7b",
                "0x730e361b96b6b6ab3bdbf4cdd6ce7a9edd5cac75605acaf50884741188d41be1",
                "0x48a394fb83738dd7145ecb03cbdb4d77263d984f6f816ef37ff7870c78186e35",
                "0xca000e1ab17a3b5ffe6bef8564e75ffebb92ff5ca4953aa9dc3f22c94ea7319d",
                "0xb6dad2cc15f47c2859111ddbf40dd2a2b000c075d278d846b4dc738a92566e45",
                "0xa4ea27b4ee7bec86f183135a8c151cf4305ccd3115d1d7985d6d51c5173e6181",
                "0x3cd84e7b8af7a8de1a41ec4e4d6e06c39aadea8e6bf7c091b0ab70f4fb6e7a39",
                "0x48e1cd80b1764790bc706c37c370b0af55d00181248669c6934d8c6ade85ed36",
            ],
            [
                "0xe5887dc5d86590ae492aa079d74dd1e4ae71e5c1bf9102e8204e7a5cca19e4fb",
                "0x3975d2ebb86dce69d8540c403052492911ac61c0767209d7ff1603549b593590",
                "0x94a7f7fea92390a473fcd3cf689746e58c007a696314289309b50df786bb4cb4",
                "0x52a3f0e9845bc58efd08ea92b3f1ac0e5612a70e3b1ce24b8ff87738d5c44064",
                "0x607705b819fc9ac134888f40a6cfbf4807486a023dfa6e7135be34b12cafeb6c",
            ],
            [
                "0x359e47e36e41f7fa16e54415f2cf03873c02dc94988bac3e2af77c51732f7eac",
                "0xeda9bdf33a6979732aba5516530e74c3f260df61ac1e1b694c9d2ac57db8967b",
                "0x0bbd03fa47debb37eae087d59355eec4488cb1fe399c91e732c9f30796eac5ae",
            ],
            [
                "0x01594b611568532d7e137ba0cc486bf3d876a1378c1e50594fce4bb4cea81298",
                "0x4e8d97dc8a6dc7675b30eca1d727af9dd4a9e68c217b28a8b5c4ae9786154ab0",
            ],
            ["0x5f661ff49ba1b871ee8c8784d5e3c4cfa1f325a08b8d85c619ee9251140dc80d"],
        ]
        self.assertEqual(generate_vestings_tree(vesting_ids), expected_vesting_tree)


class TestExporter(unittest.TestCase):
    def test_export_data(self):
        chain_id = 5
        output_dir = "/tmp"
        result = export_data(chain_id, output_dir)
        self.assertEqual(len(result), 26)
        expected = [
            {
                "vestingId": "0x76699f526e8c062cc9db2004f7f3130a911208b3a18fc575760f830a73479011",
                "tag": "user",
                "account": "0x5f310dc66F4ecDE9a1769f1B7D75224dA592201e",
                "contract": "0x07dA2049Fa8127eF6280631BCbc56881d764C8Ee",
                "chainId": 5,
                "curve": 0,
                "durationWeeks": 416,
                "startDate": 1531526400,
                "amount": "23023120000000000000000",
                "proof": [
                    "0x1d410293e77b8b9635316dc45340a45ba675215f47dd873692e172887ce18fea",
                    "0xfa05773e3ca886087349aecea74c48d6da4f3dbfa1f87a508dbe57b74bb63a7b",
                    "0xe5887dc5d86590ae492aa079d74dd1e4ae71e5c1bf9102e8204e7a5cca19e4fb",
                    "0xeda9bdf33a6979732aba5516530e74c3f260df61ac1e1b694c9d2ac57db8967b",
                    "0xa75263a6298304f2d0a3a09464d6151d1a45ac564f1602171c884d0675640d45",
                ],
            },
            {
                "vestingId": "0x258cb93e463bdc67045704228ffcf2fcd64b81f0999d79eec160182f9506c19b",
                "tag": "user_v2",
                "account": "0x5f310dc66F4ecDE9a1769f1B7D75224dA592201e",
                "contract": "0x1f2c168de487EFf61829CEAe9319855eb432Ae4E",
                "chainId": 5,
                "curve": 0,
                "durationWeeks": 208,
                "startDate": 1662026400,
                "amount": "420690000000000000000",
                "proof": [
                    "0x854a51f0fa6d2a864ea67061e91fafa494b91a5821af1b4123dde1b8b6100f95",
                    "0x7cf4c7d865c76157f8191b40c97f3cfde202bd0ee471613258a3596c340b8fe9",
                    "0xe7af94ff12f5e8899e3557180d3fa3cdaa3a5042081f7d8301ad5702fe0ba488",
                    "0xc1d74fdc7dea96a840a35ff96ed268bca7a5c92e4eae398ad31e8048759e9e70",
                ],
            },
            {
                "vestingId": "0x5255888c86231e3d91e0bb705953cfc1b8a9071d387db27a805382ec38354919",
                "tag": "ecosystem",
                "account": "0x5f310dc66F4ecDE9a1769f1B7D75224dA592201e",
                "contract": "0xEc6449091Ae23A92f856702F9452011E31E66C63",
                "chainId": 5,
                "curve": 0,
                "durationWeeks": 416,
                "startDate": 1531526400,
                "amount": "43023120000000000000000",
                "proof": [
                    "0x2159b632753750f7af794d9421ae02a2f39d93d5e064fc71c4b9a426a54616d3",
                    "0x111bad1b240db7f5f397fe7f415b3766841dc4e95d808b59bcceb039fcefa29a",
                    "0xc1f8b655e82ccea0967f0725cad306af872fa00f4b870879a0192d7dbffdaf12",
                    "0xc2ce492525d8465e24c8cd30bbe3e1ab1866d4af982929c38b340860e60e56fc",
                ],
            },
        ]

        data = json.loads(
            json.dumps(
                result["0x5f310dc66F4ecDE9a1769f1B7D75224dA592201e"],
                indent=4,
                cls=EnhancedJSONEncoder,
            )
        )
        self.assertEqual(data, expected)


if __name__ == "__main__":
    unittest.main()
