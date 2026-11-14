#!/usr/bin/env python3
"""Descarga precios diarios ajustados con FMP en CSV locales privados.

Solo usa FMP_API_KEY del entorno; NUNCA imprime secretos, URLs autenticadas ni respuestas crudas.
El endpoint puede requerir un plan específico de FMP.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
from datetime import date
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from sector_etf_backtest import SECTOR_ETFS

BASE_URL = "https://financialmodelingprep.com/stable/historical-price-eod/dividend-adjusted"


def normalize_rows(records: object, symbol: str) -> list[tuple[str, float]]:
    if not isinstance(records, list) or not records:
        raise ValueError(f"{symbol}: respuesta vacía o no disponible para el plan de API")
    out = {}
    for record in records:
        if not isinstance(record, dict) or "date" not in record or "adjClose" not in record:
            raise ValueError(f"{symbol}: no hay columnas 'date' y 'adjClose' en respuesta")
        d = date.fromisoformat(record["date"]).isoformat()
        adj = float(record["adjClose"])
        if not math.isfinite(adj) or adj <= 0:
            raise ValueError(f"{symbol}: precio inválido ({d})")
        if d in out:
            raise ValueError(f"{symbol}: fecha duplicada {d}")
        out[d] = adj
    return sorted(out.items())


def fetch_symbol(symbol: str, key: str, start: date, end: date) -> list[tuple[str, float]]:
    # No escribir a log esta URL: contiene apikey.
    query = urlencode({"symbol": symbol, "from": start.isoformat(), "to": end.isoformat(), "apikey": key})
    request = Request(f"{BASE_URL}?{query}", headers={"User-Agent": "NexoResearch/0.1"})
    try:
        with urlopen(request, timeout=30) as response:
            records = json.load(response)
    except (HTTPError, URLError, TimeoutError) as exc:
        # Los objetos HTTPError pueden contener la URL, por eso no mostramos str(exc).
        raise RuntimeError(f"FMP no pudo responder para {symbol}: {type(exc).__name__}") from None
    except json.JSONDecodeError:
        raise RuntimeError(f"FMP devolvió datos no JSON para {symbol}") from None
    return normalize_rows(records, symbol)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--symbols", nargs="+", default=list(SECTOR_ETFS))
    p.add_argument("--start", type=date.fromisoformat, default=date(2017, 1, 1))
    p.add_argument("--end", type=date.fromisoformat, default=date(2026, 11, 6))
    p.add_argument("--dest", type=Path, default=Path("data/private/prices"))
    args = p.parse_args()
    if args.start >= args.end:
        p.error("Fecha inicial debe ser anterior a final")
    key = os.environ.get("FMP_API_KEY", "").strip()
    if not key:
        p.error("No se encontró FMP_API_KEY en las variables de entorno (no escribas la clave aquí)")
    args.dest.mkdir(parents=True, exist_ok=True)
    for symbol in args.symbols:
        if symbol not in SECTOR_ETFS:
            p.error(f"ETF no permitido en universo predefinido: {symbol}")
        rows = fetch_symbol(symbol, key, args.start, args.end)
        file = args.dest / f"{symbol}.csv"
        with file.open("w", encoding="utf-8", newline="") as output:
            writer = csv.writer(output)
            writer.writerow(["date", "adjClose"])
            writer.writerows(rows)
        print(f"{symbol}: {len(rows)} fechas; guardado en carpeta privada")
    print("Descarga concluida. Verifica cobertura de fechas antes del backtest")


if __name__ == "__main__":
    main()
