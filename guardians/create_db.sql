CREATE TABLE IF NOT EXISTS guardians (
    id TEXT NOT NULL PRIMARY KEY,
    address_or_ens TEXT NOT NULL,
    address TEXT,
    chain_id INTEGER NOT NULL DEFAULT 1,
    name TEXT NOT NULL,
    ens TEXT,
    image_url TEXT,
    image_src BLOB,
    image_1x BLOB,
    image_2x BLOB,
    image_3x BLOB,
    reason TEXT,
    contribution TEXT
);

CREATE TABLE IF NOT EXISTS vestings (
    chain_id INTEGER NOT NULL,
    contract TEXT NOT NULL,
    vesting_id TEXT NOT NULL,
    account TEXT NOT NULL,
    duration_weeks INTEGER NOT NULL,
    start_date INTEGER,
    amount TEXT,
    curve INTEGER DEFAULT 0,
    proof TEXT,
    CONSTRAINT con_vestings_pk PRIMARY KEY (chain_id, contract, vesting_id)
);

CREATE INDEX idx_vestings_owner ON vestings(account);
