import json
import unittest
import uuid

from database import get_db, prepare_db
from exporter import Export, VestingEncoder, export_data, process_vestings


class TestExporter(unittest.TestCase):
    def test_export_data(self):
        random_filename = str(uuid.uuid4())
        db_path = f"/tmp/{random_filename}"
        # Prepare database
        prepare_db(db_path)
        db = next(get_db(db_path))

        chain_id = 5
        output_dir = "/tmp"
        verbose = False
        export = Export.allocations

        start_date = None
        duration = None
        process_vestings(db, chain_id, verbose, start_date, duration)

        result = export_data(
            db,
            chain_id,
            output_dir,
            verbose,
            export,
        )
        self.assertEqual(len(result), 21)
        expected = [
            {
                "proof": [],
                "tag": "user",
                "account": "0x5f310dc66F4ecDE9a1769f1B7D75224dA592201e",
                "chainId": 5,
                "contract": "0x07dA2049Fa8127eF6280631BCbc56881d764C8Ee",
                "vestingId": "0x76699f526e8c062cc9db2004f7f3130a911208b3a18fc575760f830a73479011",
                "durationWeeks": 416,
                "startDate": 1531526400,
                "amount": "23023120000000000000000",
                "curve": 0,
            },
            {
                "proof": [],
                "tag": "user_v2",
                "account": "0x5f310dc66F4ecDE9a1769f1B7D75224dA592201e",
                "chainId": 5,
                "contract": "0x864c87C1bC9D29DFB59752336292520Ede64E5Eb",
                "vestingId": "0x1e98e82b20b75cf087ab93e767219456ec4a629687408ec622deadaf642bae19",
                "durationWeeks": 208,
                "startDate": 1662026400,
                "amount": "420690000000000000000",
                "curve": 0,
            },
            {
                "proof": [],
                "tag": "ecosystem",
                "account": "0x5f310dc66F4ecDE9a1769f1B7D75224dA592201e",
                "chainId": 5,
                "contract": "0xEc6449091Ae23A92f856702F9452011E31E66C63",
                "vestingId": "0x5255888c86231e3d91e0bb705953cfc1b8a9071d387db27a805382ec38354919",
                "durationWeeks": 416,
                "startDate": 1531526400,
                "amount": "43023120000000000000000",
                "curve": 0,
            },
        ]

        data = json.loads(
            json.dumps(
                result["0x5f310dc66F4ecDE9a1769f1B7D75224dA592201e"],
                indent=4,
                cls=VestingEncoder,
            )
        )
        self.assertEqual(data, expected)


if __name__ == "__main__":
    unittest.main()
