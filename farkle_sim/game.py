"""Turn and full-game simulation engine."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .scoring import score_roll
from .strategies import Strategy, TurnContext

DEFAULT_TARGET_SCORE = 10_000
DEFAULT_MIN_ENTRY = 300  # points needed in a single turn to get "on the board"


@dataclass(frozen=True)
class TurnResult:
    points: int
    busted: bool
    newly_on_board: bool
    rolls: int


def play_turn(
    strategy: Strategy,
    player_total: int,
    on_board: bool,
    opponent_best_total: int,
    target_score: int,
    final_round: bool,
    rng: random.Random,
    min_entry: int = DEFAULT_MIN_ENTRY,
) -> TurnResult:
    """Simulate a single player's turn and return the outcome."""
    dice_remaining = 6
    turn_score = 0
    rolls = 0

    while True:
        roll = [rng.randint(1, 6) for _ in range(dice_remaining)]
        rolls += 1
        result = score_roll(roll)

        if result.is_farkle:
            return TurnResult(points=0, busted=True, newly_on_board=False, rolls=rolls)

        turn_score += result.score
        dice_remaining = result.dice_remaining
        if dice_remaining == 0:
            dice_remaining = 6  # hot dice: every die scored, re-roll all six

        can_bank = on_board or turn_score >= min_entry
        if can_bank:
            ctx = TurnContext(
                dice_remaining=dice_remaining,
                turn_score=turn_score,
                player_total=player_total,
                opponent_best_total=opponent_best_total,
                target_score=target_score,
                final_round=final_round,
            )
            if not strategy.decide(ctx):
                return TurnResult(points=turn_score, busted=False, newly_on_board=True, rolls=rolls)
        # else: not on the board yet and below min_entry -- must keep rolling.


@dataclass
class PlayerState:
    name: str
    strategy: Strategy
    score: int = 0
    on_board: bool = False
    turns_taken: int = 0
    busts: int = 0


@dataclass
class GameResult:
    players: list  # list[PlayerState] (final state)
    winner_index: int
    total_turns: int

    @property
    def winner_name(self) -> str:
        return self.players[self.winner_index].name


def simulate_game(
    players: list[tuple[str, Strategy]],
    target_score: int = DEFAULT_TARGET_SCORE,
    min_entry: int = DEFAULT_MIN_ENTRY,
    rng: random.Random | None = None,
    shuffle_order: bool = True,
) -> GameResult:
    """Simulate one full multi-player game to completion.

    Standard "final round" rule: as soon as a player's turn ends with a
    total >= target_score, every other player gets exactly one more turn,
    then the highest total wins outright (busting/overshoot has no
    special bonus in this ruleset).
    """
    if rng is None:
        rng = random.Random()

    order = list(range(len(players)))
    if shuffle_order:
        rng.shuffle(order)
    states = [PlayerState(name=n, strategy=s) for n, s in players]

    final_round_remaining: int | None = None
    total_turns = 0
    idx = 0
    while True:
        p = order[idx % len(order)]
        state = states[p]
        opponent_best = max((s.score for j, s in enumerate(states) if j != p), default=0)

        result = play_turn(
            strategy=state.strategy,
            player_total=state.score,
            on_board=state.on_board,
            opponent_best_total=opponent_best,
            target_score=target_score,
            final_round=final_round_remaining is not None,
            rng=rng,
            min_entry=min_entry,
        )
        state.turns_taken += 1
        total_turns += 1
        if result.busted:
            state.busts += 1
        else:
            state.score += result.points
            state.on_board = True

        if final_round_remaining is None and state.score >= target_score:
            final_round_remaining = len(states) - 1
        elif final_round_remaining is not None:
            final_round_remaining -= 1
            if final_round_remaining <= 0:
                break

        idx += 1

    winner_index = max(range(len(states)), key=lambda i: states[i].score)
    return GameResult(players=states, winner_index=winner_index, total_turns=total_turns)
