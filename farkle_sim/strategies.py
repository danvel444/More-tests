"""Bank-vs-reroll decision strategies.

Every strategy implements `decide(ctx: TurnContext) -> bool`, returning
True to keep rolling (push for more points) or False to bank the turn
score and end the turn. The engine only asks for a decision when banking
is actually legal (i.e. the player is on the board, or this turn's score
already clears the game's minimum entry score) -- see game.py.
"""

from __future__ import annotations

from dataclasses import dataclass

from .probabilities import dice_stats


@dataclass(frozen=True)
class TurnContext:
    dice_remaining: int      # dice available for the *next* roll if we continue (6 = hot dice/turn start)
    turn_score: int          # points banked-in-hand for this turn so far (not yet on the scoreboard)
    player_total: int        # this player's confirmed score before this turn
    opponent_best_total: int # the best confirmed score among opponents
    target_score: int        # score needed to trigger the final round
    final_round: bool        # True if this is the player's last-chance turn of the game


class Strategy:
    name = "base"

    def decide(self, ctx: TurnContext) -> bool:  # pragma: no cover - interface
        raise NotImplementedError

    def __repr__(self) -> str:
        return self.name


@dataclass
class ThresholdStrategy(Strategy):
    """Classic "go big to N" strategy: keep rolling until turn_score >= threshold."""

    threshold: int

    def __post_init__(self):
        self.name = f"threshold({self.threshold})"

    def decide(self, ctx: TurnContext) -> bool:
        return ctx.turn_score < self.threshold


@dataclass
class ThresholdWithFloorStrategy(Strategy):
    """Push for `threshold` points, but bail out early once dice_remaining
    drops to a dangerous level, even if the threshold hasn't been hit yet.
    This models the common "take the small points and run" instinct once
    you're down to your last die or two.
    """

    threshold: int
    risk_floor_dice: int = 1  # bank once dice_remaining <= this, regardless of threshold

    def __post_init__(self):
        self.name = f"threshold({self.threshold})+floor({self.risk_floor_dice})"

    def decide(self, ctx: TurnContext) -> bool:
        if ctx.dice_remaining <= self.risk_floor_dice:
            return False
        return ctx.turn_score < self.threshold


class ExpectedValueStrategy(Strategy):
    """1-ply expected-value-optimal strategy.

    For n dice remaining, rolling again is worth more (in expectation)
    than banking exactly when:

        turn_score < (1 - p_farkle(n)) * E[score | hit, n] / p_farkle(n)

    i.e. below a breakeven turn score that depends only on how many dice
    are left. Those breakeven values are derived from the *exact* roll
    probabilities in probabilities.py (full enumeration), not textbook
    approximations. `margin` scales the breakeven up/down (>1 = more
    conservative, <1 = more aggressive) to explore risk appetite around
    the EV-neutral point.
    """

    def __init__(self, margin: float = 1.0):
        self.margin = margin
        self.name = f"ev_optimal(margin={margin:g})"
        self._breakeven = {}
        for n in range(1, 7):
            s = dice_stats(n)
            p = s.farkle_probability
            g = s.expected_score_given_hit
            self._breakeven[n] = ((1 - p) * g / p) * margin if p > 0 else float("inf")

    def decide(self, ctx: TurnContext) -> bool:
        n = ctx.dice_remaining if ctx.dice_remaining > 0 else 6
        return ctx.turn_score < self._breakeven[n]

    def breakeven_table(self) -> dict:
        return dict(self._breakeven)


@dataclass
class CatchUpStrategy(Strategy):
    """Score-aware strategy: push harder when behind, play it safer when
    ahead -- especially once the final round has started and the lead
    just needs protecting.
    """

    base_threshold: int = 300
    risk_floor_dice: int = 1
    aggression_per_deficit_1000: float = 120.0  # extra threshold per 1000 pts behind
    lead_protection_factor: float = 0.5         # shrink threshold when comfortably ahead

    def __post_init__(self):
        self.name = (
            f"catch_up(base={self.base_threshold}, floor={self.risk_floor_dice})"
        )

    def decide(self, ctx: TurnContext) -> bool:
        deficit = ctx.opponent_best_total - ctx.player_total
        threshold = self.base_threshold
        if deficit > 0:
            threshold += (deficit / 1000.0) * self.aggression_per_deficit_1000
        elif deficit < 0:
            # We're ahead -- ease off, especially in the final round where
            # busting could hand the win away for nothing.
            factor = self.lead_protection_factor if ctx.final_round else 0.8
            threshold = max(150, threshold + deficit * factor / 10)

        if ctx.final_round and ctx.player_total + ctx.turn_score >= ctx.opponent_best_total + 50:
            # Already enough banked-in-hand to retake/keep the lead: stop pushing luck.
            return ctx.dice_remaining > self.risk_floor_dice and ctx.turn_score < threshold * 0.5

        if ctx.dice_remaining <= self.risk_floor_dice:
            return False
        return ctx.turn_score < threshold


def make_threshold_family(values) -> list[ThresholdStrategy]:
    return [ThresholdStrategy(v) for v in values]
