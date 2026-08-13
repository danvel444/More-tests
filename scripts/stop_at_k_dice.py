"""Isolate the "stop when N dice are left" question with a large-sample run.

Runs a multi-way tournament between pure dice-count cutoff strategies
(bank only once dice_remaining <= K, ignoring turn score entirely until
then), the EV-optimal dice-and-score-aware strategy, and a realistic
fixed-threshold baseline -- split across worker processes to make a
million-game run practical on a multi-core box.

Usage:
    python3 scripts/stop_at_k_dice.py --games 1000000 --workers 4 --seed 42
"""

from __future__ import annotations

import argparse
import sys
import time
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from farkle_sim.simulate import run_tournament  # noqa: E402
from farkle_sim.strategies import ExpectedValueStrategy, ThresholdStrategy, ThresholdWithFloorStrategy  # noqa: E402

NEVER_BANK_ON_SCORE = 10**9  # effectively disables the score-threshold half of ThresholdWithFloorStrategy


def build_contestants():
    return [
        ("stop_at_1_die", ThresholdWithFloorStrategy(NEVER_BANK_ON_SCORE, risk_floor_dice=1)),
        ("stop_at_2_dice", ThresholdWithFloorStrategy(NEVER_BANK_ON_SCORE, risk_floor_dice=2)),
        ("stop_at_3_dice", ThresholdWithFloorStrategy(NEVER_BANK_ON_SCORE, risk_floor_dice=3)),
        ("ev_optimal", ExpectedValueStrategy()),
        ("threshold(300)", ThresholdStrategy(300)),
    ]


def run_chunk(args):
    seed, games = args
    contestants = build_contestants()
    stats = run_tournament(contestants, games=games, seed=seed)
    return {
        name: (s.games, s.wins, s.total_score, s.total_turns, s.total_busts)
        for name, s in stats.items()
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=1_000_000)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    per_worker = args.games // args.workers
    chunks = [(args.seed + i, per_worker) for i in range(args.workers)]
    remainder = args.games - per_worker * args.workers
    if remainder:
        chunks[-1] = (chunks[-1][0], chunks[-1][1] + remainder)

    t0 = time.time()
    with Pool(args.workers) as pool:
        results = pool.map(run_chunk, chunks)
    elapsed = time.time() - t0

    totals = {}
    for chunk_result in results:
        for name, (games, wins, score, turns, busts) in chunk_result.items():
            g, w, sc, tu, bu = totals.get(name, (0, 0, 0, 0, 0))
            totals[name] = (g + games, w + wins, sc + score, tu + turns, bu + busts)

    print(f"{args.games:,} games total across {args.workers} workers in {elapsed:.1f}s\n")
    header = f"{'strategy':<18} {'win%':>7} {'avg score':>10} {'avg turns':>10} {'bust%':>7}"
    print(header)
    print("-" * len(header))
    rows = sorted(totals.items(), key=lambda kv: kv[1][1] / kv[1][0], reverse=True)
    for name, (g, w, sc, tu, bu) in rows:
        print(
            f"{name:<18} {w / g * 100:>6.2f}% {sc / g:>10.0f} {tu / g:>10.2f} {bu / tu * 100:>6.2f}%"
        )


if __name__ == "__main__":
    main()
