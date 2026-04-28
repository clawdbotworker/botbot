from __future__ import annotations

from datetime import date

from debt_portfolio_analyzer.models import Account, Flag, FlagLevel


# Statute of limitations (years) for written contracts / open accounts by US
# state. This is a coarse summary intended for portfolio screening only — not
# legal advice. Some states distinguish written/oral/open-ended; values below
# lean toward the written-contract bucket commonly used for credit-card debt.
# Operators should validate against current state law before acting.
STATE_SOL_YEARS: dict[str, int] = {
    "AL": 6, "AK": 3, "AZ": 6, "AR": 5, "CA": 4, "CO": 6, "CT": 6, "DE": 3,
    "DC": 3, "FL": 5, "GA": 6, "HI": 6, "ID": 5, "IL": 10, "IN": 6, "IA": 10,
    "KS": 5, "KY": 10, "LA": 10, "ME": 6, "MD": 3, "MA": 6, "MI": 6, "MN": 6,
    "MS": 3, "MO": 10, "MT": 8, "NE": 5, "NV": 6, "NH": 3, "NJ": 6, "NM": 6,
    "NY": 6, "NC": 3, "ND": 6, "OH": 8, "OK": 5, "OR": 6, "PA": 4, "RI": 10,
    "SC": 3, "SD": 6, "TN": 6, "TX": 4, "UT": 6, "VT": 6, "VA": 5, "WA": 6,
    "WV": 10, "WI": 6, "WY": 10,
}


def _years_between(start: date, end: date) -> float:
    return (end - start).days / 365.25


def is_time_barred(account: Account, today: date | None = None) -> bool:
    """True if statute of limitations likely expired in the debtor's state.

    Uses date_of_first_delinquency if present, else charge_off_date. If neither
    is available or the state is unknown, returns False (cannot determine).
    """
    today = today or date.today()
    state = (account.debtor_state or "").upper()
    sol = STATE_SOL_YEARS.get(state)
    if sol is None:
        return False
    anchor = account.date_of_first_delinquency or account.charge_off_date
    if anchor is None:
        return False
    return _years_between(anchor, today) > sol


def check_compliance(account: Account, today: date | None = None) -> list[Flag]:
    """Produce compliance flags for a single account.

    Hard stops mean: do not attempt collection.
    Warnings mean: special handling (e.g., time-barred disclosures, missing
    documentation that bars suit).
    Info flags surface things the operator should be aware of.
    """
    today = today or date.today()
    flags: list[Flag] = []

    if account.bankruptcy_flag:
        flags.append(Flag(
            "BANKRUPTCY",
            FlagLevel.HARD_STOP,
            "Account in bankruptcy — automatic stay or discharge may apply.",
        ))
    if account.deceased_flag:
        flags.append(Flag(
            "DECEASED",
            FlagLevel.HARD_STOP,
            "Debtor reported deceased — only estate may be contacted, with restrictions.",
        ))
    if account.cease_desist_flag:
        flags.append(Flag(
            "CEASE_DESIST",
            FlagLevel.HARD_STOP,
            "Cease-and-desist on file — communication restricted under FDCPA.",
        ))
    if account.litigation_flag:
        flags.append(Flag(
            "LITIGATION",
            FlagLevel.HARD_STOP,
            "Active litigation — route to counsel; do not contact directly.",
        ))
    if account.fraud_dispute_flag:
        flags.append(Flag(
            "FRAUD_DISPUTE",
            FlagLevel.HARD_STOP,
            "Account disputed as fraudulent — investigate before any collection activity.",
        ))

    if not account.has_chain_of_title:
        flags.append(Flag(
            "MISSING_CHAIN_OF_TITLE",
            FlagLevel.WARNING,
            "Chain of title not documented — ownership may be challenged.",
        ))
    if not account.has_signed_agreement:
        flags.append(Flag(
            "MISSING_SIGNED_AGREEMENT",
            FlagLevel.WARNING,
            "No signed account agreement on file — proof of debt is weak.",
        ))
    if not account.has_statements:
        flags.append(Flag(
            "MISSING_STATEMENTS",
            FlagLevel.WARNING,
            "No periodic statements on file — balance substantiation is weak.",
        ))

    if is_time_barred(account, today=today):
        flags.append(Flag(
            "TIME_BARRED",
            FlagLevel.WARNING,
            "Likely past statute of limitations in debtor's state — cannot sue; "
            "Reg F disclosure may be required when collecting.",
        ))

    if not account.has_valid_contact:
        flags.append(Flag(
            "NO_VALID_CONTACT",
            FlagLevel.WARNING,
            "No usable address, phone, or email — skip-tracing required before any contact.",
        ))

    if account.times_sold and account.times_sold > 2:
        flags.append(Flag(
            "RESOLD_MULTIPLE",
            FlagLevel.INFO,
            f"Sold {account.times_sold} times — likely already worked; recoveries usually lower.",
        ))

    if not account.debtor_state or account.debtor_state.upper() not in STATE_SOL_YEARS:
        flags.append(Flag(
            "STATE_UNKNOWN",
            FlagLevel.INFO,
            "Debtor state missing or unrecognized — SOL and licensing cannot be evaluated.",
        ))

    return flags
