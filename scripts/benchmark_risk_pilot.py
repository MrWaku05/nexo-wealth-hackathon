#!/usr/bin/env python3
"""Piloto reproducible: exposición sintética al benchmark vs. 100% benchmark.

NO es un portafolio de valores invertibles, no demuestra alfa y NO sustituye
al Backtest Engine licenciado ni al análisis de factores.

Ejemplo:
python scripts/benchmark_risk_pilot.py --zip 'KN_US_Equity_Core(1).zip' \
  --output research/benchmark_risk_pilot_LOCAL.json
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

LOOKBACK = 60
TARGET_VOL = 0.15
MIN_EXPOSURE = 0.60
MAX_EXPOSURE = 1.0
ONE_WAY_COST = 0.0005
OOS_START = date(2018, 1, 1)


def read_benchmark(path: Path) -> list[tuple[date, float]]:
    with ZipFile(path) as source:
        names = [n for n in source.namelist() if n.endswith('_Returns_Daily.csv')]
        if len(names) != 1:
            raise ValueError('Debe existir exactamente un archivo Returns_Daily.csv')
        with source.open(names[0]) as binary:
            with io.TextIOWrapper(binary, encoding='utf-8-sig') as decoded:
                rows = list(csv.DictReader(decoded))
    series = [(date.fromisoformat(x['m_date']), float(x['return'])) for x in rows]
    if len(series) < LOOKBACK + 2:
        raise ValueError('No hay suficientes observaciones')
    if any(not math.isfinite(r) or r <= -1 for _, r in series):
        raise ValueError('Rendimientos inválidos')
    if any(series[i][0] <= series[i - 1][0] for i in range(1, len(series))):
        raise ValueError('Fechas duplicadas o no ordenadas')
    return series


def target_weight(past_returns: list[float]) -> float:
    """Calcula peso usando EXCLUSIVAMENTE el historial ya observado."""
    if len(past_returns) != LOOKBACK:
        raise ValueError('El histórico debe tener exactamente 60 rendimientos')
    sigma = statistics.stdev(past_returns) * math.sqrt(252)
    if sigma <= 1e-12:
        return MAX_EXPOSURE
    return max(MIN_EXPOSURE, min(MAX_EXPOSURE, TARGET_VOL / sigma))


def stats(dates: list[date], returns: list[float]) -> dict:
    if not dates or len(dates) != len(returns):
        raise ValueError('La serie estadística está vacía o desalineada')
    wealth = 1.0
    peak = 1.0
    max_dd = 0.0
    for r in returns:
        wealth *= 1 + r
        peak = max(peak, wealth)
        max_dd = min(max_dd, wealth / peak - 1)
    years = (dates[-1] - dates[0]).days / 365.25
    mean = statistics.mean(returns)
    vol = statistics.stdev(returns) * math.sqrt(252) if len(returns) > 1 else 0.0
    return {
        'start': dates[0].isoformat(), 'end': dates[-1].isoformat(),
        'days': len(returns), 'total_return': wealth - 1,
        'cagr': wealth ** (1 / years) - 1 if years > 0 else None,
        'annual_volatility': vol, 'max_drawdown': max_dd,
        'sharpe_zero_riskfree': mean * 252 / vol if vol else None,
    }


def simulate(series: list[tuple[date, float]]) -> dict:
    """Rebalanceo al inicio de cada mes, usando retornos hasta el cierre previo."""
    if len(series) <= LOOKBACK:
        raise ValueError('La serie es insuficiente')
    dates = [d for d, _ in series]
    ret = [r for _, r in series]
    wealth = 1.0
    wealth_index = 1.0
    weight_end_prev_day = 0.0
    last_rebalance_month = None
    daily_strategy = []
    daily_index = []
    daily_dates = []
    rebalance_events = []
    total_cost_fraction = 0.0
    for i in range(LOOKBACK, len(series)):
        d, r = series[i]
        month = (d.year, d.month)
        weight = weight_end_prev_day
        fee_fraction = 0.0
        if last_rebalance_month != month:
            # La operación al comienzo del día t ve únicamente r[t-60:t].
            weight = target_weight(ret[i - LOOKBACK:i])
            fee_fraction = abs(weight - weight_end_prev_day) * ONE_WAY_COST
            total_cost_fraction += fee_fraction
            rebalance_events.append({
                'date': d.isoformat(), 'target_exposure': round(weight, 8),
                'observed_volatility': round(statistics.stdev(ret[i - LOOKBACK:i]) * math.sqrt(252), 8),
                'fee_fraction': round(fee_fraction, 10),
            })
            last_rebalance_month = month
        # Simulación auto-financiada. El efectivo se supone 0% y no recibe intereses.
        day_return = weight * r - fee_fraction
        wealth *= 1 + day_return
        wealth_index *= 1 + r
        if 1 + day_return <= 0:
            raise ValueError('Capital no positivo; revisar datos y modelo')
        weight_end_prev_day = weight * (1 + r) / (1 + day_return)
        daily_strategy.append(day_return)
        daily_index.append(r)
        daily_dates.append(d)
    out = {
        'status': 'research_pilot_not_investable',
        'name': 'Exposición sintética a KN US Equity Core con volatilidad móvil',
        'disclaimer': 'NO es una estrategia de acciones/ETF invertible; usa rentabilidades del benchmark para ensayar un motor de riesgo. No es un backtest oficial de Investment Lab ni atribución de factores.',
        'source': 'KN_US_Equity_Core_Returns_Daily.csv',
        'assumptions': {
            'lookback_trading_days': LOOKBACK,
            'annual_target_volatility': TARGET_VOL,
            'min_exposure': MIN_EXPOSURE, 'max_exposure': MAX_EXPOSURE,
            'rebalance': 'primer dia habil de cada mes, antes del retorno del dia',
            'signal_lag': '60 retornos terminados al cierre del dia anterior',
            'one_way_cost_bps_on_turnover': ONE_WAY_COST * 10000,
            'cash_return': 0.0, 'riskfree_sharpe': 0.0,
            'currency': 'USD (retornos nominales del indice)',
            'investability': 'Indice no directamente negociable',
        },
        'full': {'benchmark': stats(daily_dates, daily_index), 'pilot': stats(daily_dates, daily_strategy)},
        'oos_from_2018': {},
        'rebalance_count': len(rebalance_events),
        'cumulative_cost_fraction_approx': total_cost_fraction,
        'sample_rebalances': rebalance_events[:3] + rebalance_events[-3:],
    }
    oos_idx = next((j for j, d in enumerate(daily_dates) if d >= OOS_START), None)
    if oos_idx is not None:
        out['oos_from_2018'] = {
            'benchmark': stats(daily_dates[oos_idx:], daily_index[oos_idx:]),
            'pilot': stats(daily_dates[oos_idx:], daily_strategy[oos_idx:]),
            'caveat': 'Partición temporal descriptiva; NO es fuera de muestra validado si el diseño fue influido por resultados previos.',
        }
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip', dest='zip_path', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('research/benchmark_risk_pilot_LOCAL.json'))
    args = parser.parse_args()
    output = simulate(read_benchmark(args.zip_path))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Piloto sintetico calculado; NO es estrategia invertible ni backtest oficial.')
    print('Reporte local:', args.output)
    for name in ('benchmark', 'pilot'):
        s = output['full'][name]
        print(name, 'CAGR', f"{s['cagr']:.2%}", 'volatilidad', f"{s['annual_volatility']:.2%}", 'max_dd', f"{s['max_drawdown']:.2%}")


if __name__ == '__main__':
    main()
