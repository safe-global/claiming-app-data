import json
import unittest
import uuid

from database import get_db, prepare_db
from exporter import Export, VestingEncoder, export_data, process_vestings


class TestExporter(unittest.TestCase):
    def test_export_data(self):
        random_filename = str(uuid.uuid4())
        db_path = f"/tmp/{random_filename}"
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
                "account": "0xC642bEc0e4f69815e89723C09caA8DAa524cAc9c",
                "chainId": 5,
                "contract": "0x07dA2049Fa8127eF6280631BCbc56881d764C8Ee",
                "vestingId": "0x2bb9cf494fe2749da5aa9e392a4e134213930312d22049a4c099dcc48fad3c05",
                "durationWeeks": 416,
                "startDate": 1538042400,
                "amount": "23023120000000000000000",
                "curve": 0,
            },
            {
                "proof": [],
                "tag": "user_v2",
                "account": "0xC642bEc0e4f69815e89723C09caA8DAa524cAc9c",
                "chainId": 5,
                "contract": "0xA19C1d8faAc5d8379e90e22CA8F21cdd938a61ee",
                "vestingId": "0xcdd4faebcbfcfc6140a04951a018228bee1832f463c7c3a2901d60a845547e3b",
                "durationWeeks": 208,
                "startDate": 1662026400,
                "amount": "420690000000000000000",
                "curve": 0,
            },
            {
                "proof": [],
                "tag": "ecosystem",
                "account": "0xC642bEc0e4f69815e89723C09caA8DAa524cAc9c",
                "chainId": 5,
                "contract": "0xEc6449091Ae23A92f856702F9452011E31E66C63",
                "vestingId": "0x6c44fcbabe1216809436b73f63fc1ab4947679e834adcfa89240ed809ac53f17",
                "durationWeeks": 416,
                "startDate": 1538042400,
                "amount": "43023120000000000000000",
                "curve": 0,
            },
        ]

        data = json.loads(
            json.dumps(
                result["0xC642bEc0e4f69815e89723C09caA8DAa524cAc9c"],
                indent=4,
                cls=VestingEncoder,
            )
        )
        self.assertEqual(data, expected)


if __name__ == "__main__":
    unittest.main()
