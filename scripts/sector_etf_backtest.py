#!/usr/bin/env python3
"""E1: backtest sencillo y reproducible de rotación de ETFs sectoriales.

Usa cierres históricos ajustados por dividendos y el benchmark KN US Equity Core.
No implementa el Backtest Engine licenciado de KaxaNuk; el método es independiente.
No requiere pandas, Internet ni clave FMP para ejecutarse sobre CSV locales.
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

SECTOR_ETFS = ("XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY")
TREND_DAYS = 200
MOMENTUM_DAYS = 126
SKIP_RECENT_DAYS = 21
TOP_N = 5
CAP_PER_ETF = 0.20  # Tope conservador; el reto especifica 20% por ACCIÓN individual.
ONE_WAY_BPS = 10.0


def read_benchmark(core_zip: Path) -> list[tuple[date, float]]:
    """La serie oficial de rendimientos diarios, sin reconstrucción artificial."""
    with ZipFile(core_zip) as archive:
        files = [name for name in archive.namelist() if name.endswith("_Returns_Daily.csv")]
        if len(files) != 1:
            raise ValueError("Se esperaba un único archivo _Returns_Daily.csv en el ZIP Core")
        with archive.open(files[0]) as stream:
            reader = csv.DictReader(io.TextIOWrapper(stream, encoding="utf-8-sig"))
            rows = [(date.fromisoformat(row["m_date"]), float(row["return"])) for row in reader]
    if len(rows) < TREND_DAYS + 2:
        raise ValueError("Benchmark demasiado corto")
    if any(not math.isfinite(value) or value <= -1.0 for _, value in rows):
        raise ValueError("Benchmark con rendimientos no válidos")
    if any(rows[i][0] <= rows[i - 1][0] for i in range(1, len(rows))):
        raise ValueError("Benchmark: fechas repetidas/desordenadas")
    return rows


def load_adjusted_prices(directory: Path, symbols: tuple[str, ...]) -> dict[str, dict[date, float]]:
    """Solo acepta adjClose: no confundir precios sin dividendos con retornos totales."""
    data = {}
    for symbol in symbols:
        path = directory / f"{symbol}.csv"
        if not path.is_file():
            raise FileNotFoundError(f"Falta CSV de {symbol} en {directory}")
        with path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or not {"date", "adjClose"}.issubset(reader.fieldnames):
                raise ValueError(f"{symbol}: columnas requeridas 'date' y 'adjClose'")
            prices = {}
            for row in reader:
                d = date.fromisoformat(row["date"])
                p = float(row["adjClose"])
                if not math.isfinite(p) or p <= 0:
                    raise ValueError(f"{symbol}: precio inválido en {d.isoformat()}")
                if d in prices:
                    raise ValueError(f"{symbol}: fecha duplicada {d.isoformat()}")
                prices[d] = p
            if len(prices) < TREND_DAYS + 2:
                raise ValueError(f"{symbol}: menos de {TREND_DAYS + 2} registros")
        data[symbol] = prices
    return data


def rank_at_close(previous_closes: dict[str, list[float]]) -> dict[str, float]:
    """Usa señales ya conocidas al cierre t-1; se ejecuta al cierre t.

    Momento 126-21: P[t-22] / P[t-127] - 1, con índices negativos
    relativos a una lista finalizada el día anterior.
    """
    qualifying = []
    for ticker, history in previous_closes.items():
        if len(history) < TREND_DAYS:
            raise ValueError("Faltan observaciones para SMA200")
        last_price = history[-1]
        ma200 = statistics.fmean(history[-TREND_DAYS:])
        momentum = history[-(SKIP_RECENT_DAYS + 1)] / history[-(MOMENTUM_DAYS + 1)] - 1.0
        if last_price > ma200 and momentum > 0:
            qualifying.append((momentum, ticker))
    qualifying.sort(key=lambda item: (-item[0], item[1]))
    # Mantener el resto en efectivo, no repartir más del 20% por ETF.
    return {ticker: CAP_PER_ETF for _, ticker in qualifying[:TOP_N]}


def statistics_for(dates: list[date], returns: list[float]) -> dict[str, float | int | str | None]:
    if not dates or len(dates) != len(returns):
        raise ValueError("Rendimientos y fechas deben tener igual tamaño y no estar vacíos")
    equity = peak = 1.0
    worst_drawdown = 0.0
    for r in returns:
        equity *= 1.0 + r
        peak = max(peak, equity)
        worst_drawdown = min(worst_drawdown, equity / peak - 1.0)
    days = (dates[-1] - dates[0]).days
    volatility = statistics.stdev(returns) * math.sqrt(252) if len(returns) >= 2 else 0.0
    annual_mean = statistics.fmean(returns) * 252
    return {
        "start": dates[0].isoformat(), "end": dates[-1].isoformat(), "trading_days": len(dates),
        "total_return": equity - 1.0,
        "cagr": equity ** (365.25 / days) - 1.0 if days > 0 else None,
        "annual_volatility": volatility, "max_drawdown": worst_drawdown,
        "sharpe_riskfree_zero": annual_mean / volatility if volatility > 0 else None,
    }


def run_backtest(
    benchmark: list[tuple[date, float]],
    prices: dict[str, dict[date, float]],
    start: date,
    end: date,
    cost_bps: float = ONE_WAY_BPS,
) -> dict:
    if not 0 <= cost_bps <= 10000:
        raise ValueError("cost_bps inválido")
    if start >= end:
        raise ValueError("Inicio debe preceder al cierre")
    if len(prices) < TOP_N:
        raise ValueError(f"Se requieren al menos {TOP_N} ETFs para el diseño predefinido")

    calendar = [d for d, _ in benchmark if d <= end]
    benchmark_return = dict(benchmark)
    symbols = tuple(sorted(prices))
    initial_candidates = [i for i, d in enumerate(calendar) if d >= start and i >= TREND_DAYS + 1]
    if not initial_candidates:
        raise ValueError("No hay suficientes fechas posteriores a la ventana de indicadores")
    first_i = initial_candidates[0]
    # Hacer fallar la ejecución ante fechas o activos sin dato, sin rellenar silenciosamente.
    for ticker in symbols:
        missing = [d for d in calendar[first_i - TREND_DAYS - 1:] if d not in prices[ticker]]
        if missing:
            raise ValueError(
                f"{ticker}: faltan {len(missing)} sesiones del calendario KN Core; "
                f"primera {missing[0].isoformat()}. Verifica proveedor, splits y fechas."
            )

    # Cada día del portafolio comienza con los pesos obtenidos en el CIERRE previo.
    wealth = 1.0
    target_weights: dict[str, float] = {}
    started = False
    rebalance_month = None
    entries: list[dict] = []
    rebalance_log: list[dict] = []
    turnover_total = 0.0

    for i in range(first_i, len(calendar)):
        today = calendar[i]
        month = (today.year, today.month)
        weights_start = dict(target_weights)
        gross = 0.0
        if started:
            yesterday = calendar[i - 1]
            gross = sum(
                w * (prices[t][today] / prices[t][yesterday] - 1.0)
                for t, w in weights_start.items()
            )
            denom = 1.0 + gross
            if denom <= 0:
                raise ValueError("Capital insuficiente para soportar movimiento diario")
            drifted = {
                t: w * (prices[t][today] / prices[t][yesterday]) / denom
                for t, w in weights_start.items()
            }
        else:
            drifted = {}

        fee_fraction = 0.0
        if month != rebalance_month:
            # En fecha i, las señales llegan hasta i-1; se simula compra al cierre i.
            signal_data = {
                ticker: [prices[ticker][d] for d in calendar[i - TREND_DAYS:i]]
                for ticker in symbols
            }
            new_weights = rank_at_close(signal_data)
            if sum(new_weights.values()) > 1.0 + 1e-10:
                raise AssertionError("Pesos superan 100%")
            if any(w > CAP_PER_ETF + 1e-10 for w in new_weights.values()):
                raise AssertionError("Se incumplió el tope por ETF")
            # Volumen comprado+vendido; solo las posiciones de ETFs generan costo.
            traded_fraction = sum(
                abs(new_weights.get(t, 0.0) - drifted.get(t, 0.0))
                for t in set(new_weights) | set(drifted)
            )
            fee_fraction = traded_fraction * cost_bps / 10000.0
            if fee_fraction >= 1:
                raise ValueError("Costo excede capital")
            turnover_total += traded_fraction
            target_weights = new_weights
            rebalance_log.append({
                "date": today.isoformat(),
                "signal_as_of": calendar[i - 1].isoformat(),
                "execution": "close_today; new weights effective next session",
                "weights": dict(sorted(new_weights.items())),
                "cash_weight": round(1.0 - sum(new_weights.values()), 10),
                "traded_notional_fraction": traded_fraction,
                "cost_fraction": fee_fraction,
            })
            rebalance_month = month
        else:
            target_weights = drifted

        if started:
            # Comisión del rebalanceo al cierre i se descuenta del patrimonio de día i.
            net = (1.0 + gross) * (1.0 - fee_fraction) - 1.0
            wealth *= 1.0 + net
            entries.append({
                "date": today.isoformat(), "strategy_net_return": net,
                "benchmark_return": benchmark_return[today],
                "cash_weight_close": 1.0 - sum(target_weights.values()),
            })
        else:
            # Primer rebalanceo: capital inicial en caja; empieza medición en i+1.
            started = True
            wealth *= 1.0 - fee_fraction
            # El costo inicial se carga explícitamente a la primera rentabilidad reportada.
            opening_fee = fee_fraction

    if not entries:
        raise ValueError("La prueba necesita más de un día tras primer rebalanceo")
    # La tasa diaria del primer día de inversión recoge el costo inicial anterior a esa sesión.
    entries[0]["strategy_net_return"] = (
        (1 + entries[0]["strategy_net_return"]) * (1 - opening_fee) - 1
    )
    dates = [date.fromisoformat(x["date"]) for x in entries]
    strategy_rets = [x["strategy_net_return"] for x in entries]
    core_rets = [x["benchmark_return"] for x in entries]
    return {
        "status": "offline_backtest_with_real_assets_if_price_data_verified",
        "research_only": True,
        "strategy": "Rotación sectorial top-5 con tendencia SMA200 y momentum 126-21",
        "benchmark": "KN US Equity Core (retornos proporcionados)",
        "instruments": list(symbols),
        "methodology": {
            "universe": "ETFs sectoriales predefinidos, no miembros de KN US Equity Core",
            "trend": "P[t-1] > SMA200[t-1]",
            "momentum": "P[t-22] / P[t-127] - 1, observado hasta t-1",
            "selection": "hasta cinco ETFs con momentum positivo y tendencia positiva",
            "weight_per_selected_etf": CAP_PER_ETF,
            "remaining_cash_return": 0.0,
            "rebalance": "primer día bursátil de cada mes al cierre; peso efectivo desde t+1",
            "cost_one_way_bps": cost_bps,
            "data_requirement": "adjusted close por dividendos/splits en USD para cada ETF",
            "key_limit": "20% por ETF, límite conservador adicional al 20% por acción del reto",
        },
        "strategy_metrics_net": statistics_for(dates, strategy_rets),
        "benchmark_metrics": statistics_for(dates, core_rets),
        "active_cagr_difference": statistics_for(dates, strategy_rets)["cagr"] - statistics_for(dates, core_rets)["cagr"],
        "turnover_traded_fraction_total": turnover_total,
        "rebalances": rebalance_log,
        "daily_returns": entries,
        "caveats": [
            "Backtest independiente; no es KaxaNuk Backtest Engine.",
            "Universo fijo de ETFs, sujeto a sesgo de selección retrospectiva; registrar justificación.",
            "Los datos deben cubrir todas las sesiones; los activos delistados fuera del universo no se evalúan.",
            "Costo simplificado por volumen, sin impacto, impuestos ni bid-ask real.",
            "Efectivo al 0%; la estrategia no modela la liquidez ni la apertura de mercado.",
            "El periodo no es fuera de muestra independiente sin pre-registro previo.",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--core-zip", type=Path, required=True)
    p.add_argument("--prices", type=Path, default=Path("data/private/prices"))
    p.add_argument("--start", type=date.fromisoformat, default=date(2019, 1, 1))
    p.add_argument("--end", type=date.fromisoformat, default=date(2026, 11, 6))
    p.add_argument("--cost-bps", type=float, default=ONE_WAY_BPS)
    p.add_argument("--output", type=Path, default=Path("research/sector_etf_result_LOCAL.json"))
    args = p.parse_args()
    report = run_backtest(
        read_benchmark(args.core_zip), load_adjusted_prices(args.prices, SECTOR_ETFS),
        args.start, args.end, args.cost_bps,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    s, b = report["strategy_metrics_net"], report["benchmark_metrics"]
    print(f"Informe local: {args.output}")
    print(f"E1 estrategia CAGR neto: {s['cagr']:.2%} | drawdown: {s['max_drawdown']:.2%}")
    print(f"E0 benchmark CAGR: {b['cagr']:.2%} | drawdown: {b['max_drawdown']:.2%}")
    print("IMPORTANTE: backtest independiente no oficial; validar datos, limitaciones y periodo")


if __name__ == "__main__":
    main()