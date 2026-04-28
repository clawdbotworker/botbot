import csv
import io
import json
import os
from contextlib import redirect_stdout
from pathlib import Path

from debt_portfolio_analyzer.cli import main


SAMPLE = Path(__file__).resolve().parent.parent / "examples" / "sample_tape.csv"


def test_analyze_text_smoke():
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(["analyze", str(SAMPLE), "--price", "5000"])
    assert rc == 0
    out = buf.getvalue()
    assert "DEBT PORTFOLIO ANALYSIS" in out
    assert "Score distribution" in out
    assert "ROI estimate" in out


def test_analyze_json_smoke():
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(["analyze", str(SAMPLE), "--price", "5000", "--format", "json"])
    assert rc == 0
    data = json.loads(buf.getvalue())
    assert data["summary"]["accounts"] == 20
    assert "roi" in data
    assert "score_distribution" in data


def test_score_writes_csv(tmp_path):
    out_path = tmp_path / "scored.csv"
    rc = main(["score", str(SAMPLE), str(out_path)])
    assert rc == 0
    with out_path.open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 20
    assert {"account_id", "score", "expected_recovery", "flags"}.issubset(rows[0].keys())
