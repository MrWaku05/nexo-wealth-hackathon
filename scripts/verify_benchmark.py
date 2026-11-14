#!/usr/bin/env python3
"""Valida los metadatos publicados del benchmark; opcionalmente recalcula desde el ZIP fuente.

No modifica archivos, no llama a APIs ni utiliza claves.

Ejemplos:
  python scripts/verify_benchmark.py --summary benchmark_summary.json
  python scripts/verify_benchmark.py --summary benchmark_summary.json --zip "C:/data/KN_US_Equity_Core.zip"
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import statistics
from datetime import date
from pathlib import Path
from zipfile import ZipFile


def check_summary(obj: dict) -> None:
    assert obj["benchmark"] == "KN US Equity Core"
    assert obj["return_type"].startswith("provided daily return")
    for key in ("full", "since_2000", "since_2020", "in_2026"):
        s = obj[key]
        assert date.fromisoformat(s["start"]) <= date.fromisoformat(s["end"])
        assert 0 < s["n"] <= s["days"]
        assert s["total_return"] > -1
        assert 0 <= s["volatility"] < 100
        assert -1 <= s["max_drawdown"] <= 0
        assert abs(s["final_index"] - 100 * (1 + s["total_return"])) < 1e-5
    assert obj["full"]["end"] == obj["constituents_latest"]["date"]
    assert obj["constituents_latest"]["member_count"] >= 1
    assert abs(obj["constituents_latest"]["weight_sum"] - 1) < 0.01
    assert len(obj["curve_monthly"]) >= 24
    last_month = ""
    for point in obj["curve_monthly"]:
        assert point["month"] > last_month
        assert point["index"] > 0
        last_month = point["month"]


def from_zip(path: Path) -> dict:
    with ZipFile(path) as z:
        names = [n for n in z.namelist() if n.endswith("_Returns_Daily.csv")]
        assert len(names) == 1, f"Se esperaba un solo Returns_Daily, encontrados: {len(names)}"
        with z.open(names[0]) as binary, io.TextIOWrapper(binary, encoding="utf-8-sig") as source:
            data = list(csv.DictReader(source))
    assert data and all("m_date" in r and "return" in r for r in data)
    dt = [date.fromisoformat(row["m_date"]) for row in data]
    returns = [float(row["return"]) for row in data]
    assert all(-1 < r and math.isfinite(r) for r in returns)
    assert all(dt[i] > dt[i - 1] for i in range(1, len(dt)))
    growth = math.exp(math.fsum(math.log1p(r) for r in returns))
    peak = 1.0
    wealth = 1.0
    drawdown = 0.0
    worst_date = None
    for t, r in zip(dt, returns):
        wealth *= 1 + r
        peak = max(peak, wealth)
        d = wealth / peak - 1
        if d < drawdown:
            drawdown, worst_date = d, t.isoformat()
    return {
        "start": dt[0].isoformat(), "end": dt[-1].isoformat(), "n": len(dt),
        "total_return": growth - 1,
        "cagr": growth ** (365.25 / (dt[-1] - dt[0]).days) - 1,
        "volatility": statistics.stdev(returns) * math.sqrt(252),
        "max_drawdown": drawdown,
        "drawdown_day": worst_date,
    }


def validate_source(given: dict, actual: dict) -> None:
    for key in ("start", "end", "n", "drawdown_day"):
        assert given[key] == actual[key], f"{key}: summary={given[key]!r}; fuente={actual[key]!r}"
    for key in ("total_return", "cagr", "volatility", "max_drawdown"):
        assert math.isclose(given[key], actual[key], rel_tol=0, abs_tol=1e-7), (
            f"{key}: summary={given[key]:.8f}; fuente={actual[key]:.8f}"
        )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--summary", type=Path, default=Path("benchmark_summary.json"))
    p.add_argument("--zip", type=Path, default=None, help="ZIP del equipo (nunca subirlo a Git)")
    a = p.parse_args()
    obj = json.loads(a.summary.read_text(encoding="utf-8"))
    check_summary(obj)
    print("PASS resumen del KN US Equity Core: formato y coherencia interna")
    if a.zip:
        validate_source(obj["full"], from_zip(a.zip))
        print("PASS: métricas históricas del resumen reproducidas desde CSV fuente")
    else:
        print("NOTA: sin --zip no se verificó contra el CSV original")


if __name__ == "__main__":
    main()
