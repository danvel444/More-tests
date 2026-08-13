import random
import unittest

from farkle_sim.game import play_turn, simulate_game
from farkle_sim.strategies import (
    CatchUpStrategy,
    ExpectedValueStrategy,
    ThresholdStrategy,
    ThresholdWithFloorStrategy,
    TurnContext,
)


class TestThresholdStrategy(unittest.TestCase):
    def test_continues_below_threshold(self):
        s = ThresholdStrategy(300)
        ctx = TurnContext(dice_remaining=3, turn_score=100, player_total=0,
                           opponent_best_total=0, target_score=10000, final_round=False)
        self.assertTrue(s.decide(ctx))

    def test_banks_at_threshold(self):
        s = ThresholdStrategy(300)
        ctx = TurnContext(dice_remaining=3, turn_score=300, player_total=0,
                           opponent_best_total=0, target_score=10000, final_round=False)
        self.assertFalse(s.decide(ctx))


class TestThresholdWithFloor(unittest.TestCase):
    def test_bails_on_low_dice_even_under_threshold(self):
        s = ThresholdWithFloorStrategy(threshold=2000, risk_floor_dice=1)
        ctx = TurnContext(dice_remaining=1, turn_score=150, player_total=0,
                           opponent_best_total=0, target_score=10000, final_round=False)
        self.assertFalse(s.decide(ctx))

    def test_keeps_rolling_with_plenty_of_dice(self):
        s = ThresholdWithFloorStrategy(threshold=2000, risk_floor_dice=1)
        ctx = TurnContext(dice_remaining=4, turn_score=150, player_total=0,
                           opponent_best_total=0, target_score=10000, final_round=False)
        self.assertTrue(s.decide(ctx))


class TestExpectedValueStrategy(unittest.TestCase):
    def test_breakeven_decreases_with_fewer_dice(self):
        s = ExpectedValueStrategy()
        table = s.breakeven_table()
        values = [table[n] for n in range(1, 7)]
        for a, b in zip(values, values[1:]):
            self.assertLess(a, b)

    def test_bank_above_breakeven(self):
        s = ExpectedValueStrategy()
        breakeven_1_die = s.breakeven_table()[1]
        ctx = TurnContext(dice_remaining=1, turn_score=int(breakeven_1_die) + 100,
                           player_total=0, opponent_best_total=0, target_score=10000, final_round=False)
        self.assertFalse(s.decide(ctx))

    def test_roll_below_breakeven(self):
        s = ExpectedValueStrategy()
        breakeven_1_die = s.breakeven_table()[1]
        ctx = TurnContext(dice_remaining=1, turn_score=max(0, int(breakeven_1_die) - 10),
                           player_total=0, opponent_best_total=0, target_score=10000, final_round=False)
        self.assertTrue(s.decide(ctx))


class TestGameSimulation(unittest.TestCase):
    def test_play_turn_terminates_and_returns_valid_result(self):
        rng = random.Random(42)
        strategy = ThresholdStrategy(300)
        for _ in range(200):
            result = play_turn(
                strategy, player_total=0, on_board=False, opponent_best_total=0,
                target_score=10000, final_round=False, rng=rng,
            )
            self.assertGreaterEqual(result.points, 0)
            self.assertGreaterEqual(result.rolls, 1)
            if result.busted:
                self.assertEqual(result.points, 0)

    def test_simulate_game_produces_a_winner_above_target(self):
        rng = random.Random(7)
        players = [
            ("A", ThresholdStrategy(300)),
            ("B", ExpectedValueStrategy()),
            ("C", CatchUpStrategy()),
        ]
        result = simulate_game(players, target_score=3000, rng=rng)
        self.assertGreaterEqual(result.players[result.winner_index].score, 3000 - 1)
        # every player got at least one turn
        for p in result.players:
            self.assertGreaterEqual(p.turns_taken, 1)

    def test_min_entry_rule_blocks_low_banks(self):
        # A strategy that always wants to bank immediately should still be
        # forced to keep rolling until it clears the entry minimum.
        class BankImmediately:
            name = "bank_immediately"

            def decide(self, ctx):
                return False

        rng = random.Random(1)
        strategy = BankImmediately()
        successes = 0
        for _ in range(500):
            result = play_turn(
                strategy, player_total=0, on_board=False, opponent_best_total=0,
                target_score=10000, final_round=False, rng=rng, min_entry=300,
            )
            if not result.busted:
                self.assertGreaterEqual(result.points, 300)
                successes += 1
        self.assertGreater(successes, 0)


if __name__ == "__main__":
    unittest.main()
