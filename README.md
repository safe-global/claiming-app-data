# claiming-app-data
Vesting data converter and proofs generator.

Guardian data converter, address resolver, and image loader. All images are scaled and converted to PNG.


# Endpoints

## Staging endpoints

List of guardians
```
https://safe-claiming-app-data.staging.5afe.dev/guardians/guardians.json
```
Guardian images
```
https://safe-claiming-app-data.staging.5afe.dev/guardians/images/\(address_checksummed)_\(scale=1|2|3)x.png
```
Allocation
```
https://safe-claiming-app-data.staging.5afe.dev/allocations/{chain_id}/{address}.json
```
Snapshot allocations
```
https://safe-claiming-app-data.staging.5afe.dev/allocations/{chain_id}/snapshot-allocations-data.json
```

## Production endpoints
```
https://safe-claiming-app-data.gnosis-safe.io/guardians/guardians.json
```
Guardian images
```
https://safe-claiming-app-data.gnosis-safe.io/guardians/images/\(address_checksummed)_\(scale=1|2|3)x.png
```
Allocation
```
https://safe-claiming-app-data.gnosis-safe.io/allocations/{chain_id}/{address}.json
```
Snapshot allocations
```
https://safe-claiming-app-data.gnosis-safe.io/allocations/{chain_id}/snapshot-allocations-data.json
```


# Deployments


## Guardians

### Staging

Deployment on staging can be started using `Deploy Guardians` action. Action runs only on `main` branch and can be started manually.

### Production
Deployment to production is done with `Deploy All (Release)` action. Action is triggered by publishing new release:
1. Draft a release and tag it with vx.y.z version tag. 
2. Deployment action will be triggered for release.
3. Ask devops to deploy data to production.

### Prerequisites

- Place csv with guardian data under `guardians/assets/guardians.csv`.

- Not all guardian images could be scaled to square dimensions without distorting the image. 
Separate versions of images were created and placed under `guardians/assets/images` for such guardians. 
This image collection should be extended if another guardian is added, that has long or wide image. 
Images from `guardians/assets/images` will be taken for a guardian during conversion instead of an image specified by a link.

- Naming convention for image files under `guardians/assets/images`:
```
<guardian name>.png
```

### Guardians CSV 
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

### Guardians file structure
```
[
    {
        "name": "guardian name",
        "address": "checksummed address",
        "ens": "ens name if available",
        "image" "(address_checksummed)_3x.png"
        "reason": "reason for becoming a delegate",
        "contribution": "former contributions"
    },
    ...
]
```

## Vesting Data

### Staging

Deployment on staging can be started using `Deploy Vestings` action. Action runs only on `main` branch and can be started manually.
Workflow input parameter `chain_id` must be selected before action can be started.

### Production

Deployment to production is done with `Deploy All (Release)` action. Action is triggered by publishing new release.
1. Draft a release and tag it with vx.y.z version tag. 
2. Deployment action will be triggered for release.
3. Ask devops to deploy data to production.

### Prerequisites

- Place csv files with vesting data under `vestings/assets/{chain_id}/{type}_airdrop.csv`.
Naming should be `user_airdrop.csv` for user airdrop and `ecosystem_airdrop.csv` for ecosystem airdrop (`type` is `user` or `ecosystem`).

### Vesting csv
Vesting csv file contains following fields

 - Owner address
 - Vesting duration in weeks
 - Vesting start date (ISO 8601 Format)
 - Vesting amount in wei

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

##### Snapshot file (`--export snapshot`)
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


# Setting up locally
Create python virtual environment
```
mkdir env
python -m venv env
```
Activate a virtual environment
```
source env/bin/activate
```
Install dependencies
```
pip install -r requirements.txt
```

## Guardians

Place guardians.csv under `guardians/assets`

Custom guardian images should be placed under `guardians/assets/images`

Make your infura project id available for guardian processing script
```
export INFURA_PROJECT_ID=<your infura project id>
```

### Generating

Start guardian data processing by running
```
python import_guardians.py
```

Generated data will be placed under `../data/guardians`

Guardians list: `../data/guardians/guardians.json`

Guardian images: `../data/guardians/images/`

## Vestings

Place vesting csv files for a network under `vestings/assets/{chain_id}`. 
Naming should be `user_airdrop.csv` for user airdrop and `ecosystem_airdrop.csv` for ecosystem airdrop.

### Generating

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


# Contribute
You can contribute to this repo by creating a Pull Request or an issue. Please follow the default template set for the Pull Requests.
