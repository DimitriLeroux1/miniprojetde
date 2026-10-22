
import csv
from pathlib import Path

OUTPUT_DIR = Path("data")

FIELDS = [
    "transaction_id",
    "datetime_transaction",
    "iban_origine",
    "pays_source",
    "banque_source",
    "iban_destinataire",
    "pays_destinataire",
    "montant",
]

TRANSACTIONS = [
    ("T001", "FR_SOURCE_1", "BNP", "FR_DEST_1", "1000.00"),
    ("T002", "FR_SOURCE_1", "BNP", "FR_DEST_2", "6000.00"),
    ("T003", "FR_SOURCE_2", "SG", "FR_DEST_1", "2500.00"),
    ("T004", "FR_SOURCE_3", "BNP", "FR_DEST_3", "7000.00"),
    ("T005", "FR_SOURCE_2", "SG", "FR_DEST_2", "500.00"),
    ("T006", "FR_SOURCE_1", "BNP", "FR_DEST_3", "2000.00"),
    ("T007", "FR_SOURCE_4", "CA", "FR_DEST_1", "8000.00"),
    ("T008", "FR_SOURCE_4", "CA", "FR_DEST_2", "3000.00"),
    ("T009", "FR_SOURCE_3", "BNP", "FR_DEST_1", "1500.00"),
    ("T010", "FR_SOURCE_2", "SG", "FR_DEST_3", "5500.00"),
    ("T011", "FR_SOURCE_5", "CA", "FR_DEST_2", "4000.00"),
    ("T012", "FR_SOURCE_5", "CA", "FR_DEST_1", "6500.00"),
    ("T013", "FR_SOURCE_1", "BNP", "FR_DEST_2", "5000.00"),
    ("T014", "FR_SOURCE_3", "BNP", "FR_DEST_3", "9000.00"),
    ("T015", "FR_SOURCE_4", "CA", "FR_DEST_1", "1000.00"),
]


def generate_csv_files():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for index in range(3):
        filename = OUTPUT_DIR / f"transactions_{index + 1}.csv"

        start = index * 5
        batch = TRANSACTIONS[start:start + 5]

        with filename.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writeheader()

            for offset, tx in enumerate(batch):
                transaction_id, origin, bank, dest, amount = tx

                writer.writerow({
                    "transaction_id": transaction_id,
                    "datetime_transaction":
                        f"2026-10-{index + 1:02d}T{10 + offset:02d}:00:00Z",
                    "iban_origine": origin,
                    "pays_source": "FR",
                    "banque_source": bank,
                    "iban_destinataire": dest,
                    "pays_destinataire": "FR",
                    "montant": amount,
                })

        print(f"Fichier généré : {filename}")


if __name__ == "__main__":
    generate_csv_files()
