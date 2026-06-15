#!/usr/bin/env python3
"""crypto-intel-mcp — Crypto market intelligence (price, momentum, trending) over MCP.

Transport: stdio (local — Claude Desktop / Claude Code / agents).

Each tool returns a uniform Result rendered as Markdown (default) or JSON.
Sources fail gracefully: a missing data source returns "no data", never a
fabricated value. Powered by CoinGecko's free public API — no key required.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

from . import analyze
from .formatting import ResponseFormat, render
from .sources import momentum, quote, trending

# Load .env from the project root (parent of this package), if present.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

mcp = FastMCP("crypto_intel_mcp")


# ─── shared helpers ──────────────────────────────────────────────────────────

async def _run(fn, *args):
    """Run a blocking source function in a thread so the event loop stays free."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: fn(*args))


class CoinInput(BaseModel):
    """Input for single-coin tools."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    coin: str = Field(
        ...,
        description="Coin symbol, name, or id — e.g. 'BTC', 'bitcoin', 'ETH', 'solana'.",
        min_length=1,
        max_length=50,
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="'markdown' for a human-readable report or 'json' for structured data.",
    )


class MarketInput(BaseModel):
    """Input for market-wide tools that take no specific coin."""

    model_config = ConfigDict(extra="forbid")

    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="'markdown' for a human-readable report or 'json' for structured data.",
    )


# ─── tools ───────────────────────────────────────────────────────────────────

@mcp.tool(
    name="crypto_get_quote",
    annotations={"title": "Crypto Price Snapshot", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
)
async def crypto_get_quote(params: CoinInput) -> str:
    """Get a current price snapshot for a cryptocurrency.

    Informational (not a buy/sell signal): live price, 24h change, market-cap
    rank, 24h volume, and distance from all-time high.

    Examples:
        - "What's bitcoin trading at?" -> coin='BTC'
        - "How far is ETH from its all-time high?" -> coin='ethereum'
    """
    sig = await _run(quote.fetch, params.coin)
    return render(sig, f"Quote — {params.coin}", params.response_format)


@mcp.tool(
    name="crypto_momentum",
    annotations={"title": "Crypto Momentum Signal", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
)
async def crypto_momentum(params: CoinInput) -> str:
    """Score a coin's price momentum across 24h, 7d and 30d into one signal.

    Returns a directional score from -100 (breaking down) to +100 (strong
    broad-based upward momentum), weighting recent action more heavily.

    Examples:
        - "Does solana have momentum?" -> coin='SOL'
        - "Is bitcoin trending up or down?" -> coin='bitcoin'
    """
    sig = await _run(momentum.fetch, params.coin)
    return render(sig, f"Momentum — {params.coin}", params.response_format)


@mcp.tool(
    name="crypto_trending",
    annotations={"title": "Trending Coins", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
)
async def crypto_trending(params: MarketInput) -> str:
    """List the coins the market is searching for most right now (CoinGecko trending).

    A breadth/attention indicator — useful for spotting where retail interest is
    concentrating. Takes no coin.

    Examples:
        - "What crypto is trending right now?"
        - "Show me the hot coins today."
    """
    sig = await _run(trending.fetch, "")
    return render(sig, "Trending Crypto", params.response_format)


@mcp.tool(
    name="crypto_analyze",
    annotations={"title": "Full Crypto Analysis (Composite)", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
)
async def crypto_analyze(params: CoinInput) -> str:
    """Run a full analysis of a coin and return one scored verdict.

    Blends multi-timeframe momentum with whether the coin is trending and the
    overall crypto market tide into a single verdict (RISK-ON → AVOID) with a
    gauge and the reasoning behind it.

    This is the primary tool — prefer it for "should I look at X?" questions.

    Examples:
        - "Give me a full read on bitcoin" -> coin='BTC'
        - "Should I be looking at SOL?" -> coin='solana'
    """
    sig = await _run(analyze.analyze, params.coin)
    return render(sig, f"Crypto Intelligence — {params.coin}", params.response_format)


def main() -> None:
    """Console entrypoint — runs the MCP server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
