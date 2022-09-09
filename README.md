# claiming-app-data
Vesting data converter and proofs generator.
Guardian data converter and image loader. Images are scaled and converted to PNG.



## Vesting Data

### Generating

Place vesting csv files for a network under `vestings/assets/{chain_id}`. 
Naming should be `user_airdrop.csv` for user airdrop and `ecosystem_airdrop.csv` for ecosystem airdrop.

Now exporter script can be used to parse vesting csv files, generate proofs, and export data to different formats: either one file for snapshot allocation data or multiple files that contain vesting data for an address. Thea aforementioned steps can be performed at once or separately.

Example:
```
python vestings/exporter.py --chain_id 1 --output-directory ../data/allocations --generate-vestings --generate-proofs --export allocations
```

If you want to see all possible parameters 
```
python vestings/exporter.py -h
```

Exporter will place generated files under `{output_directory}/{chain_id}`

### Deploying to staging

1. Add generated files from data/ folder to repository and commit them.
2. Open PR for merging them to main branch.
3. After PR is merged deployment action will upload files to staging thus making them available.

### Deploying to production

1. Draft a release and tag it with vx.y.z version tag. 
2. Deployment action will be triggered for release.
3. Ask devops to deploy data to production.





