"""Monte Carlo tournament runner for comparing strategies."""

from __future__ import annotations

import random
import statistics
from dataclasses import dataclass, field

from .game import DEFAULT_MIN_ENTRY, DEFAULT_TARGET_SCORE, simulate_game
from .strategies import Strategy


@dataclass
class StrategyStats:
    name: str
    games: int = 0
    wins: int = 0
    total_score: int = 0
    total_turns: int = 0
    total_busts: int = 0
    scores: list = field(default_factory=list)

    @property
    def win_rate(self) -> float:
        return self.wins / self.games if self.games else 0.0

    @property
    def avg_score(self) -> float:
        return self.total_score / self.games if self.games else 0.0

    @property
    def avg_turns(self) -> float:
        return self.total_turns / self.games if self.games else 0.0

    @property
    def bust_rate(self) -> float:
        return self.total_busts / self.total_turns if self.total_turns else 0.0

    @property
    def score_stdev(self) -> float:
        return statistics.pstdev(self.scores) if len(self.scores) > 1 else 0.0


def run_tournament(
    contestants: list[tuple[str, Strategy]],
    games: int = 10_000,
    target_score: int = DEFAULT_TARGET_SCORE,
    min_entry: int = DEFAULT_MIN_ENTRY,
    seed: int | None = None,
) -> dict[str, StrategyStats]:
    """Play every contestant against every other contestant, `games` total
    round-robin games all together at the same table each game (so with
    K contestants, each game is a K-player free-for-all). Turn order is
    reshuffled every game to remove first-mover bias.
    """
    rng = random.Random(seed)
    stats = {name: StrategyStats(name=name) for name, _ in contestants}

    for _ in range(games):
        result = simulate_game(
            contestants, target_score=target_score, min_entry=min_entry, rng=rng
        )
        for i, state in enumerate(result.players):
            s = stats[state.name]
            s.games += 1
            s.total_score += state.score
            s.total_turns += state.turns_taken
            s.total_busts += state.busts
            s.scores.append(state.score)
            if i == result.winner_index:
                s.wins += 1

    return stats


def print_leaderboard(stats: dict[str, StrategyStats]) -> str:
    rows = sorted(stats.values(), key=lambda s: s.win_rate, reverse=True)
    header = f"{'strategy':<40} {'win%':>7} {'avg score':>10} {'avg turns':>10} {'bust%':>7}"
    lines = [header, "-" * len(header)]
    for s in rows:
        lines.append(
            f"{s.name:<40} {s.win_rate*100:>6.2f}% {s.avg_score:>10.0f} "
            f"{s.avg_turns:>10.2f} {s.bust_rate*100:>6.2f}%"
        )
    return "\n".join(lines)


def duel(
    a: tuple[str, Strategy],
    b: tuple[str, Strategy],
    games: int = 10_000,
    target_score: int = DEFAULT_TARGET_SCORE,
    min_entry: int = DEFAULT_MIN_ENTRY,
    seed: int | None = None,
) -> dict[str, StrategyStats]:
    return run_tournament([a, b], games=games, target_score=target_score, min_entry=min_entry, seed=seed)
