from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from debt_portfolio_analyzer.models import ScoredAccount


# Default cost assumptions, expressed as fractions of gross recoveries.
DEFAULT_AGENCY_FEE = 0.30          # contingency fee paid to a licensed agency
DEFAULT_OPS_OVERHEAD = 0.05        # data, skip-trace, payment processing, etc.
DEFAULT_LEGAL_RESERVE = 0.03       # compliance counsel, dispute handling


@dataclass
class RoiEstimate:
    purchase_price: float
    face_value: float
    collectable_face_value: float          # excludes hard-stop accounts
    expected_gross_recovery_low: float
    expected_gross_recovery_mid: float
    expected_gross_recovery_high: float
    total_costs_mid: float
    expected_net_mid: float
    roi_mid: float                          # net / purchase_price
    breakeven_purchase_price: float         # max price for ROI >= 0 (mid case)
    recommended_max_purchase_price: float   # mid case net of cushion

    def as_dict(self) -> dict:
        return {
            "purchase_price": self.purchase_price,
            "face_value": self.face_value,
            "collectable_face_value": self.collectable_face_value,
            "expected_gross_recovery_low": self.expected_gross_recovery_low,
            "expected_gross_recovery_mid": self.expected_gross_recovery_mid,
            "expected_gross_recovery_high": self.expected_gross_recovery_high,
            "total_costs_mid": self.total_costs_mid,
            "expected_net_mid": self.expected_net_mid,
            "roi_mid": self.roi_mid,
            "breakeven_purchase_price": self.breakeven_purchase_price,
            "recommended_max_purchase_price": self.recommended_max_purchase_price,
        }


def estimate_roi(
    scored: Iterable[ScoredAccount],
    purchase_price: float,
    *,
    agency_fee: float = DEFAULT_AGENCY_FEE,
    ops_overhead: float = DEFAULT_OPS_OVERHEAD,
    legal_reserve: float = DEFAULT_LEGAL_RESERVE,
    low_band: float = 0.6,
    high_band: float = 1.4,
    target_roi: float = 0.25,
) -> RoiEstimate:
    """Estimate gross/net recovery and ROI for a scored portfolio.

    Costs are applied as fractions of *gross recoveries* (the standard model
    for contingency-fee servicing). Hard-stop accounts are excluded entirely.

    The low/high bands wrap the mid recovery estimate to express modeling
    uncertainty.
    """
    scored = list(scored)
    face_value = sum(s.account.current_balance for s in scored)
    collectable = [s for s in scored if not s.is_hard_stop]
    collectable_face = sum(s.account.current_balance for s in collectable)
    mid = sum(s.expected_recovery for s in collectable)

    cost_rate = agency_fee + ops_overhead + legal_reserve
    total_costs_mid = mid * cost_rate
    net_mid = mid - total_costs_mid - purchase_price

    roi_mid = (net_mid / purchase_price) if purchase_price > 0 else 0.0

    # Breakeven: price at which mid net == 0.
    breakeven = mid * (1 - cost_rate)
    # Recommended max: discount breakeven to hit target ROI.
    recommended_max = breakeven / (1 + target_roi) if (1 + target_roi) > 0 else 0.0

    return RoiEstimate(
        purchase_price=purchase_price,
        face_value=face_value,
        collectable_face_value=collectable_face,
        expected_gross_recovery_low=mid * low_band,
        expected_gross_recovery_mid=mid,
        expected_gross_recovery_high=mid * high_band,
        total_costs_mid=total_costs_mid,
        expected_net_mid=net_mid,
        roi_mid=roi_mid,
        breakeven_purchase_price=breakeven,
        recommended_max_purchase_price=recommended_max,
    )
