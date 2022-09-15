#!/bin/bash

cd guardians
#TODO: process guardian data
git branch feature/guardians_data_update
git checkout feature/guardians_data_update
git add ../data/guardians
git commit -m "Update guardians"
git push origin feature/guardians_data_update
