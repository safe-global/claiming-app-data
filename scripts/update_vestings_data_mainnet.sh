#!/bin/bash

cd vestings
python exporter.py --clear-db --chain-id ${1} --process-vestings --generate-proofs --output-directory ../data/allocations
git branch feature/allocations_data_update
git checkout feature/allocations_data_update
git add ../data/allocations/1
git commit -m "Update allocations"
git push origin feature/allocations_data_update
