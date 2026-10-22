
from src.loader import load_all_csv
from src.processor import (
    sum_by_origin_iban,
    sum_by_source_bank,
    sum_by_destination_iban,
    flag_large_transactions,
)


def main():
    transactions = load_all_csv("data")

    print(f"Transactions chargées : {len(transactions)}")

    print("\n=== MONTANTS PAR IBAN ORIGINE ===")
    for iban, total in sum_by_origin_iban(transactions).items():
        print(f"{iban}: {total} €")

    print("\n=== MONTANTS PAR BANQUE ===")
    for bank, total in sum_by_source_bank(transactions).items():
        print(f"{bank}: {total} €")

    print("\n=== MONTANTS PAR IBAN DESTINATAIRE ===")
    for iban, total in sum_by_destination_iban(transactions).items():
        print(f"{iban}: {total} €")

    print("\n=== TRANSACTIONS SUPÉRIEURES À 5000 € ===")
    flagged_transactions = flag_large_transactions(transactions)

    for tx in flagged_transactions:
        if tx["flag"]:
            print(
                f"{tx['transaction_id']} : "
                f"{tx['montant']} €"
            )


if __name__ == "__main__":
    main()
