# claiming-app-data
Vesting data converter and proofs generator.

Guardian data converter, address resolver, and image loader. Images are scaled and converted to PNG.

## Guardians

### Guardians csv
Guardians csv file contains following fields

 - Guardian name 
 - Description of reasons for becoming a delegate
 - Description of former contributions
 - Guardian address or ENS name
 - Image url
 - Start Date (UTC)
 - Submit Date (UTC)
 - Network ID
 - Tags

Not all guardian images could be cropped to square dimensions without distorting the image. We have created square image versions for guardians that do not have square images and placed them under
`guardians/assets/images`. This image collection should be extended if another guardian with not square image is added. These images will be taken for a guardian during conversion instead of initially provided image.

Naming convention for image files under `guardians/assets/images`:
```
<guardian name>.png
```

### Generating
Place csv with guardian data under `guardians/assets/guardians.csv`.

TBD


Generated data will be placed under `../data/guardians`

Guardians list: `../data/guardians/guardians.json`

Guardian images: `../data/guardians/images/`

### Deploying to staging

1. Add generated files from data/ folder to repository and commit them.
2. Open PR for merging them to main branch.
3. After PR is merged deployment action will upload files to staging thus making them available.

### Staging endpoints

List of guardians
```
https://safe-claiming-app-data.staging.gnosisdev.com/guardians/guardians.json
```
Guardian images
```
https://safe-claiming-app-data.staging.gnosisdev.com/guardians/images/\(address_checksummed)_\(scale=1|2|3)x.png
```

### Deploying to production

1. Draft a release and tag it with vx.y.z version tag. 
2. Deployment action will be triggered for release.
3. Ask devops to deploy data to production.

### Production endpoints
```
https://safe-claiming-app-data.gnosis-safe.io/guardians/guardians.json
```
Guardian images
```
https://safe-claiming-app-data.gnosis-safe.io/guardians/images/\(address_checksummed)_\(scale=1|2|3)x.png
```


## Vesting Data

### Vesting csv
Vesting csv file contains following fields

 - Owner address
 - Vesting duration in weeks
 - Vesting start date (ISO 8601 Format)
 - Vesting amount in wei


### Generating

Place vesting csv files for a network under `vestings/assets/{chain_id}`. 
Naming should be `user_airdrop.csv` for user airdrop and `ecosystem_airdrop.csv` for ecosystem airdrop.

Now exporter script can be used to parse vesting csv files, generate proofs, and export data to different formats: either one file for snapshot allocation data or multiple files that contain vesting data for an address. The aforementioned steps can be performed at once or separately.

Example:
```
python vestings/exporter.py --chain_id 1 --output-directory ../data/allocations --generate-vestings --generate-proofs --export allocations
```

If you want to see all possible parameters 
```
python vestings/exporter.py -h
```

Exporter will place generated files under `{output_directory}/{chain_id}`

### Allocation file structure

#### Vesting file (`--export allocations`)
Contains all defined allocations for a specific address with proofs.
```
[
    {
        "tag": "[user | ecosystem]",
        "account": "checksummed address",
        "chainId": chain id,
        "contract": "checksummed airdrop contract addres",
        "vestingId": "vesting hash",
        "durationWeeks": integer,
        "startDate": timestamp,
        "amount": "amount in wei",
        "curve": integer,
        "proof": [
        ]
    },
    ...
 ]
```

#### Snapshot file (`--export snapshot`)
Contains all defined allocation. Proofs are not included.
```
[
    [
        {
            "tag": "[user | ecosystem]",
            "account": "checksummed address",
            "chainId": chain id,
            "contract": "checksummed airdrop contract addres",
            "vestingId": "vesting hash",
            "durationWeeks": integer,
            "startDate": timestamp,
            "amount": "amount in wei",
            "curve": integer 
        },
        ...
    ],
    ...
]
```

### Deploying to staging

1. Add generated files from data/ folder to repository and commit them.
2. Open PR for merging them to main branch.
3. After PR is merged deployment action will upload files to staging thus making them available.

### Staging endpoints

Allocation
```
https://safe-claiming-app-data.staging.gnosisdev.com/allocations/{chain_id}/{address}.json
```
Snapshot allocations
```
https://safe-claiming-app-data.staging.gnosisdev.com/allocations/{chain_id}/snapshot-allocations-data.json
```

### Deploying to production

1. Draft a release and tag it with vx.y.z version tag. 
2. Deployment action will be triggered for release.
3. Ask devops to deploy data to production.

### Production endpoints

Allocation
```
https://safe-claiming-app-data.gnosis-safe.io/allocations/{chain_id}/{address}.json
```
Snapshot allocations
```
https://safe-claiming-app-data.gnosis-safe.io/allocations/{chain_id}/snapshot-allocations-data.json
```


## Contribute
You can contribute to this repo by creating a Pull Request or an issue. Please follow the default template set for the Pull Requests.