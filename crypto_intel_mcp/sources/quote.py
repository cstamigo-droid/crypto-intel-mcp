"""Crypto price snapshot — price, 24h move, market cap rank, volume, ATH distance.

Informational (no directional score): use it to anchor any analysis with the
current state of a coin.
"""
from __future__ import annotations

from .. import coingecko
from ..result import Result


def fetch(query: str) -> Result:
    coin_id = coingecko.resolve(query)
    if not coin_id:
        return Result.failed("quote", f"no coin matches '{query}'")
    try:
        m = coingecko.market(coin_id)
    except Exception as e:
        return Result.failed("quote", str(e))
    if not m:
        return Result.failed("quote", f"no market data for {coin_id}")

    price = m.get("current_price")
    chg = m.get("price_change_percentage_24h")
    ath_dist = m.get("ath_change_percentage")
    sym = (m.get("symbol") or "").upper()
    # Adaptive price format: commas for >=$1, more decimals for sub-dollar coins.
    price_str = f"{price:,.2f}" if price is None or price >= 1 else f"{price:.8f}".rstrip("0")
    summary = (
        f"{sym} ${price_str} · {chg:+.1f}% 24h · rank #{m.get('market_cap_rank', '?')} "
        f"· {ath_dist:+.0f}% from ATH"
    )
    return Result(
        source="quote",
        ok=True,
        summary=summary,
        data={
            "name": m.get("name"),
            "symbol": sym,
            "price_usd": price,
            "change_24h_pct": round(chg, 2) if chg is not None else None,
            "market_cap": m.get("market_cap"),
            "market_cap_rank": m.get("market_cap_rank"),
            "volume_24h": m.get("total_volume"),
            "ath": m.get("ath"),
            "pct_from_ath": round(ath_dist, 1) if ath_dist is not None else None,
            "url": f"https://www.coingecko.com/en/coins/{coin_id}",
        },
    )
