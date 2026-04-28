from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from debt_portfolio_analyzer.models import FlagLevel, ScoredAccount
from debt_portfolio_analyzer.roi import RoiEstimate, estimate_roi


def _bucket(score: int) -> str:
    if score == 0:
        return "0 (hard-stop)"
    if score < 20:
        return "1-19"
    if score < 40:
        return "20-39"
    if score < 60:
        return "40-59"
    if score < 80:
        return "60-79"
    return "80-100"


_BUCKET_ORDER = ("0 (hard-stop)", "1-19", "20-39", "40-59", "60-79", "80-100")


def build_report(
    scored: Iterable[ScoredAccount],
    purchase_price: float,
    *,
    top_n: int = 10,
) -> dict:
    scored = list(scored)
    n = len(scored)
    face_value = sum(s.account.current_balance for s in scored)
    hard_stops = [s for s in scored if s.is_hard_stop]
    warnings = [
        s for s in scored
        if not s.is_hard_stop
        and any(f.level == FlagLevel.WARNING for f in s.flags)
    ]

    distribution: dict[str, int] = {b: 0 for b in _BUCKET_ORDER}
    for s in scored:
        distribution[_bucket(s.score)] += 1

    flag_counts: dict[str, int] = {}
    for s in scored:
        for f in s.flags:
            flag_counts[f.code] = flag_counts.get(f.code, 0) + 1

    roi = estimate_roi(scored, purchase_price=purchase_price)

    top = sorted(scored, key=lambda s: s.score, reverse=True)[:top_n]

    return {
        "summary": {
            "accounts": n,
            "face_value": face_value,
            "hard_stop_accounts": len(hard_stops),
            "hard_stop_face_value": sum(s.account.current_balance for s in hard_stops),
            "warning_accounts": len(warnings),
        },
        "score_distribution": distribution,
        "flag_counts": flag_counts,
        "roi": roi.as_dict(),
        "top_accounts": [
            {
                "account_id": s.account.account_id,
                "score": s.score,
                "current_balance": s.account.current_balance,
                "expected_recovery_rate": s.expected_recovery_rate,
                "expected_recovery": s.expected_recovery,
                "flags": [f.code for f in s.flags],
            }
            for s in top
        ],
    }


def _money(x: float) -> str:
    return f"${x:,.2f}"


def _pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def render_report(report: dict) -> str:
    s = report["summary"]
    roi = report["roi"]
    lines: list[str] = []
    lines.append("=" * 64)
    lines.append("DEBT PORTFOLIO ANALYSIS")
    lines.append("=" * 64)
    lines.append("")
    lines.append("Disclaimer: analysis only. This tool does not contact consumers.")
    lines.append("Output is not legal advice; verify SOL and licensing per state.")
    lines.append("")
    lines.append("-- Summary --")
    lines.append(f"  Accounts:              {s['accounts']:,}")
    lines.append(f"  Face value:            {_money(s['face_value'])}")
    lines.append(f"  Hard-stop accounts:    {s['hard_stop_accounts']:,} "
                 f"({_money(s['hard_stop_face_value'])})")
    lines.append(f"  Warning accounts:      {s['warning_accounts']:,}")
    lines.append("")

    lines.append("-- Score distribution --")
    for bucket in _BUCKET_ORDER:
        count = report["score_distribution"].get(bucket, 0)
        bar = "#" * min(40, count)
        lines.append(f"  {bucket:<14} {count:>5}  {bar}")
    lines.append("")

    lines.append("-- Compliance flags --")
    if not report["flag_counts"]:
        lines.append("  (none)")
    else:
        for code, count in sorted(
            report["flag_counts"].items(), key=lambda kv: (-kv[1], kv[0])
        ):
            lines.append(f"  {code:<28} {count:>5}")
    lines.append("")

    lines.append("-- ROI estimate --")
    lines.append(f"  Purchase price:                 {_money(roi['purchase_price'])}")
    lines.append(f"  Collectable face value:         {_money(roi['collectable_face_value'])}")
    lines.append(f"  Expected gross recovery (low):  {_money(roi['expected_gross_recovery_low'])}")
    lines.append(f"  Expected gross recovery (mid):  {_money(roi['expected_gross_recovery_mid'])}")
    lines.append(f"  Expected gross recovery (high): {_money(roi['expected_gross_recovery_high'])}")
    lines.append(f"  Total costs (mid):              {_money(roi['total_costs_mid'])}")
    lines.append(f"  Expected net (mid):             {_money(roi['expected_net_mid'])}")
    lines.append(f"  ROI (mid):                      {_pct(roi['roi_mid'])}")
    lines.append(f"  Breakeven price:                {_money(roi['breakeven_purchase_price'])}")
    lines.append(f"  Recommended max price:          {_money(roi['recommended_max_purchase_price'])}")
    lines.append("")

    lines.append("-- Top collectable accounts --")
    if not report["top_accounts"]:
        lines.append("  (none)")
    else:
        lines.append(f"  {'account_id':<20}{'score':>6}{'balance':>14}{'rate':>8}{'recovery':>14}  flags")
        for row in report["top_accounts"]:
            lines.append(
                f"  {str(row['account_id'])[:18]:<20}"
                f"{row['score']:>6}"
                f"{_money(row['current_balance']):>14}"
                f"{_pct(row['expected_recovery_rate']):>8}"
                f"{_money(row['expected_recovery']):>14}"
                f"  {','.join(row['flags']) or '-'}"
            )
    lines.append("")
    return "\n".join(lines)
