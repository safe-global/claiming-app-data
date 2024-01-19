#!/bin/sh

python vestings/tests.py
python vestings/exporter.py --chain-id 5 --output-directory data/allocations
