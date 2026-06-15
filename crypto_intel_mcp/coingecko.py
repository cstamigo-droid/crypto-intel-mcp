"""Low-level CoinGecko client (free public API, no key required). Cached raw pulls.

CoinGecko's free tier is generous and keyless, which makes this server run out of
the box — ideal for demos. TTLs are short for prices, longer for slow data.
"""
from __future__ import annotations

import requests

from . import cache

_BASE = "https://api.coingecko.com/api/v3"
_TTL_RESOLVE = 3600.0   # symbol -> id mapping barely changes
_TTL_MARKET = 60.0      # prices age fast
_TTL_TRENDING = 300.0
_TTL_GLOBAL = 300.0


def _get(path: str, params: dict | None = None) -> object:
    resp = requests.get(_BASE + path, params=params or {}, timeout=15)
    resp.raise_for_status()
    return resp.json()


def resolve(query: str) -> str | None:
    """Resolve a symbol/name/id to a CoinGecko coin id (cached). None if not found."""
    q = query.strip().lower()

    def _do():
        data = _get("/search", {"query": q})
        coins = data.get("coins", [])
        return coins[0]["id"] if coins else None

    return cache.get_or_fetch(f"cg:resolve:{q}", _TTL_RESOLVE, _do)


def market(coin_id: str) -> dict | None:
    """Rich market data for one coin id, incl. multi-timeframe % (cached)."""

    def _do():
        data = _get("/coins/markets", {
            "vs_currency": "usd",
            "ids": coin_id,
            "price_change_percentage": "24h,7d,30d",
        })
        return data[0] if data else None

    return cache.get_or_fetch(f"cg:market:{coin_id}", _TTL_MARKET, _do)


def trending() -> dict:
    """The current most-searched coins on CoinGecko (cached)."""
    return cache.get_or_fetch("cg:trending", _TTL_TRENDING, lambda: _get("/search/trending"))


def global_data() -> dict:
    """Global market data: total market cap, BTC dominance, 24h change (cached)."""
    return cache.get_or_fetch("cg:global", _TTL_GLOBAL, lambda: _get("/global").get("data", {}))
