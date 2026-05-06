# tiingo-mcp

MCP server that exposes the Tiingo financial data API as Claude tools. Provides stock prices, fundamentals, news, dividends, splits, and ticker search.

> **Python invocation:** always `uv run python` — never bare `python`/`python3`. Package ops via `uv add`/`uv sync`. (Repo-wide; see top-level CLAUDE.md.)

## Tool Inventory

| Tool | Returns | Key Params |
|------|---------|------------|
| `get_ticker_metadata` | Company info, exchange, date range | ticker |
| `get_end_of_day_prices` | Daily OHLCV + adjusted prices | ticker, start_date, end_date, resample_freq |
| `get_news` | News articles | tickers, tags, sources, start_date, end_date, limit |
| `get_splits` | Stock split history | ticker, start_ex_date, end_ex_date |
| `get_dividend_distributions` | Dividend history | ticker, start_ex_date, end_ex_date |
| `get_dividend_yield` | Historical dividend yield | ticker, start_date, end_date, columns |
| `search_tickers` | Ticker/company matches | query |
| `get_supported_tickers` | Full ticker list (~80k) | asset_type, exchange |
| `get_fundamentals_meta` | Available metrics and definitions | (none) |
| `get_fundamentals_daily_metrics` | PE ratio, market cap, etc. | ticker, start_date, end_date, columns |
| `get_fundamentals_statements` | Balance sheet, income, cash flow | ticker, start_date, end_date, year, quarter |

## Architecture

```
src/tiingo_mcp/
    __init__.py   — package marker
    client.py     — TiingoClient: async HTTP client wrapping Tiingo REST API
    server.py     — FastMCP server: one @mcp.tool() per endpoint
```

- `TiingoClient(api_key)` — HTTP client using `httpx.AsyncClient`
- Lazy singleton via `get_client()` — one instance per server lifetime
- Each MCP tool wraps a `TiingoClient` method, returning raw Tiingo JSON
- `.env` loaded at startup via `load_dotenv()`

## Setup

```bash
just install-mcp   # Register with Claude Code (user scope, one-time)
just serve         # Start MCP server (stdio transport, for debugging)
just test [args]   # Run pytest
just lint          # Ruff check + format check
just typing        # Type check
just install       # Sync deps
just clean         # Remove .venv, caches
```

After `just install-mcp`, restart Claude Code to pick up the new server.

## Configuration

`TIINGO_API_KEY` in `.env` at project root (never committed).

## Dependencies

- `mcp[cli]>=1.0` — FastMCP server framework
- `httpx>=0.27` — async HTTP client
- `python-dotenv>=1.0` — load .env
- Dev: `pytest`, `pytest-asyncio`, `respx` (HTTP mocking)

## Gotchas

- Server fails silently if `TIINGO_API_KEY` is not set — HTTP 401 on all calls
- All tools return raw Tiingo JSON; formatting/filtering is Claude's responsibility
- `get_supported_tickers` downloads a large ZIP (~80k tickers); takes time
- `permaTicker` is stable across renames — useful for tracking FB → META
- MCP servers load at Claude Code session startup; register once, then restart Claude
