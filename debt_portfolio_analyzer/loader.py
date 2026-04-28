from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

from debt_portfolio_analyzer.models import Account, AccountType, Portfolio


_DATE_FORMATS = (
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%m/%d/%y",
    "%Y/%m/%d",
    "%d-%b-%Y",
)


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    s = value.strip()
    if not s:
        return None
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _parse_float(value: str | None) -> float:
    if value is None:
        return 0.0
    s = str(value).strip().replace("$", "").replace(",", "")
    if not s:
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def _parse_bool(value: str | None) -> bool:
    if value is None:
        return False
    s = str(value).strip().lower()
    return s in {"1", "true", "t", "yes", "y"}


def _parse_int(value: str | None, default: int = 0) -> int:
    if value is None:
        return default
    s = str(value).strip()
    if not s:
        return default
    try:
        return int(float(s))
    except ValueError:
        return default


def _row_to_account(row: dict[str, str], idx: int) -> Account:
    # Normalize keys to snake_case lower for tolerant matching.
    normalized = {
        (k or "").strip().lower().replace(" ", "_"): (v if v is not None else "")
        for k, v in row.items()
    }

    def get(*keys: str, default: str = "") -> str:
        for k in keys:
            v = normalized.get(k)
            if v not in (None, ""):
                return v
        return default

    account_id = get("account_id", "id", "loan_id") or f"row_{idx}"

    return Account(
        account_id=account_id,
        original_creditor=get("original_creditor", "originator") or None,
        current_creditor=get("current_creditor", "seller") or None,
        debtor_name=get("debtor_name", "consumer_name", "name") or None,
        debtor_state=(get("debtor_state", "state") or "").upper() or None,
        debtor_address=get("debtor_address", "address") or None,
        debtor_phone=get("debtor_phone", "phone") or None,
        debtor_email=get("debtor_email", "email") or None,
        account_type=AccountType.parse(get("account_type", "product_type", "type")),
        original_balance=_parse_float(get("original_balance", "orig_balance")),
        current_balance=_parse_float(
            get("current_balance", "balance", "face_value", "outstanding_balance")
        ),
        charge_off_balance=_parse_float(get("charge_off_balance", "co_balance")),
        open_date=_parse_date(get("open_date")),
        charge_off_date=_parse_date(get("charge_off_date", "co_date")),
        last_payment_date=_parse_date(get("last_payment_date", "lpd")),
        last_payment_amount=_parse_float(get("last_payment_amount", "lpa")),
        date_of_first_delinquency=_parse_date(
            get("date_of_first_delinquency", "dofd", "first_delinquency")
        ),
        has_signed_agreement=_parse_bool(get("has_signed_agreement", "signed_agreement")),
        has_statements=_parse_bool(get("has_statements", "statements")),
        has_chain_of_title=_parse_bool(get("has_chain_of_title", "chain_of_title")),
        times_sold=_parse_int(get("times_sold", "sale_count"), default=1),
        bankruptcy_flag=_parse_bool(get("bankruptcy_flag", "bankruptcy")),
        deceased_flag=_parse_bool(get("deceased_flag", "deceased")),
        cease_desist_flag=_parse_bool(get("cease_desist_flag", "cease_desist")),
        litigation_flag=_parse_bool(get("litigation_flag", "litigation")),
        fraud_dispute_flag=_parse_bool(get("fraud_dispute_flag", "fraud_dispute", "fraud")),
        raw=dict(row),
    )


def load_tape(path: str | Path) -> Portfolio:
    """Load a charged-off debt tape from a CSV file.

    The loader is tolerant: column names are normalized (snake_case, lowercase),
    several aliases are accepted, and missing values default to empty/false/0.
    """
    p = Path(path)
    with p.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        accounts = [_row_to_account(row, i) for i, row in enumerate(reader)]
    return Portfolio(accounts=accounts)


def load_tape_from_rows(rows: Iterable[dict[str, str]]) -> Portfolio:
    accounts = [_row_to_account(row, i) for i, row in enumerate(rows)]
    return Portfolio(accounts=accounts)
