from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from debt_portfolio_analyzer.loader import load_tape
from debt_portfolio_analyzer.report import build_report, render_report
from debt_portfolio_analyzer.scoring import score_portfolio


def _cmd_analyze(args: argparse.Namespace) -> int:
    portfolio = load_tape(args.tape)
    scored = score_portfolio(portfolio)
    report = build_report(scored, purchase_price=args.price, top_n=args.top)

    if args.format == "json":
        sys.stdout.write(json.dumps(report, indent=2, default=str))
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render_report(report))

    if args.scored_csv:
        _write_scored_csv(scored, args.scored_csv)
    return 0


def _cmd_score(args: argparse.Namespace) -> int:
    portfolio = load_tape(args.tape)
    scored = score_portfolio(portfolio)
    _write_scored_csv(scored, args.output)
    return 0


def _write_scored_csv(scored, output_path: str | Path) -> None:
    fieldnames = [
        "account_id",
        "score",
        "expected_recovery_rate",
        "expected_recovery",
        "current_balance",
        "is_hard_stop",
        "flags",
    ]
    with Path(output_path).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in scored:
            writer.writerow({
                "account_id": s.account.account_id,
                "score": s.score,
                "expected_recovery_rate": f"{s.expected_recovery_rate:.4f}",
                "expected_recovery": f"{s.expected_recovery:.2f}",
                "current_balance": f"{s.account.current_balance:.2f}",
                "is_hard_stop": s.is_hard_stop,
                "flags": "|".join(f.code for f in s.flags),
            })


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="dpa",
        description=(
            "Debt portfolio analyzer. Scores collectability and surfaces "
            "compliance flags from a charged-off debt tape (CSV). Analysis "
            "only — does not contact consumers."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser("analyze", help="Score a tape and print a portfolio report.")
    analyze.add_argument("tape", help="Path to the debt tape CSV.")
    analyze.add_argument(
        "--price", type=float, default=0.0,
        help="Proposed purchase price for ROI estimation. Default 0.",
    )
    analyze.add_argument(
        "--format", choices=("text", "json"), default="text",
        help="Output format. Default text.",
    )
    analyze.add_argument("--top", type=int, default=10, help="Top-N accounts to list.")
    analyze.add_argument(
        "--scored-csv", default=None,
        help="Optional path to also write a per-account scored CSV.",
    )
    analyze.set_defaults(func=_cmd_analyze)

    score = sub.add_parser("score", help="Score a tape and write per-account CSV.")
    score.add_argument("tape", help="Path to the debt tape CSV.")
    score.add_argument("output", help="Path to write the scored CSV.")
    score.set_defaults(func=_cmd_score)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
