"""Parallel head-to-head duel between two named strategies (large sample sizes).

Usage:
    python3 scripts/duel_mp.py --a stop_at_2_dice --b stop_at_3_dice --games 1000000 --workers 4
"""

from __future__ import annotations

import argparse
import sys
import time
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from farkle_sim.simulate import run_tournament  # noqa: E402
from stop_at_k_dice import build_contestants  # noqa: E402

_ALL = {name: strat for name, strat in build_contestants()}


def run_chunk(args):
    seed, games, a_name, b_name = args
    contestants = [(a_name, _ALL[a_name]), (b_name, _ALL[b_name])]
    stats = run_tournament(contestants, games=games, seed=seed)
    return {name: (s.games, s.wins, s.total_score, s.total_turns, s.total_busts) for name, s in stats.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True, choices=list(_ALL))
    ap.add_argument("--b", required=True, choices=list(_ALL))
    ap.add_argument("--games", type=int, default=1_000_000)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    per_worker = args.games // args.workers
    chunks = [(args.seed + i, per_worker, args.a, args.b) for i in range(args.workers)]
    remainder = args.games - per_worker * args.workers
    if remainder:
        s, g, a, b = chunks[-1]
        chunks[-1] = (s, g + remainder, a, b)

    t0 = time.time()
    with Pool(args.workers) as pool:
        results = pool.map(run_chunk, chunks)
    elapsed = time.time() - t0

    totals = {}
    for chunk_result in results:
        for name, (games, wins, score, turns, busts) in chunk_result.items():
            g, w, sc, tu, bu = totals.get(name, (0, 0, 0, 0, 0))
            totals[name] = (g + games, w + wins, sc + score, tu + turns, bu + busts)

    print(f"{args.a} vs {args.b}: {args.games:,} games in {elapsed:.1f}s\n")
    for name, (g, w, sc, tu, bu) in sorted(totals.items(), key=lambda kv: kv[1][1], reverse=True):
        print(f"  {name:<16} win% {w / g * 100:6.2f}   avg score {sc / g:8.0f}   bust% {bu / tu * 100:6.2f}")


if __name__ == "__main__":
    main()
