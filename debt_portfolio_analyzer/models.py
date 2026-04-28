from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class AccountType(str, Enum):
    CREDIT_CARD = "credit_card"
    MEDICAL = "medical"
    AUTO = "auto"
    PERSONAL_LOAN = "personal_loan"
    UTILITY = "utility"
    TELECOM = "telecom"
    RETAIL = "retail"
    STUDENT = "student"
    OTHER = "other"

    @classmethod
    def parse(cls, value: str | None) -> "AccountType":
        if not value:
            return cls.OTHER
        key = value.strip().lower().replace("-", "_").replace(" ", "_")
        try:
            return cls(key)
        except ValueError:
            return cls.OTHER


class FlagLevel(str, Enum):
    HARD_STOP = "hard_stop"   # do not collect
    WARNING = "warning"       # special handling required
    INFO = "info"             # informational


@dataclass(frozen=True)
class Flag:
    code: str
    level: FlagLevel
    message: str


@dataclass
class Account:
    """A single charged-off account from a debt tape.

    Required fields are minimal; the rest are best-effort. Missing data is
    itself a signal that drives compliance flags and reduces collectability
    score.
    """

    account_id: str
    original_creditor: str | None = None
    current_creditor: str | None = None
    debtor_name: str | None = None
    debtor_state: str | None = None        # 2-letter US state code
    debtor_address: str | None = None
    debtor_phone: str | None = None
    debtor_email: str | None = None

    account_type: AccountType = AccountType.OTHER
    original_balance: float = 0.0
    current_balance: float = 0.0
    charge_off_balance: float = 0.0

    open_date: date | None = None
    charge_off_date: date | None = None
    last_payment_date: date | None = None
    last_payment_amount: float = 0.0
    date_of_first_delinquency: date | None = None

    has_signed_agreement: bool = False
    has_statements: bool = False
    has_chain_of_title: bool = False
    times_sold: int = 1

    bankruptcy_flag: bool = False
    deceased_flag: bool = False
    cease_desist_flag: bool = False
    litigation_flag: bool = False
    fraud_dispute_flag: bool = False

    raw: dict = field(default_factory=dict)

    @property
    def has_valid_contact(self) -> bool:
        return bool(
            (self.debtor_address and self.debtor_state)
            or self.debtor_phone
            or self.debtor_email
        )

    @property
    def has_full_docs(self) -> bool:
        return self.has_signed_agreement and self.has_statements and self.has_chain_of_title


@dataclass
class ScoredAccount:
    account: Account
    score: int                  # 0-100 collectability
    expected_recovery_rate: float  # 0..1 of current_balance
    flags: list[Flag] = field(default_factory=list)

    @property
    def is_hard_stop(self) -> bool:
        return any(f.level == FlagLevel.HARD_STOP for f in self.flags)

    @property
    def expected_recovery(self) -> float:
        if self.is_hard_stop:
            return 0.0
        return self.account.current_balance * self.expected_recovery_rate


@dataclass
class Portfolio:
    accounts: list[Account]

    @property
    def face_value(self) -> float:
        return sum(a.current_balance for a in self.accounts)

    @property
    def size(self) -> int:
        return len(self.accounts)
