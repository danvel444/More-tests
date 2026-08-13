"""Farkle scoring engine.

Implements the standard Farkle ruleset used by most digital implementations
and calculators:

  * Single 1  = 100 points
  * Single 5  = 50 points
  * Three of a kind:
        three 1s = 1000
        three N  = N * 100   (N in 2..6)
    Four/five/six of a kind DOUBLE the three-of-a-kind value for each extra
    matching die (4-kind = 2x, 5-kind = 4x, 6-kind = 8x the base triple).
  * Straight (1-2-3-4-5-6, all six dice at once) = 1500
  * Three pairs (all six dice at once)            = 1500

A roll that contains no scoring dice/combinations at all is a "Farkle"
(bust) and scores 0 for the whole roll.

The engine always returns the *maximum* score obtainable from a roll and
how many dice were consumed to produce it (matching how virtually every
Farkle strategy calculator and most real play works: you bank the best
combination available, you don't intentionally leave scoring dice on the
table). This keeps the "how many dice do I have left to re-roll" state
well defined, which is what the bank-vs-continue strategies operate on.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Sequence

STRAIGHT_SCORE = 1500
THREE_PAIRS_SCORE = 1500


@dataclass(frozen=True)
class ScoreResult:
    """Result of scoring a single roll of dice."""

    score: int
    dice_used: int
    dice_total: int
    is_farkle: bool

    @property
    def dice_remaining(self) -> int:
        """Dice left over (unscored) after taking the best combination."""
        return self.dice_total - self.dice_used


def _triplet_base(face: int) -> int:
    return 1000 if face == 1 else face * 100


def _counts_score(counts: Counter) -> tuple[int, int]:
    """Best score obtainable from per-face counts using n-of-a-kind + singles.

    Returns (score, dice_used). Grouping every matching die of a face
    together (rather than splitting some off as singles) is always at
    least as good in this ruleset, so the decomposition is deterministic
    per face -- no search required.
    """
    score = 0
    dice_used = 0
    for face in range(1, 7):
        count = counts.get(face, 0)
        if count == 0:
            continue
        if count >= 3:
            score += _triplet_base(face) * (2 ** (count - 3))
            dice_used += count
        elif face == 1:
            score += 100 * count
            dice_used += count
        elif face == 5:
            score += 50 * count
            dice_used += count
        # 2s, 3s, 4s, 6s in counts of 1-2 score nothing and are left unused.
    return score, dice_used


def score_roll(dice: Sequence[int]) -> ScoreResult:
    """Score a single roll (up to 6 dice), returning the best decomposition."""
    n = len(dice)
    if n == 0:
        return ScoreResult(score=0, dice_used=0, dice_total=0, is_farkle=False)
    if not (1 <= n <= 6):
        raise ValueError(f"a roll must contain 1-6 dice, got {n}")
    for d in dice:
        if d not in (1, 2, 3, 4, 5, 6):
            raise ValueError(f"invalid die face: {d!r}")

    counts = Counter(dice)
    best_score, best_used = _counts_score(counts)

    if n == 6:
        # Special whole-roll combinations, only possible with all six dice.
        if len(counts) == 6:  # one of each face 1..6
            if STRAIGHT_SCORE > best_score:
                best_score, best_used = STRAIGHT_SCORE, 6
        elif len(counts) == 3 and all(c == 2 for c in counts.values()):
            if THREE_PAIRS_SCORE > best_score:
                best_score, best_used = THREE_PAIRS_SCORE, 6

    is_farkle = best_score == 0
    return ScoreResult(score=best_score, dice_used=best_used, dice_total=n, is_farkle=is_farkle)
