"""Composite crypto verdict — momentum, adjusted for attention and market tide.

Base score is the multi-timeframe momentum. Two context adjustments:
  - In CoinGecko's trending list  -> small boost (the market is watching).
  - Total crypto market cap 24h move -> a small tide nudge (rising tide lifts).
The result is one scored Result, so it renders with the gauge like any signal.
"""
from __future__ import annotations

from . import coingecko
from .result import Result, clamp
from .sources import momentum, trending


def _verdict(score: float) -> tuple[str, str]:
    if score >= 40:
        return "Strong momentum", "RISK-ON"
    if score >= 15:
        return "Building momentum", "LEAN LONG"
    if score > -15:
        return "Neutral", "WAIT"
    if score > -40:
        return "Weakening", "LEAN SHORT / AVOID"
    return "Breaking down", "AVOID"


def analyze(query: str) -> Result:
    coin_id = coingecko.resolve(query)
    if not coin_id:
        return Result.failed("analyze", f"no coin matches '{query}'")

    mom = momentum.fetch(query)
    if not mom.ok or mom.score is None:
        return Result.failed("analyze", mom.error or "no momentum data")

    score = mom.score
    notes = []

    # Attention: is the coin trending right now?
    tr = trending.fetch()
    is_trending = False
    if tr.ok:
        is_trending = any(coin_id == c.split(" ")[0].lower() for c in tr.data.get("trending", []))
        # trending stores symbols; also check the symbol from momentum summary
        sym = mom.summary.split(" ")[0].lower()
        is_trending = is_trending or any(sym == c.split(" ")[0].lower() for c in tr.data.get("trending", []))
    if is_trending:
        score = clamp(score + 10, -100, 100)
        notes.append("In CoinGecko trending (elevated attention).")

    # Market tide: total crypto market cap 24h direction.
    mcap_chg = None
    try:
        g = coingecko.global_data()
        mcap_chg = g.get("market_cap_change_percentage_24h_usd")
        btc_dom = g.get("market_cap_percentage", {}).get("btc")
    except Exception:
        btc_dom = None
    if mcap_chg is not None:
        score = clamp(score + clamp(mcap_chg, -5, 5), -100, 100)
        notes.append(f"Total crypto market cap {mcap_chg:+.1f}% 24h"
                     + (f", BTC dominance {btc_dom:.0f}%." if btc_dom is not None else "."))

    verdict, action = _verdict(score)
    return Result(
        source="analyze",
        ok=True,
        score=round(score, 1),
        confidence=mom.confidence,
        summary=f"{verdict} → {action}. {mom.summary}",
        data={
            "verdict": verdict,
            "action": action,
            "momentum_score": mom.score,
            "is_trending": is_trending,
            "market_cap_change_24h_pct": round(mcap_chg, 2) if mcap_chg is not None else None,
            "notes": notes,
            "url": f"https://www.coingecko.com/en/coins/{coin_id}",
        },
    )
