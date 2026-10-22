
CREATE TABLE IF NOT EXISTS processed_files (
    file_hash CHAR(64) PRIMARY KEY,
    filename TEXT NOT NULL,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(100) PRIMARY KEY,

    file_hash CHAR(64) NOT NULL
        REFERENCES processed_files(file_hash),

    datetime_transaction TIMESTAMPTZ NOT NULL,

    iban_origine VARCHAR(34) NOT NULL,
    pays_source VARCHAR(2) NOT NULL,
    banque_source VARCHAR(100) NOT NULL,

    iban_destinataire VARCHAR(34) NOT NULL,
    pays_destinataire VARCHAR(2) NOT NULL,

    montant NUMERIC(15,2) NOT NULL
        CHECK (montant >= 0),

    flag BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS aggregates (
    category VARCHAR(30) NOT NULL,
    entity_key VARCHAR(100) NOT NULL,
    total NUMERIC(18,2) NOT NULL DEFAULT 0,

    PRIMARY KEY (category, entity_key)
);
