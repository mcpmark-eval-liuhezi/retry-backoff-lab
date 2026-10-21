"""Jittered exponential backoff for the HTTP retry client.

Implements *full jitter* (as described in the AWS Architecture Blog article
"Exponential Backoff and Jitter"): instead of sleeping for the full computed
backoff, we sleep for a uniformly random duration between zero and the capped
exponential bound. This spreads clients out and prevents synchronized retries
from re-creating a retry storm / thundering herd against a shared service
that is already struggling.

A reference implementation of the same idea can be found in the ``nopanic``
project (``src/nopanic/backoff.py``), which documents full jitter as "the
recommended default for anything that talks to a shared service - it avoids
retry stampedes."
"""

from __future__ import annotations

import random

__all__ = ["backoff_delay", "exponential_backoff_bound"]

BASE_DELAY = 0.5
"""Delay (in seconds) used before the first retry."""

MULTIPLIER = 2.0
"""Growth factor applied for each successive attempt."""

MAX_DELAY = 30.0
"""Upper bound (in seconds) on any single backoff delay."""


def exponential_backoff_bound(
    attempt,
    *,
    base=BASE_DELAY,
    multiplier=MULTIPLIER,
    max_delay=MAX_DELAY,
):
    """Deterministic exponential backoff bound for ``attempt``.

    Returns ``min(max_delay, base * multiplier ** attempt)``.
    """
    if attempt < 0:
        raise ValueError("attempt must be >= 0")
    return min(max_delay, base * (multiplier ** attempt))


def backoff_delay(
    attempt,
    *,
    base=BASE_DELAY,
    multiplier=MULTIPLIER,
    max_delay=MAX_DELAY,
    rng=random,
):
    """Return the delay (in seconds) to sleep before the next retry.

    Exponential backoff with **full jitter**::

        sleep = uniform(0, min(max_delay, base * multiplier ** attempt))

    ``attempt`` is zero-indexed: pass ``0`` for the delay before the first
    retry, ``1`` for the second, and so on.

    Args:
        attempt: Zero-indexed retry attempt number (``0`` = first retry).
        base: Base delay in seconds for the first retry.
        multiplier: Growth factor applied per attempt.
        max_delay: Ceiling on any single backoff delay, in seconds.
        rng: Source of randomness; anything with a ``uniform(a, b)``
            method (defaults to :mod:`random`), so tests can seed it
            deterministically.

    Returns:
        A random delay in the half-open interval
        ``[0, min(max_delay, base * multiplier ** attempt))``.
    """
    bound = exponential_backoff_bound(
        attempt, base=base, multiplier=multiplier, max_delay=max_delay
    )
    return rng.uniform(0.0, bound)
