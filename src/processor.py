
from collections import defaultdict
from decimal import Decimal


def sum_by_origin_iban(transactions):
    """Somme des montants envoyés par IBAN origine."""
    totals = defaultdict(lambda: Decimal("0"))

    for tx in transactions:
        iban = tx["iban_origine"]
        totals[iban] += Decimal(tx["montant"])

    return dict(totals)


def sum_by_source_bank(transactions):
    """Somme des montants envoyés par banque source."""
    totals = defaultdict(lambda: Decimal("0"))

    for tx in transactions:
        bank = tx["banque_source"]
        totals[bank] += Decimal(tx["montant"])

    return dict(totals)


def sum_by_destination_iban(transactions):
    """Somme des montants reçus par IBAN destinataire."""
    totals = defaultdict(lambda: Decimal("0"))

    for tx in transactions:
        iban = tx["iban_destinataire"]
        totals[iban] += Decimal(tx["montant"])

    return dict(totals)


def flag_large_transactions(transactions):
    """Signale les transactions supérieures à 5000 euros."""
    result = []

    for tx in transactions:
        new_tx = {
            **tx,
            "flag": Decimal(tx["montant"]) > Decimal("5000")
        }
        result.append(new_tx)

    return result
