
import os
import hashlib
from datetime import datetime

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Ouvre une connexion PostgreSQL."""
    return psycopg2.connect(
        os.environ["DATABASE_URL"]
    )


def calculate_file_hash(filepath):
    """Calcule le SHA-256 du contenu d'un CSV."""
    sha256 = hashlib.sha256()

    with open(filepath, "rb") as file:
        for chunk in iter(
            lambda: file.read(65536), b""
        ):
            sha256.update(chunk)

    return sha256.hexdigest()


def upsert_aggregates(cursor, category, totals):
    """Ajoute les montants aux agrégats existants."""
    for key, total in totals.items():
        cursor.execute(
            """
            INSERT INTO aggregates (
                category, entity_key, total
            )
            VALUES (%s, %s, %s)
            ON CONFLICT (category, entity_key)
            DO UPDATE SET
                total = aggregates.total + EXCLUDED.total
            """,
            (category, key, total)
        )


def insert_file_results(
    filepath,
    transactions,
    sender_totals,
    bank_totals,
    receiver_totals,
):
    """
    Insère un fichier et ses résultats atomiquement.
    Retourne False si le fichier est déjà traité.
    """
    file_hash = calculate_file_hash(filepath)

    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO processed_files (
                    file_hash, filename
                )
                VALUES (%s, %s)
                ON CONFLICT (file_hash) DO NOTHING
                RETURNING file_hash
                """,
                (file_hash, os.path.basename(filepath))
            )

            if cursor.fetchone() is None:
                print(f"Déjà traité : {filepath}")
                return False

            for tx in transactions:
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
                        datetime.fromisoformat(
                            tx["datetime_transaction"]
                        ),
                        tx["iban_origine"],
                        tx["pays_source"],
                        tx["banque_source"],
                        tx["iban_destinataire"],
                        tx["pays_destinataire"],
                        tx["montant"],
                        tx["flag"],
                    )
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
    print(f"Fichier inséré : {filepath}")
    return True
