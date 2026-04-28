from datetime import date

from debt_portfolio_analyzer.compliance import (
    STATE_SOL_YEARS,
    check_compliance,
    is_time_barred,
)
from debt_portfolio_analyzer.models import Account, AccountType, FlagLevel


def _account(**kw) -> Account:
    base = dict(
        account_id="t1",
        debtor_state="CA",
        debtor_phone="555-0000",
        account_type=AccountType.CREDIT_CARD,
        current_balance=1000.0,
        charge_off_date=date(2024, 1, 1),
        date_of_first_delinquency=date(2023, 7, 1),
        has_signed_agreement=True,
        has_statements=True,
        has_chain_of_title=True,
        times_sold=1,
    )
    base.update(kw)
    return Account(**base)


def test_state_sol_table_covers_50_states_plus_dc():
    assert len(STATE_SOL_YEARS) == 51


def test_time_barred_uses_dofd():
    a = _account(
        debtor_state="CA",  # SOL = 4 years
        date_of_first_delinquency=date(2018, 1, 1),
        charge_off_date=date(2018, 7, 1),
    )
    assert is_time_barred(a, today=date(2026, 4, 28)) is True


def test_not_time_barred_when_within_sol():
    a = _account(
        debtor_state="CA",
        date_of_first_delinquency=date(2024, 6, 1),
        charge_off_date=date(2024, 12, 1),
    )
    assert is_time_barred(a, today=date(2026, 4, 28)) is False


def test_unknown_state_does_not_assert_time_barred():
    a = _account(debtor_state="ZZ", date_of_first_delinquency=date(2000, 1, 1))
    assert is_time_barred(a, today=date(2026, 4, 28)) is False


def test_hard_stop_flags():
    bk = check_compliance(_account(bankruptcy_flag=True))
    assert any(f.code == "BANKRUPTCY" and f.level == FlagLevel.HARD_STOP for f in bk)

    dec = check_compliance(_account(deceased_flag=True))
    assert any(f.code == "DECEASED" and f.level == FlagLevel.HARD_STOP for f in dec)

    cd = check_compliance(_account(cease_desist_flag=True))
    assert any(f.code == "CEASE_DESIST" and f.level == FlagLevel.HARD_STOP for f in cd)

    lit = check_compliance(_account(litigation_flag=True))
    assert any(f.code == "LITIGATION" and f.level == FlagLevel.HARD_STOP for f in lit)


def test_documentation_warnings():
    flags = check_compliance(_account(
        has_chain_of_title=False,
        has_signed_agreement=False,
        has_statements=False,
    ))
    codes = {f.code for f in flags}
    assert "MISSING_CHAIN_OF_TITLE" in codes
    assert "MISSING_SIGNED_AGREEMENT" in codes
    assert "MISSING_STATEMENTS" in codes


def test_no_valid_contact_warning():
    a = _account(
        debtor_phone=None,
        debtor_email=None,
        debtor_address=None,
    )
    flags = check_compliance(a)
    assert any(f.code == "NO_VALID_CONTACT" for f in flags)


def test_resold_multiple_info_flag():
    flags = check_compliance(_account(times_sold=4))
    assert any(f.code == "RESOLD_MULTIPLE" and f.level == FlagLevel.INFO for f in flags)


def test_state_unknown_info_flag():
    flags = check_compliance(_account(debtor_state="ZZ"))
    assert any(f.code == "STATE_UNKNOWN" and f.level == FlagLevel.INFO for f in flags)
