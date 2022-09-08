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
