"""Tests deterministas: precios sintéticos no son evidencia de mercado."""
import csv
import importlib.util
import tempfile
import unittest
import zipfile
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('etf', ROOT / 'scripts' / 'sector_etf_backtest.py')
etf = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(etf)


def synthetic(n=270, shock_day=None):
    dates = [date(2020, 1, 1) + timedelta(days=i) for i in range(n)]
    prices = {}
    for j, t in enumerate(etf.SECTOR_ETFS):
        p = 100.0
        asset = {}
        for i, d in enumerate(dates):
            r = 0.002 + 0.0001 * (len(etf.SECTOR_ETFS) - j)
            if i == shock_day and j == 0:
                r = -0.10
            p *= 1 + r
            asset[d] = p
        prices[t] = asset
    index = [(d, 0.001) for d in dates]
    return index, prices


class SectorBacktestTests(unittest.TestCase):
    def test_cap_and_cash(self):
        _, assets = synthetic()
        history = {t: list(a.values())[:220] for t, a in assets.items()}
        weights = etf.rank_at_close(history)
        self.assertTrue(weights)
        self.assertLessEqual(sum(weights.values()), 1.000000001)
        self.assertTrue(all(w <= 0.20 for w in weights.values()))
        self.assertLessEqual(len(weights), 5)

    def test_next_day_execution_and_signal_lag(self):
        index, prices = synthetic()
        initial = etf.run_backtest(index, prices, date(2020, 8, 1), date(2020, 9, 25))
        shock_index, shock_prices = synthetic(shock_day=255)
        after = etf.run_backtest(shock_index, shock_prices, date(2020, 8, 1), date(2020, 9, 25))
        self.assertEqual(initial['rebalances'][0]['weights'], after['rebalances'][0]['weights'])
        self.assertEqual(initial['rebalances'][0]['signal_as_of'],
                         (date.fromisoformat(initial['rebalances'][0]['date']) - timedelta(days=1)).isoformat())
        self.assertGreater(date.fromisoformat(initial['daily_returns'][0]['date']),
                           date.fromisoformat(initial['rebalances'][0]['date']))

    def test_missing_price_fails_loudly(self):
        index, prices = synthetic()
        removed = index[235][0]
        del prices['XLK'][removed]
        with self.assertRaisesRegex(ValueError, r'XLK: faltan'):
            etf.run_backtest(index, prices, date(2020, 8, 1), date(2020, 9, 25))

    def test_costs_reduce_return(self):
        index, prices = synthetic()
        no_fee = etf.run_backtest(index, prices, date(2020, 8, 1), date(2020, 9, 25), cost_bps=0)
        with_fee = etf.run_backtest(index, prices, date(2020, 8, 1), date(2020, 9, 25), cost_bps=20)
        self.assertLess(with_fee['strategy_metrics_net']['total_return'],
                        no_fee['strategy_metrics_net']['total_return'])

    def test_reproducible_and_benchmark_aligned(self):
        index, prices = synthetic()
        a = etf.run_backtest(index, prices, date(2020, 8, 1), date(2020, 9, 25))
        b = etf.run_backtest(index, prices, date(2020, 8, 1), date(2020, 9, 25))
        self.assertEqual(a, b)
        self.assertEqual(a['strategy_metrics_net']['trading_days'], a['benchmark_metrics']['trading_days'])

    def test_csv_and_zip_inputs(self):
        index, prices = synthetic()
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            core = folder / 'core.zip'
            with zipfile.ZipFile(core, 'w') as z:
                z.writestr('KN_US_Equity_Core_Returns_Daily.csv',
                    'm_date,return\n' + ''.join(f'{d},{r}\n' for d, r in index))
            for ticker, obs in prices.items():
                with (folder / f'{ticker}.csv').open('w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['date', 'adjClose'])
                    writer.writerows((str(d), v) for d, v in obs.items())
            self.assertEqual(len(etf.read_benchmark(core)), 270)
            loaded = etf.load_adjusted_prices(folder, etf.SECTOR_ETFS)
            self.assertEqual(len(loaded), len(prices))
            self.assertGreater(len(etf.run_backtest(index, loaded, date(2020, 8, 1), date(2020, 9, 25))['daily_returns']), 1)


if __name__ == '__main__':
    unittest.main()
