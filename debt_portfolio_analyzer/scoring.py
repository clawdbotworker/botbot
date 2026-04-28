from __future__ import annotations

from datetime import date

from debt_portfolio_analyzer.compliance import check_compliance
from debt_portfolio_analyzer.models import (
    Account,
    AccountType,
    FlagLevel,
    Portfolio,
    ScoredAccount,
)


# Recovery-rate buckets keyed by the upper-bound score. Empirical industry
# anchors: fresh, well-documented credit-card paper recovers in the low-to-mid
# teens; aged tertiary paper recovers under 1%.
_RECOVERY_BUCKETS: list[tuple[int, float]] = [
    (20, 0.003),
    (40, 0.010),
    (60, 0.030),
    (80, 0.080),
    (100, 0.150),
]


_TYPE_MODIFIER: dict[AccountType, int] = {
    AccountType.CREDIT_CARD: 0,
    AccountType.MEDICAL: -3,       # documentation often weaker; HIPAA care needed
    AccountType.AUTO: -5,          # often deficiency balances, contested
    AccountType.PERSONAL_LOAN: 2,
    AccountType.UTILITY: -2,
    AccountType.TELECOM: -2,
    AccountType.RETAIL: 0,
    AccountType.STUDENT: -10,      # federal vs private complexity
    AccountType.OTHER: -3,
}


def _age_score(account: Account, today: date) -> int:
    """+/- score component for charge-off age. Newer is better."""
    if account.charge_off_date is None:
        return -5
    months = (today.year - account.charge_off_date.year) * 12 + (
        today.month - account.charge_off_date.month
    )
    if months < 0:
        return 0
    if months <= 6:
        return 20
    if months <= 12:
        return 12
    if months <= 24:
        return 5
    if months <= 48:
        return -5
    if months <= 72:
        return -12
    return -20


def _last_payment_score(account: Account, today: date) -> int:
    if account.last_payment_date is None or account.last_payment_amount <= 0:
        return 0
    months = (today.year - account.last_payment_date.year) * 12 + (
        today.month - account.last_payment_date.month
    )
    if months <= 12:
        return 8
    if months <= 24:
        return 4
    return 0


def _balance_score(account: Account) -> int:
    """Tiny balances are uneconomic; very large balances skew toward dispute."""
    bal = account.current_balance
    if bal <= 0:
        return -10
    if bal < 100:
        return -8
    if bal < 500:
        return 0
    if bal < 5_000:
        return 4
    if bal < 25_000:
        return 2
    return -3


def _docs_score(account: Account) -> int:
    score = 0
    if account.has_chain_of_title:
        score += 6
    if account.has_signed_agreement:
        score += 6
    if account.has_statements:
        score += 4
    return score


def _contact_score(account: Account) -> int:
    score = 0
    if account.debtor_phone:
        score += 4
    if account.debtor_email:
        score += 2
    if account.debtor_address and account.debtor_state:
        score += 4
    return score


def _times_sold_penalty(account: Account) -> int:
    if account.times_sold <= 1:
        return 0
    return -min(15, 4 * (account.times_sold - 1))


def _recovery_rate_for(score: int) -> float:
    score = max(0, min(100, score))
    for upper, rate in _RECOVERY_BUCKETS:
        if score <= upper:
            return rate
    return _RECOVERY_BUCKETS[-1][1]


def score_account(account: Account, today: date | None = None) -> ScoredAccount:
    today = today or date.today()
    flags = check_compliance(account, today=today)
    is_hard_stop = any(f.level == FlagLevel.HARD_STOP for f in flags)

    raw = 50
    raw += _age_score(account, today)
    raw += _last_payment_score(account, today)
    raw += _balance_score(account)
    raw += _docs_score(account)
    raw += _contact_score(account)
    raw += _times_sold_penalty(account)
    raw += _TYPE_MODIFIER.get(account.account_type, 0)

    if any(f.code == "TIME_BARRED" for f in flags):
        raw -= 25
    if any(f.code == "NO_VALID_CONTACT" for f in flags):
        raw -= 8

    score = max(0, min(100, raw))
    if is_hard_stop:
        score = 0
        rate = 0.0
    else:
        rate = _recovery_rate_for(score)

    return ScoredAccount(
        account=account,
        score=score,
        expected_recovery_rate=rate,
        flags=flags,
    )


def score_portfolio(portfolio: Portfolio, today: date | None = None) -> list[ScoredAccount]:
    today = today or date.today()
    return [score_account(a, today=today) for a in portfolio.accounts]
