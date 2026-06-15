"""What's trending on CoinGecko right now — the most-searched coins.

A breadth/attention signal: coins the market is actively looking at. Takes no
specific coin (the optional query argument is ignored).
"""
from __future__ import annotations

from .. import coingecko
from ..result import Result


def fetch(query: str = "") -> Result:
    try:
        t = coingecko.trending()
    except Exception as e:
        return Result.failed("trending", str(e))
    coins = t.get("coins", [])
    if not coins:
        return Result.failed("trending", "no trending data")

    symbols = [c["item"]["symbol"].upper() for c in coins[:10]]
    detail = [
        f"{c['item']['symbol'].upper()} (#{c['item'].get('market_cap_rank') or '?'})"
        for c in coins[:10]
    ]
    return Result(
        source="trending",
        ok=True,
        summary="Trending now: " + ", ".join(symbols),
        data={
            "trending": detail,
            "url": "https://www.coingecko.com/en/highlights/trending-crypto",
        },
    )
