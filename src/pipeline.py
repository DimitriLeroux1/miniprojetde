
from pathlib import PurePosixPath

from src.loader import load_csv_bytes
from src.processor import (
    sum_by_origin_iban,
    sum_by_source_bank,
    sum_by_destination_iban,
    flag_large_transactions,
)
from src.database import insert_file_results
from src.s3_client import (
    list_csv_files,
    download_file,
)


def process_content(filename, content):
    """Traite les octets d'un CSV, indépendamment
    de son origine (S3 ou autre).
    """
    transactions = load_csv_bytes(content)

    if not transactions:
        raise ValueError(f"Fichier vide : {filename}")

    sender_totals = sum_by_origin_iban(transactions)
    bank_totals = sum_by_source_bank(transactions)
    receiver_totals = sum_by_destination_iban(
        transactions
    )
    flagged = flag_large_transactions(transactions)

    return insert_file_results(
        filename,
        content,
        flagged,
        sender_totals,
        bank_totals,
        receiver_totals,
    )


def process_s3_file(key):
    """Télécharge un CSV depuis S3 puis le traite."""
    print(f"Téléchargement S3 : {key}")

    content = download_file(key)

    filename = PurePosixPath(key).name
    return process_content(filename, content)


def run_pipeline():
    csv_keys = list_csv_files()

    if not csv_keys:
        raise RuntimeError("Aucun CSV trouvé sur S3")

    inserted = 0
    skipped = 0

    for key in csv_keys:
        if process_s3_file(key):
            inserted += 1
        else:
            skipped += 1

    print("\n=== BILAN S3 ===")
    print(f"Fichiers insérés : {inserted}")
    print(f"Fichiers ignorés : {skipped}")


if __name__ == "__main__":
    run_pipeline()
