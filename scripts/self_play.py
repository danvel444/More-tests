"""Self-play sanity check: N clones of the same strategy at one table.

Purpose: with every seat running an identical strategy, no seat has any
inherent edge, so each clone's win rate should land statistically near
1/N. This is a control on the simulator itself (confirms turn-order
shuffling isn't secretly favoring anyone) and, as a side effect, reports
each strategy's "intrinsic" avg score / turns / bust rate uncontaminated
by whatever mix of opponents it happened to be tested against elsewhere.

Usage:
    python3 scripts/self_play.py --strategy ev_optimal --players 5 --games 20000
    python3 scripts/self_play.py --strategy all --players 5 --games 20000
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from farkle_sim.simulate import print_leaderboard, run_tournament  # noqa: E402
from farkle_sim.strategies import (  # noqa: E402
    CatchUpStrategy,
    ExpectedValueStrategy,
    ThresholdStrategy,
    ThresholdWithFloorStrategy,
)

NEVER_BANK_ON_SCORE = 10**9

FACTORIES = {
    "stop_at_1_die": lambda: ThresholdWithFloorStrategy(NEVER_BANK_ON_SCORE, risk_floor_dice=1),
    "stop_at_2_dice": lambda: ThresholdWithFloorStrategy(NEVER_BANK_ON_SCORE, risk_floor_dice=2),
    "stop_at_3_dice": lambda: ThresholdWithFloorStrategy(NEVER_BANK_ON_SCORE, risk_floor_dice=3),
    "ev_optimal": lambda: ExpectedValueStrategy(),
    "threshold(300)": lambda: ThresholdStrategy(300),
    "threshold(300)+floor(1)": lambda: ThresholdWithFloorStrategy(300, 1),
    "catch_up": lambda: CatchUpStrategy(),
}


def run_self_play(name: str, players: int, games: int, seed: int):
    factory = FACTORIES[name]
    contestants = [(f"{name}#{i+1}", factory()) for i in range(players)]
    stats = run_tournament(contestants, games=games, seed=seed)
    rows = [stats[n] for n, _ in contestants]
    win_rates = [s.win_rate for s in rows]
    expected = 1 / players
    spread = max(win_rates) - min(win_rates)
    print(f"=== self-play: {players}x {name}, {games:,} games ===")
    print(print_leaderboard(stats))
    print(
        f"expected win% if perfectly symmetric: {expected*100:.2f}%   "
        f"observed spread across seats: {spread*100:.2f} pts"
    )
    avg_score = sum(s.avg_score for s in rows) / players
    avg_bust = sum(s.bust_rate for s in rows) / players
    print(f"intrinsic (self-play) avg score: {avg_score:.0f}   avg bust rate: {avg_bust*100:.2f}%\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategy", required=True, choices=list(FACTORIES) + ["all"])
    ap.add_argument("--players", type=int, default=5)
    ap.add_argument("--games", type=int, default=20_000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    names = list(FACTORIES) if args.strategy == "all" else [args.strategy]
    for name in names:
        run_self_play(name, args.players, args.games, args.seed)


if __name__ == "__main__":
    main()
