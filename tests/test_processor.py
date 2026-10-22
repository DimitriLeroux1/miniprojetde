
from decimal import Decimal

from src.processor import (
    sum_by_origin_iban,
    sum_by_source_bank,
    sum_by_destination_iban,
    flag_large_transactions,
)


TRANSACTIONS = [
    {
        "transaction_id": "T001",
        "iban_origine": "FR_SOURCE_1",
        "banque_source": "BNP",
        "iban_destinataire": "FR_DEST_1",
        "montant": "1000.00",
    },
    {
        "transaction_id": "T002",
        "iban_origine": "FR_SOURCE_1",
        "banque_source": "BNP",
        "iban_destinataire": "FR_DEST_2",
        "montant": "6000.00",
    },
    {
        "transaction_id": "T003",
        "iban_origine": "FR_SOURCE_2",
        "banque_source": "SG",
        "iban_destinataire": "FR_DEST_1",
        "montant": "2500.00",
    },
]


def test_sum_by_origin_iban():
    result = sum_by_origin_iban(TRANSACTIONS)

    assert result["FR_SOURCE_1"] == Decimal("7000")
    assert result["FR_SOURCE_2"] == Decimal("2500")


def test_sum_by_source_bank():
    result = sum_by_source_bank(TRANSACTIONS)

    assert result["BNP"] == Decimal("7000")
    assert result["SG"] == Decimal("2500")


def test_sum_by_destination_iban():
    result = sum_by_destination_iban(TRANSACTIONS)

    assert result["FR_DEST_1"] == Decimal("3500")
    assert result["FR_DEST_2"] == Decimal("6000")


def test_flag_large_transactions():
    result = flag_large_transactions(TRANSACTIONS)

    assert result[0]["flag"] is False
    assert result[1]["flag"] is True
    assert result[2]["flag"] is False


def test_exactly_5000_not_flagged():
    transactions = [
        {"montant": "5000.00"},
        {"montant": "5000.01"},
    ]

    result = flag_large_transactions(transactions)

    assert result[0]["flag"] is False
    assert result[1]["flag"] is True


def test_processor_does_not_modify_input():
    original = [dict(tx) for tx in TRANSACTIONS]

    flag_large_transactions(TRANSACTIONS)

    assert TRANSACTIONS == original
