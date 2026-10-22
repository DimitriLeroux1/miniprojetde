
import hashlib
import os

import psycopg2
from dotenv import load_dotenv
from psycopg2 import OperationalError
from psycopg2.errors import (
    DeadlockDetected,
    SerializationFailure,
)

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])


def calculate_file_hash(content: bytes):
    return hashlib.sha256(content).hexdigest()


def upsert_aggregates(cursor, category, totals):
    for key, total in totals.items():
        cursor.execute(
            """
            INSERT INTO aggregates
                (category, entity_key, total)
            VALUES (%s, %s, %s)
            ON CONFLICT (category, entity_key)
            DO UPDATE SET
                total = aggregates.total + EXCLUDED.total
            """,
            (category, key, total),
        )


def _insert_once(
    filename,
    content,
    transactions,
    sender_totals,
    bank_totals,
    receiver_totals,
    fail_after=None,
):
    file_hash = calculate_file_hash(content)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO processed_files
                    (file_hash, filename)
                VALUES (%s, %s)
                ON CONFLICT (file_hash) DO NOTHING
                RETURNING file_hash
                """,
                (file_hash, filename),
            )

            if cursor.fetchone() is None:
                logger.info(
                    "Fichier déjà traité : %s", filename
                )
                return False

            for index, tx in enumerate(transactions, 1):
                cursor.execute(
                    """
                    INSERT INTO transactions (
                        transaction_id,
                        file_hash,
                        datetime_transaction,
                        iban_origine,
                        pays_source,
                        banque_source,
                        iban_destinataire,
                        pays_destinataire,
                        montant,
                        flag
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        tx["transaction_id"],
                        file_hash,
                        tx["datetime_transaction"],
                        tx["iban_origine"],
                        tx["pays_source"],
                        tx["banque_source"],
                        tx["iban_destinataire"],
                        tx["pays_destinataire"],
                        tx["montant"],
                        tx["flag"],
                    ),
                )

                # Simulation volontaire d'une erreur.
                # Réservé aux tests, jamais à la production.
                if fail_after is not None and index == fail_after:
                    raise RuntimeError(
                        "Simulation : échec pendant insertion"
                    )

            upsert_aggregates(
                cursor, "sender", sender_totals
            )
            upsert_aggregates(
                cursor, "bank", bank_totals
            )
            upsert_aggregates(
                cursor, "receiver", receiver_totals
            )

    # Commit automatique si aucune exception.
    return True


@retry(
    retry=retry_if_exception_type((
        OperationalError,
        DeadlockDetected,
        SerializationFailure,
    )),
    stop=stop_after_attempt(4),
    wait=wait_exponential(
        multiplier=1,
        min=1,
        max=8,
    ),
    before_sleep=before_sleep_log(
        logger, logging.WARNING
    ),
    reraise=True,
)
def insert_file_results(
    filename,
    content,
    transactions,
    sender_totals,
    bank_totals,
    receiver_totals,
    fail_after=None,
):
    return _insert_once(
        filename,
        content,
        transactions,
        sender_totals,
        bank_totals,
        receiver_totals,
        fail_after,
    )
