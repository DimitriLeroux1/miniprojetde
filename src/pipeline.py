
from pathlib import Path

from src.loader import load_csv_bytes
from src.processor import (
    sum_by_origin_iban,
    sum_by_source_bank,
    sum_by_destination_iban,
    flag_large_transactions,
)
from src.database import insert_file_results


def process_file(filepath, fail_after=None):
    filepath = Path(filepath)

    # Une seule lecture physique du fichier.
    content = filepath.read_bytes()

    transactions = load_csv_bytes(content)

    if not transactions:
        raise ValueError(
            f"Fichier vide : {filepath.name}"
        )

    sender_totals = sum_by_origin_iban(transactions)
    bank_totals = sum_by_source_bank(transactions)
    receiver_totals = sum_by_destination_iban(
        transactions
    )
    flagged = flag_large_transactions(transactions)

    return insert_file_results(
        filepath.name,
        content,
        flagged,
        sender_totals,
        bank_totals,
        receiver_totals,
        fail_after=fail_after,
    )


def run_pipeline():
    csv_files = sorted(Path("data").glob("*.csv"))

    if not csv_files:
        raise RuntimeError("Aucun fichier CSV trouvé")

    inserted = 0
    skipped = 0

    for filepath in csv_files:
        print(f"Traitement : {filepath.name}")

        if process_file(filepath):
            inserted += 1
        else:
            skipped += 1

    print("\n=== BILAN ===")
    print(f"Fichiers insérés : {inserted}")
    print(f"Fichiers ignorés : {skipped}")


if __name__ == "__main__":
    run_pipeline()
