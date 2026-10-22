
import csv
from pathlib import Path
import io

def load_csv(filepath):
    """Charge les transactions depuis un fichier CSV."""
    filepath = Path(filepath)

    with filepath.open(
        "r", encoding="utf-8", newline=""
    ) as file:
        reader = csv.DictReader(file)
        return list(reader)


def load_all_csv(directory="data"):
    """Charge tous les CSV d'un dossier."""
    directory = Path(directory)
    transactions = []

    for filepath in sorted(directory.glob("*.csv")):
        data = load_csv(filepath)
        transactions.extend(data)

    return transactions

def load_csv_bytes(content):
    """Charge un CSV à partir des octets déjà lus."""
    text = content.decode("utf-8-sig")

    reader = csv.DictReader(io.StringIO(text))
    return list(reader)