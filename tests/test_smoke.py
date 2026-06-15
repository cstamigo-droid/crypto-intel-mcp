"""Smoke test — hits the real CoinGecko API and prints each Result.

Run:  python tests/test_smoke.py [COIN]
This is a live network test, not a unit test.
"""
import sys
from pathlib import Path

# Make stdout UTF-8 safe so the live demo output (em-dashes, arrows) prints on
# Windows consoles (cp1252) without crashing. No PYTHONUTF8 env var required.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from crypto_intel_mcp import analyze  # noqa: E402
from crypto_intel_mcp.formatting import ResponseFormat, render  # noqa: E402
from crypto_intel_mcp.sources import momentum, quote, trending  # noqa: E402


def main() -> None:
    coin = sys.argv[1] if len(sys.argv) > 1 else "bitcoin"
    print(f"\n{'=' * 70}\n  QUOTE\n{'=' * 70}")
    print(render(quote.fetch(coin), f"quote — {coin}", ResponseFormat.MARKDOWN))

    print(f"\n{'=' * 70}\n  MOMENTUM\n{'=' * 70}")
    print(render(momentum.fetch(coin), f"momentum — {coin}", ResponseFormat.MARKDOWN))

    print(f"\n{'=' * 70}\n  TRENDING\n{'=' * 70}")
    print(render(trending.fetch(), "trending", ResponseFormat.MARKDOWN))

    print(f"\n{'=' * 70}\n  ANALYZE (composite)\n{'=' * 70}")
    print(render(analyze.analyze(coin), f"analyze — {coin}", ResponseFormat.MARKDOWN))


if __name__ == "__main__":
    main()
