from datetime import date

from debt_portfolio_analyzer.models import Account, AccountType
from debt_portfolio_analyzer.roi import estimate_roi
from debt_portfolio_analyzer.scoring import score_account


TODAY = date(2026, 4, 28)


def _good_account(account_id: str = "g", **kw) -> Account:
    base = dict(
        account_id=account_id,
        debtor_state="CA",
        debtor_phone="555-0000",
        account_type=AccountType.CREDIT_CARD,
        current_balance=5000.0,
        charge_off_date=date(2026, 2, 1),
        date_of_first_delinquency=date(2025, 8, 1),
        last_payment_date=date(2025, 11, 1),
        last_payment_amount=100.0,
        has_signed_agreement=True,
        has_statements=True,
        has_chain_of_title=True,
        times_sold=1,
    )
    base.update(kw)
    return Account(**base)


def test_hard_stops_excluded_from_collectable_face_value():
    scored = [
        score_account(_good_account("g1"), today=TODAY),
        score_account(_good_account("g2", bankruptcy_flag=True), today=TODAY),
    ]
    roi = estimate_roi(scored, purchase_price=500.0)
    assert roi.face_value == 10_000.0
    assert roi.collectable_face_value == 5_000.0


def test_breakeven_above_purchase_price_implies_positive_roi():
    scored = [score_account(_good_account(f"a{i}"), today=TODAY) for i in range(20)]
    purchase = 100.0
    roi = estimate_roi(scored, purchase_price=purchase)
    assert roi.breakeven_purchase_price > purchase
    assert roi.roi_mid > 0
    assert roi.recommended_max_purchase_price < roi.breakeven_purchase_price


def test_zero_purchase_price_does_not_divide_by_zero():
    scored = [score_account(_good_account("a1"), today=TODAY)]
    roi = estimate_roi(scored, purchase_price=0.0)
    assert roi.roi_mid == 0.0


def test_recovery_low_mid_high_ordered():
    scored = [score_account(_good_account(f"a{i}"), today=TODAY) for i in range(5)]
    roi = estimate_roi(scored, purchase_price=100.0)
    assert (
        roi.expected_gross_recovery_low
        <= roi.expected_gross_recovery_mid
        <= roi.expected_gross_recovery_high
    )
