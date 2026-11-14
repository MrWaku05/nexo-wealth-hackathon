"""Pruebas locales sin red ni dependencias externas."""
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads((ROOT / "benchmark_summary.json").read_text(encoding="utf-8"))
        cls.verify = load_module("verify_benchmark", ROOT / "scripts/verify_benchmark.py")

    def test_benchmark_summary_is_consistent(self):
        self.verify.check_summary(self.summary)

    def test_benchmark_is_distinct_from_strategy(self):
        self.assertEqual(self.summary["benchmark"], "KN US Equity Core")
        self.assertNotIn("strategy_returns", self.summary)
        self.assertNotIn("alpha", self.summary)

    def test_html_present_and_labelled(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("KN US Equity Core", html)
        self.assertIn("NEXO", html)
        self.assertIn("</html>", html.lower())
        self.assertNotIn("FMP KEY", html)


class FactorInspectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inspect = load_module("inspect_factor_model", ROOT / "scripts/inspect_factor_model.py")

    def test_manifest_from_synthetic_zip(self):
        with tempfile.TemporaryDirectory() as t:
            zp = Path(t) / "sample.zip"
            with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
                z.writestr("Factors/Market.csv", "Date,AAPL,MSFT\n2026-01-02,0.1,0.2\n2026-01-05,0.2,0.3\n")
                z.writestr("Factors/Idyo_Returns.csv", ",AAPL\n2026-01-02,0.1\n")
            m = self.inspect.inspect(zp)
            self.assertEqual(m["csv_count"], 2)
            self.assertEqual(m["all_entry_count"], 2)
            files = {item["path"]: item for item in m["entries"]}
            self.assertEqual(files["Factors/Market.csv"]["column_count"], 3)
            self.assertEqual(files["Factors/Market.csv"]["sample_first_column_values"][0], "2026-01-02")
            self.assertTrue(files["Factors/Idyo_Returns.csv"]["reserved_aggregate"])


if __name__ == "__main__":
    unittest.main()
