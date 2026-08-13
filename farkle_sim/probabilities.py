"""Exact (not approximated) Farkle roll probabilities.

Rather than relying on the commonly-quoted textbook approximations, this
module brute-force enumerates every one of the 6**n outcomes for rolling
n dice (n = 1..6, at most 46656 outcomes) and scores each one with the
same engine used by the simulator, so the numbers below are exact for the
ruleset implemented in scoring.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product

from .scoring import score_roll


@dataclass(frozen=True)
class DiceStats:
    dice: int
    farkle_probability: float
    expected_score: float          # unconditional E[score], includes farkle=0 outcomes
    expected_score_given_hit: float  # E[score | not farkle]
    hot_dice_probability: float    # P(all dice score, i.e. dice_remaining == 0)


@lru_cache(maxsize=None)
def dice_stats(n: int) -> DiceStats:
    """Exact statistics for rolling n fresh dice, n in 1..6."""
    if not (1 <= n <= 6):
        raise ValueError("n must be between 1 and 6")

    total_outcomes = 0
    farkle_outcomes = 0
    hot_dice_outcomes = 0
    score_sum = 0
    score_sum_given_hit = 0
    hit_outcomes = 0

    for combo in product(range(1, 7), repeat=n):
        result = score_roll(combo)
        total_outcomes += 1
        score_sum += result.score
        if result.is_farkle:
            farkle_outcomes += 1
        else:
            hit_outcomes += 1
            score_sum_given_hit += result.score
            if result.dice_remaining == 0:
                hot_dice_outcomes += 1

    return DiceStats(
        dice=n,
        farkle_probability=farkle_outcomes / total_outcomes,
        expected_score=score_sum / total_outcomes,
        expected_score_given_hit=(score_sum_given_hit / hit_outcomes) if hit_outcomes else 0.0,
        hot_dice_probability=hot_dice_outcomes / total_outcomes,
    )


def all_dice_stats() -> list[DiceStats]:
    return [dice_stats(n) for n in range(1, 7)]


if __name__ == "__main__":
    print(f"{'dice':>4} {'P(farkle)':>10} {'E[score]':>10} {'E[score|hit]':>13} {'P(hot dice)':>12}")
    for s in all_dice_stats():
        print(
            f"{s.dice:>4} {s.farkle_probability:>10.4f} {s.expected_score:>10.1f} "
            f"{s.expected_score_given_hit:>13.1f} {s.hot_dice_probability:>12.4f}"
        )
