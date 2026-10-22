
from decimal import Decimal

from src.database import get_connection
from src.pipeline import run_pipeline


def test_database_integration():
    # Relancer la pipeline doit être sans effet
    # sur des fichiers déjà insérés.
    run_pipeline()
    run_pipeline()

    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                "SELECT COUNT(*) FROM transactions"
            )
            assert cursor.fetchone()[0] == 15

            cursor.execute(
                "SELECT COUNT(*) FROM processed_files"
            )
            assert cursor.fetchone()[0] == 3

            cursor.execute(
                """
                SELECT entity_key, total
                FROM aggregates
                WHERE category = 'bank'
                """
            )
            totals = dict(cursor.fetchall())

            assert totals == {
                "BNP": Decimal("31500"),
                "SG": Decimal("8500"),
                "CA": Decimal("22500"),
            }

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM transactions
                WHERE flag = TRUE
                """
            )
            assert cursor.fetchone()[0] == 6
