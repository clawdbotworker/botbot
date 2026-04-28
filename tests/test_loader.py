from datetime import date
from pathlib import Path

from debt_portfolio_analyzer.loader import load_tape, load_tape_from_rows
from debt_portfolio_analyzer.models import AccountType


SAMPLE = Path(__file__).resolve().parent.parent / "examples" / "sample_tape.csv"


def test_load_sample_tape():
    portfolio = load_tape(SAMPLE)
    assert portfolio.size == 20
    a = next(a for a in portfolio.accounts if a.account_id == "A001")
    assert a.account_type == AccountType.CREDIT_CARD
    assert a.debtor_state == "CA"
    assert a.current_balance == 3850.50
    assert a.has_chain_of_title is True
    assert a.charge_off_date == date(2025, 4, 10)


def test_load_tape_tolerant_to_aliases_and_formats():
    rows = [
        {
            "id": "X1",
            "Balance": "$1,234.56",
            "State": "tx",
            "co_date": "06/15/2024",
            "type": "Credit-Card",
            "signed_agreement": "yes",
        },
    ]
    p = load_tape_from_rows(rows)
    a = p.accounts[0]
    assert a.account_id == "X1"
    assert a.current_balance == 1234.56
    assert a.debtor_state == "TX"
    assert a.charge_off_date == date(2024, 6, 15)
    assert a.account_type == AccountType.CREDIT_CARD
    assert a.has_signed_agreement is True


def test_load_tape_handles_missing_id():
    rows = [{"current_balance": "100"}]
    p = load_tape_from_rows(rows)
    assert p.accounts[0].account_id == "row_0"


def test_load_tape_unknown_account_type_falls_back_to_other():
    rows = [{"id": "Y", "type": "spaceship_loan"}]
    p = load_tape_from_rows(rows)
    assert p.accounts[0].account_type == AccountType.OTHER
