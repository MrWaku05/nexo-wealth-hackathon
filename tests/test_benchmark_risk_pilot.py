"""Pruebas de no-mirada-futura y contabilidad para piloto sintético."""
import importlib.util
import unittest
from datetime import date, timedelta
from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'scripts' / 'benchmark_risk_pilot.py'
spec = importlib.util.spec_from_file_location('pilot', p)
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


def synthetic(n=260):
    start = date(2023, 1, 2)
    return [(start + timedelta(days=i), 0.001 if i % 2 == 0 else -0.001) for i in range(n)]


class PilotTests(unittest.TestCase):
    def test_exposure_bounds(self):
        w = pilot.target_weight([0.03 if j % 2 else -0.03 for j in range(60)])
        self.assertGreaterEqual(w, 0.60)
        self.assertLessEqual(w, 1.0)

    def test_past_only_no_lookahead(self):
        a = synthetic()
        b = list(a)
        b[150] = (b[150][0], 0.25)
        # Una sorpresa futura no cambia las decisiones previas.
        p1 = pilot.simulate(a)['sample_rebalances']
        p2 = pilot.simulate(b)['sample_rebalances']
        self.assertEqual(p1[:3], p2[:3])

    def test_flat_returns_only_initial_fee(self):
        series = [(d, 0.0) for d, _ in synthetic()]
        out = pilot.simulate(series)
        self.assertAlmostEqual(out['full']['benchmark']['total_return'], 0.0)
        self.assertLess(out['full']['pilot']['total_return'], 0.0)
        self.assertLess(out['cumulative_cost_fraction_approx'], 0.001)

    def test_reproducible(self):
        self.assertEqual(pilot.simulate(synthetic()), pilot.simulate(synthetic()))


if __name__ == '__main__':
    unittest.main()
