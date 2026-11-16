# tiingo-mcp

Python MCP server that exposes the [Tiingo](https://www.tiingo.com) financial
data API as tools Claude can call directly.  Modelled on
[matteoantoci/mcp-tiingo](https://github.com/matteoantoci/mcp-tiingo) (TypeScript)
with an additional `get_ticker_metadata` tool and a Python/uv stack.

## Prerequisites

- Python 3.12+, managed with [`uv`](https://docs.astral.sh/uv/)
- [`just`](https://just.systems/) task runner
- A [Tiingo API token](https://www.tiingo.com/account/api/token) (free tier available)
- [Claude Code](https://claude.ai/code) to consume the server

## Setup

### 1 — Install dependencies

```bash
just install
```

### 2 — Add your API key

On lyra, skip this: the agent-home Claude Code plugin starts the server with
`TIINGO_API_KEY` read from OpenBao (`kv-invest/tiingo/tiingo-api-token`), so
the clone needs no `.env`.

Elsewhere, `.env` is the fallback:

```bash
cp .env.example .env
# edit .env and set TIINGO_API_KEY=your-token-here
```

The server loads `.env` from the project root at startup, so the key is never
needed in your shell profile or in Claude's config. A `TIINGO_API_KEY` already
in the environment wins over `.env`.

### 3 — Register with Claude Code

```bash
just install-mcp
```

Adds `tiingo-mcp` to Claude Code's user-scoped MCP config so it is available
in every project — not just this directory.

On lyra, skip this too: the agent-home plugin registers the server.

Verify it registered:

```bash
claude mcp list
```

## Tools

| Tool | Endpoint | Key parameters |
|---|---|---|
| `get_ticker_metadata` | `GET /tiingo/daily/{ticker}` | `ticker` |
| `get_end_of_day_prices` | `GET /tiingo/daily/{ticker}/prices` | `ticker`, `start_date`, `end_date`, `resample_freq` |
| `get_news` | `GET /tiingo/news` | `tickers`, `start_date`, `end_date`, `limit`, `sort_by` |
| `get_splits` | `GET /tiingo/corporate-actions/{ticker}/splits` | `ticker`, `start_ex_date`, `end_ex_date` |
| `get_dividend_distributions` | `GET /tiingo/corporate-actions/{ticker}/distributions` | `ticker`, `start_ex_date`, `end_ex_date` |
| `get_dividend_yield` | `GET /tiingo/corporate-actions/{ticker}/distribution-yield` | `ticker`, `start_date`, `end_date`, `columns` |
| `get_fundamentals_meta` | `GET /tiingo/fundamentals/meta` | _(none)_ |
| `get_fundamentals_daily_metrics` | `GET /tiingo/fundamentals/{ticker}/daily` | `ticker`, `start_date`, `end_date`, `columns` |
| `get_fundamentals_statements` | `GET /tiingo/fundamentals/{ticker}/statements` | `ticker`, `start_date`, `end_date`, `year`, `quarter` |

All date parameters use `YYYY-MM-DD` format.  All tools return raw JSON from
the Tiingo API.

## Day-to-day

| Command | What it does |
|---|---|
| `just install-mcp` | Register with Claude Code (run once) |
| `just serve` | Start the server manually (stdio — useful for debugging) |
| `just test` | Run tests |
| `just lint` | Ruff check + format |

## Configuration

| Variable | Description |
|---|---|
| `TIINGO_API_KEY` | Tiingo API token — from OpenBao on lyra, else `.env`; never committed |

## Project layout

```
tiingo-mcp/
├── src/tiingo_mcp/
│   ├── client.py   — async Tiingo HTTP client (TiingoClient + get_client())
│   └── server.py   — FastMCP server; one @mcp.tool() per Tiingo endpoint
└── tests/
    └── test_client.py  — HTTP mocked with respx
```

## Troubleshooting

**`TIINGO_API_KEY environment variable is not set`**
Make sure `.env` exists in the project root with `TIINGO_API_KEY=…`.

**Server not visible to Claude Code after `just install-mcp`**
Start a new Claude Code session — MCP servers are loaded at session startup.

**HTTP 401 from Tiingo**
Token is invalid or expired.  Generate a new one at
<https://www.tiingo.com/account/api/token>.
