"""
Ticket-generation strategies and the low-level draw/ticket vector helpers
used by every simulation in lottery/simulate.py.

Every combination (a draw, or a ticket) is represented as a boolean vector
of length `pool_size` -- this lets "how many numbers does this ticket share
with this draw" become a single dot product, which numpy vectorizes over
millions of draws at once.
"""
from __future__ import annotations

import numpy as np

from .games import Game


def _empty_bool_matrix(n: int, pool_size: int) -> np.ndarray:
    return np.zeros((n, pool_size), dtype=np.int8)


def random_combo_bool(pool_size: int, pick_count: int, rng: np.random.Generator) -> np.ndarray:
    """A single random combination as a boolean vector of length pool_size."""
    vec = np.zeros(pool_size, dtype=np.int8)
    idx = rng.choice(pool_size, size=pick_count, replace=False)
    vec[idx] = 1
    return vec


def simulate_draws(game: Game, n: int, rng: np.random.Generator) -> dict:
    """Simulate n independent official draws for `game`.

    Returns a dict with:
      main_bool : (n, pool_size) int8      -- which numbers were drawn
      bonus_idx : (n,) int  or None        -- index of the bonus ball (bonus games only)
      grand     : (n,) int  or None        -- Grand Number 1..grand_range (Daily Grand only)
    """
    main_bool = _empty_bool_matrix(n, game.pool_size)
    # Vectorized "choose pick_count of pool_size without replacement" per row:
    # argsort of iid uniforms per row gives a random permutation per row cheaply.
    rand_keys = rng.random((n, game.pool_size))
    order = np.argsort(rand_keys, axis=1)
    chosen = order[:, :game.pick_count]
    rows = np.repeat(np.arange(n), game.pick_count)
    main_bool[rows, chosen.ravel()] = 1

    bonus_idx = None
    if game.has_bonus:
        # bonus ball comes from the numbers NOT drawn in the main draw
        bonus_pos_in_remaining = rng.integers(0, game.pool_size - game.pick_count, size=n)
        remaining = order[:, game.pick_count:]
        bonus_idx = remaining[np.arange(n), bonus_pos_in_remaining]

    grand = None
    if game.grand_range is not None:
        grand = rng.integers(1, game.grand_range + 1, size=n)

    return {"main_bool": main_bool, "bonus_idx": bonus_idx, "grand": grand}


def fixed_ticket(game: Game, rng: np.random.Generator) -> dict:
    """A single ticket, chosen once, replayed on every draw."""
    main = random_combo_bool(game.pool_size, game.pick_count, rng)
    grand = int(rng.integers(1, game.grand_range + 1)) if game.grand_range else None
    return {"main_bool": main, "grand": grand}


def quick_pick_tickets(game: Game, n: int, rng: np.random.Generator) -> dict:
    """n independently re-randomized tickets, one per draw."""
    main = _empty_bool_matrix(n, game.pool_size)
    rand_keys = rng.random((n, game.pool_size))
    order = np.argsort(rand_keys, axis=1)
    chosen = order[:, :game.pick_count]
    rows = np.repeat(np.arange(n), game.pick_count)
    main[rows, chosen.ravel()] = 1
    grand = rng.integers(1, game.grand_range + 1, size=n) if game.grand_range else None
    return {"main_bool": main, "grand": grand}


def calendar_ticket(game: Game, rng: np.random.Generator) -> dict:
    """A 'popular pattern' ticket: every main number drawn from 1..31
    (birthday-style picking), a common real-world human bias."""
    pool_lo31 = min(31, game.pool_size)
    idx = rng.choice(pool_lo31, size=game.pick_count, replace=False)
    main = np.zeros(game.pool_size, dtype=np.int8)
    main[idx] = 1
    grand = int(rng.integers(1, game.grand_range + 1)) if game.grand_range else None
    return {"main_bool": main, "grand": grand}


def spread_ticket(game: Game, rng: np.random.Generator) -> dict:
    """An 'anti-popular' ticket: numbers deliberately drawn only from the
    33+ range (or the top half of the pool), to structurally avoid the
    human birthday-clustering zone."""
    lo = min(31, game.pool_size - game.pick_count)
    hi_pool = game.pool_size - lo
    idx = lo + rng.choice(hi_pool, size=game.pick_count, replace=False)
    main = np.zeros(game.pool_size, dtype=np.int8)
    main[idx] = 1
    grand = int(rng.integers(1, game.grand_range + 1)) if game.grand_range else None
    return {"main_bool": main, "grand": grand}


def full_wheel(game: Game, pool_numbers: np.ndarray) -> np.ndarray:
    """Every combination of game.pick_count numbers drawn from the given
    subset `pool_numbers` -- a classic 'wheeling system'. Returns an
    (n_lines, pool_size) boolean matrix."""
    from itertools import combinations
    lines = []
    for combo in combinations(pool_numbers.tolist(), game.pick_count):
        vec = np.zeros(game.pool_size, dtype=np.int8)
        vec[list(combo)] = 1
        lines.append(vec)
    return np.array(lines, dtype=np.int8)
