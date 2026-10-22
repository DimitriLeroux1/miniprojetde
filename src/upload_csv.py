
from pathlib import Path

from src.s3_client import create_bucket, upload_file


def main():
    create_bucket()

    csv_files = sorted(
        Path("data").glob("*.csv")
    )

    if not csv_files:
        raise RuntimeError("Aucun CSV à envoyer")

    for filepath in csv_files:
        upload_file(filepath)

    print(f"\n{len(csv_files)} fichiers envoyés dans S3")


if __name__ == "__main__":
    main()
