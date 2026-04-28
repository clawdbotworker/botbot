from datetime import date

from debt_portfolio_analyzer.models import Account, AccountType
from debt_portfolio_analyzer.scoring import score_account


TODAY = date(2026, 4, 28)


def _good_account(**kw) -> Account:
    base = dict(
        account_id="g1",
        debtor_state="CA",
        debtor_phone="555-0000",
        debtor_email="g@example.com",
        debtor_address="1 Main St",
        account_type=AccountType.CREDIT_CARD,
        original_balance=4000.0,
        current_balance=3800.0,
        charge_off_date=date(2026, 1, 15),
        last_payment_date=date(2025, 10, 1),
        last_payment_amount=120.0,
        date_of_first_delinquency=date(2025, 7, 1),
        has_signed_agreement=True,
        has_statements=True,
        has_chain_of_title=True,
        times_sold=1,
    )
    base.update(kw)
    return Account(**base)


def test_fresh_well_documented_account_scores_high():
    s = score_account(_good_account(), today=TODAY)
    assert s.score >= 80
    assert s.expected_recovery_rate >= 0.08
    assert not s.is_hard_stop


def test_hard_stop_zeroes_out_recovery():
    s = score_account(_good_account(bankruptcy_flag=True), today=TODAY)
    assert s.is_hard_stop
    assert s.score == 0
    assert s.expected_recovery_rate == 0.0
    assert s.expected_recovery == 0.0


def test_aged_undocumented_account_scores_low():
    a = _good_account(
        charge_off_date=date(2017, 1, 1),
        date_of_first_delinquency=date(2016, 6, 1),
        last_payment_date=None,
        last_payment_amount=0.0,
        has_signed_agreement=False,
        has_statements=False,
        has_chain_of_title=False,
        times_sold=4,
    )
    s = score_account(a, today=TODAY)
    assert s.score < 30
    assert s.expected_recovery_rate <= 0.01


def test_time_barred_penalizes_score():
    sol_state = "CA"  # SOL = 4 years
    fresh = score_account(_good_account(debtor_state=sol_state), today=TODAY)
    barred = score_account(_good_account(
        debtor_state=sol_state,
        date_of_first_delinquency=date(2018, 1, 1),
        charge_off_date=date(2018, 6, 1),
        last_payment_date=None,
        last_payment_amount=0.0,
    ), today=TODAY)
    assert barred.score < fresh.score
    assert any(f.code == "TIME_BARRED" for f in barred.flags)


def test_score_bounded_0_100():
    a = _good_account(current_balance=10_000_000)
    s = score_account(a, today=TODAY)
    assert 0 <= s.score <= 100
