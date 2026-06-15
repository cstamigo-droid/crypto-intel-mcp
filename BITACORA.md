# BITACORA — crypto-intel-mcp

---

## 2026-06-14 — Sesión 1 — v0.1 construido (primer output de mcp-factory)

**Qué es:** primer server de muestra real generado con `mcp-factory` — valida la
fábrica con algo serio y suma una segunda pieza de portfolio (acciones + cripto).

**Completado:**
- ✅ Generado con `python new_server.py crypto-intel-mcp "..."` desde la fábrica
- ✅ Cliente `coingecko.py` (API gratis, sin key): resolve / market / trending / global, cacheado
- ✅ 3 sources: `quote.py` (snapshot), `momentum.py` (24h/7d/30d scored), `trending.py` (atención)
- ✅ `analyze.py` composite: momentum + boost trending (+10) + marea de mercado (mcap 24h)
- ✅ `server.py`: 4 tools (`crypto_get_quote`, `crypto_momentum`, `crypto_trending`, `crypto_analyze`)
- ✅ Borrado el source/tool de ejemplo de la plantilla
- ✅ `evals/crypto_intel_eval.xml` (8 pares Q/A) + README actualizado
- ✅ Verificado en vivo: BTC composite +22 LEAN LONG (detectó trending + marea), DOGE precio sub-dólar OK, coin inexistente degrada sin crash, 4 tools registradas

**Decisiones:**
- CoinGecko free (sin key) elegido a propósito: corre al instante para demos.
- Score momentum: escalas por volatilidad (24h=8% → ±100, 7d=20%, 30d=40%), pesos 0.5/0.3/0.2.
- Composite devuelve un Result con score → usa el gauge estándar (no hace falta render_composite).

**Pendiente (Fase 6 — acciones humanas, igual que equity-intel-mcp):**
- [ ] Claude Desktop: pegar bloque `mcpServers` del README, reiniciar, probar "give me a full read on bitcoin"
- [ ] Video demo 60s → portfolio Upwork/Lemon.io
- [ ] GitHub público + topics `mcp` `claude` `crypto` `model-context-protocol`

**Lección para la fábrica:** el flujo generar→reemplazar source→probar funcionó sin fricción.
Único pulido manual: formato de precio adaptativo (sci-notation feo con `:.4g` para precios grandes).
