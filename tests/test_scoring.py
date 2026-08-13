import unittest

from farkle_sim.scoring import score_roll


class TestScoring(unittest.TestCase):
    def test_farkle(self):
        r = score_roll([2, 3, 4, 6, 2, 3])
        self.assertTrue(r.is_farkle)
        self.assertEqual(r.score, 0)

    def test_single_one(self):
        r = score_roll([1])
        self.assertEqual(r.score, 100)
        self.assertEqual(r.dice_used, 1)

    def test_single_five(self):
        r = score_roll([5])
        self.assertEqual(r.score, 50)

    def test_non_scoring_single_die(self):
        r = score_roll([3])
        self.assertTrue(r.is_farkle)

    def test_triple_ones(self):
        r = score_roll([1, 1, 1])
        self.assertEqual(r.score, 1000)
        self.assertEqual(r.dice_used, 3)

    def test_triple_twos(self):
        r = score_roll([2, 2, 2])
        self.assertEqual(r.score, 200)

    def test_triple_sixes(self):
        r = score_roll([6, 6, 6])
        self.assertEqual(r.score, 600)

    def test_four_of_a_kind_doubles_triple(self):
        r = score_roll([4, 4, 4, 4])
        self.assertEqual(r.score, 800)  # 400 * 2
        self.assertEqual(r.dice_used, 4)

    def test_five_of_a_kind(self):
        r = score_roll([2, 2, 2, 2, 2])
        self.assertEqual(r.score, 800)  # 200 * 4

    def test_six_of_a_kind(self):
        r = score_roll([3, 3, 3, 3, 3, 3])
        self.assertEqual(r.score, 2400)  # 300 * 8
        self.assertEqual(r.dice_used, 6)

    def test_straight(self):
        r = score_roll([1, 2, 3, 4, 5, 6])
        self.assertEqual(r.score, 1500)
        self.assertEqual(r.dice_used, 6)

    def test_three_pairs(self):
        r = score_roll([2, 2, 4, 4, 6, 6])
        self.assertEqual(r.score, 1500)
        self.assertEqual(r.dice_used, 6)

    def test_three_pairs_beats_naive_counting(self):
        # 1,1,5,5,3,3 as three pairs (1500) should beat singles-only reading
        # (two 1s=200 + two 5s=100 = 300, threes don't score alone).
        r = score_roll([1, 1, 5, 5, 3, 3])
        self.assertEqual(r.score, 1500)

    def test_mixed_combo_and_singles(self):
        # three 5s (500) plus a lone 1 (100) plus two non-scoring dice.
        r = score_roll([5, 5, 5, 1, 2, 3])
        self.assertEqual(r.score, 600)
        self.assertEqual(r.dice_used, 4)
        self.assertEqual(r.dice_remaining, 2)

    def test_hot_dice_all_scored(self):
        r = score_roll([1, 1, 1, 5, 5, 1])
        # four 1s (2000) + two 5s (100) = 2100, all six dice used.
        self.assertEqual(r.score, 2100)
        self.assertEqual(r.dice_remaining, 0)

    def test_invalid_die_face(self):
        with self.assertRaises(ValueError):
            score_roll([0, 1, 2])

    def test_invalid_dice_count(self):
        with self.assertRaises(ValueError):
            score_roll([1, 1, 1, 1, 1, 1, 1])


if __name__ == "__main__":
    unittest.main()
