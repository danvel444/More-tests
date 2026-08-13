import unittest

from farkle_sim.probabilities import dice_stats


class TestProbabilities(unittest.TestCase):
    def test_one_die_exact(self):
        s = dice_stats(1)
        # Only 1 and 5 score out of 6 faces -> farkle on 4/6 outcomes.
        self.assertAlmostEqual(s.farkle_probability, 4 / 6, places=9)
        self.assertAlmostEqual(s.expected_score, (100 + 50) / 6, places=9)

    def test_two_dice_exact(self):
        s = dice_stats(2)
        # Farkle iff neither die is a 1 or 5: (4/6)^2 = 4/9.
        self.assertAlmostEqual(s.farkle_probability, 4 / 9, places=9)

    def test_probabilities_decrease_with_more_dice(self):
        farkle_probs = [dice_stats(n).farkle_probability for n in range(1, 7)]
        for a, b in zip(farkle_probs, farkle_probs[1:]):
            self.assertGreater(a, b)

    def test_six_dice_low_farkle_rate(self):
        s = dice_stats(6)
        self.assertLess(s.farkle_probability, 0.05)

    def test_hot_dice_probability_bounds(self):
        for n in range(1, 7):
            s = dice_stats(n)
            self.assertGreaterEqual(s.hot_dice_probability, 0.0)
            self.assertLessEqual(s.hot_dice_probability, 1.0)


if __name__ == "__main__":
    unittest.main()
