
from src.s3_client import (
    list_csv_files,
    download_file,
)
from src.loader import load_csv_bytes
from src.pipeline import run_pipeline
from src.database import get_connection


def test_s3_to_postgresql():
    files = list_csv_files()

    assert len(files) == 3

    transactions = []

    for key in files:
        content = download_file(key)
        transactions.extend(load_csv_bytes(content))

    assert len(transactions) == 15

    run_pipeline()

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM transactions"
            )
            assert cursor.fetchone()[0] == 15

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM processed_files
                """
            )
            assert cursor.fetchone()[0] == 3

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM transactions
                WHERE flag = TRUE
                """
            )
            assert cursor.fetchone()[0] == 6

    run_pipeline()

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM transactions"
            )
            assert cursor.fetchone()[0] == 15
