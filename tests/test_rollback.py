
import csv
import hashlib

import pytest

from src.database import get_connection
from src.pipeline import process_file


def test_rollback_and_recovery(tmp_path):
    filepath = tmp_path / "rollback_test.csv"

    rows = [
        {
            "transaction_id": "ROLLBACK_TEST_001",
            "datetime_transaction": "2026-10-01T10:00:00Z",
            "iban_origine": "TEST_SRC",
            "pays_source": "FR",
            "banque_source": "TEST_BANK",
            "iban_destinataire": "TEST_DST",
            "pays_destinataire": "FR",
            "montant": "100.00",
        },
        {
            "transaction_id": "ROLLBACK_TEST_002",
            "datetime_transaction": "2026-10-01T11:00:00Z",
            "iban_origine": "TEST_SRC",
            "pays_source": "FR",
            "banque_source": "TEST_BANK",
            "iban_destinataire": "TEST_DST",
            "pays_destinataire": "FR",
            "montant": "200.00",
        },
    ]

    with filepath.open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(
            f, fieldnames=rows[0].keys()
        )
        writer.writeheader()
        writer.writerows(rows)

    file_hash = hashlib.sha256(
        filepath.read_bytes()
    ).hexdigest()

    # 1. Une panne survient après la première ligne.
    with pytest.raises(RuntimeError):
        process_file(filepath, fail_after=1)

    # 2. Aucune donnée partielle ne doit rester.
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM processed_files "
                "WHERE file_hash = %s",
                (file_hash,),
            )
            assert cur.fetchone()[0] == 0

            cur.execute(
                "SELECT COUNT(*) FROM transactions "
                "WHERE transaction_id LIKE 'ROLLBACK_TEST_%'"
            )
            assert cur.fetchone()[0] == 0

    # 3. Réessayer doit réussir.
    assert process_file(filepath) is True

    # 4. Un nouveau passage doit être ignoré.
    assert process_file(filepath) is False

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM transactions "
                "WHERE file_hash = %s",
                (file_hash,),
            )
            assert cur.fetchone()[0] == 2

            cur.execute(
                "SELECT total FROM aggregates "
                "WHERE category = 'bank' "
                "AND entity_key = 'TEST_BANK'"
            )
            assert cur.fetchone()[0] == 300

            # Nettoyage des données du test.
            cur.execute(
                "DELETE FROM transactions "
                "WHERE file_hash = %s",
                (file_hash,),
            )
            cur.execute(
                "DELETE FROM processed_files "
                "WHERE file_hash = %s",
                (file_hash,),
            )
            cur.execute(
                "DELETE FROM aggregates "
                "WHERE category = 'bank' "
                "AND entity_key = 'TEST_BANK'"
            )
            cur.execute(
                "DELETE FROM aggregates "
                "WHERE category IN ('sender', 'receiver') "
                "AND entity_key IN ('TEST_SRC', 'TEST_DST')"
            )
