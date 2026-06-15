"""Crypto momentum signal — blends 24h / 7d / 30d price trend into one score.

Score -100..+100: positive = broad upward momentum across timeframes, negative =
breaking down. Each timeframe has its own volatility scale (a +8% day is as
significant as a +40% month) and weight (recent action counts more).
"""
from __future__ import annotations

from .. import coingecko
from ..result import Result, clamp

# (field, weight, scale) — |pct| == scale contributes ±100 at that timeframe.
_TIMEFRAMES = [
    ("price_change_percentage_24h_in_currency", 0.5, 8.0),
    ("price_change_percentage_7d_in_currency", 0.3, 20.0),
    ("price_change_percentage_30d_in_currency", 0.2, 40.0),
]


def fetch(query: str) -> Result:
    coin_id = coingecko.resolve(query)
    if not coin_id:
        return Result.failed("momentum", f"no coin matches '{query}'")
    try:
        m = coingecko.market(coin_id)
    except Exception as e:
        return Result.failed("momentum", str(e))
    if not m:
        return Result.failed("momentum", f"no market data for {coin_id}")

    num = den = 0.0
    used = 0
    for field, weight, scale in _TIMEFRAMES:
        pct = m.get(field)
        if pct is None:
            continue
        num += clamp(pct / scale * 100, -100, 100) * weight
        den += weight
        used += 1
    if den == 0:
        return Result.failed("momentum", "no timeframe data")

    score = clamp(num / den, -100, 100)
    confidence = min(0.2 + 0.2 * used, 1.0)  # 0.8 with all three timeframes

    c24 = m.get("price_change_percentage_24h_in_currency")
    c7 = m.get("price_change_percentage_7d_in_currency")
    c30 = m.get("price_change_percentage_30d_in_currency")

    def f(x):
        return f"{x:+.1f}%" if x is not None else "n/a"

    return Result(
        source="momentum",
        ok=True,
        score=round(score, 1),
        confidence=round(confidence, 2),
        summary=f"{(m.get('symbol') or '').upper()} momentum: 24h {f(c24)} · 7d {f(c7)} · 30d {f(c30)}.",
        data={
            "change_24h_pct": round(c24, 2) if c24 is not None else None,
            "change_7d_pct": round(c7, 2) if c7 is not None else None,
            "change_30d_pct": round(c30, 2) if c30 is not None else None,
            "url": f"https://www.coingecko.com/en/coins/{coin_id}",
        },
    )
