import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
SPEC = importlib.util.spec_from_file_location('fmp', ROOT / 'scripts' / 'fmp_fetch_prices.py')
fmp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fmp)

class FMPTests(unittest.TestCase):
    def test_dividend_adjusted_price_normalization(self):
        out = fmp.normalize_rows([{'date': '2020-01-03', 'adjClose': 25.4}, {'date': '2020-01-02', 'adjClose': 25.0}], 'XLK')
        self.assertEqual(out, [('2020-01-02', 25.0), ('2020-01-03', 25.4)])

    def test_reject_unadjusted_price(self):
        with self.assertRaisesRegex(ValueError, 'adjClose'):
            fmp.normalize_rows([{'date': '2020-01-02', 'close': 25.0}], 'XLK')

    def test_reject_duplicate_date(self):
        with self.assertRaisesRegex(ValueError, 'duplicada'):
            fmp.normalize_rows([{'date': '2020-01-02', 'adjClose': 25.0}, {'date': '2020-01-02', 'adjClose': 24.0}], 'XLK')

if __name__ == '__main__':
    unittest.main()
