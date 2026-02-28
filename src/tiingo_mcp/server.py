"""
Tiingo MCP server.

Exposes Tiingo financial data as MCP tools that Claude can call directly.
Mirrors the tool set from matteoantoci/mcp-tiingo (TypeScript) plus
get_ticker_metadata which is essential for ticker validation.

Start with:  uv run tiingo-mcp
Configure:   TIINGO_API_KEY environment variable
"""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from tiingo_mcp.client import get_client

# Load .env from the project root (the directory containing src/)
# This runs before any tool is called, so TIINGO_API_KEY is available
# regardless of whether the server is launched via `just serve` or
# directly by Claude Code.
load_dotenv(Path(__file__).parents[3] / ".env")

mcp = FastMCP("tiingo")


# ---------------------------------------------------------------------------
# Daily equity data
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_ticker_metadata(ticker: str) -> dict:
    """
    Fetch metadata for a ticker: company name, description, exchange,
    start/end date of available price history.

    Use this to validate a ticker or find out how far back data goes.
    """
    return await get_client().ticker_metadata(ticker)


@mcp.tool()
async def get_end_of_day_prices(
    ticker: str,
    start_date: str | None = None,
    end_date: str | None = None,
    resample_freq: str | None = None,
) -> list[dict]:
    """
    Fetch end-of-day price history for a ticker.

    Returns a list of daily records with fields:
      date, close, high, low, open, volume,
      adjClose, adjHigh, adjLow, adjOpen, adjVolume,
      divCash, splitFactor

    Args:
        ticker:        Ticker symbol, e.g. "AAPL"
        start_date:    First date to return, YYYY-MM-DD (optional)
        end_date:      Last date to return, YYYY-MM-DD (optional)
        resample_freq: Resample frequency — "daily" (default), "weekly",
                       "monthly", "annually" (optional)
    """
    return await get_client().end_of_day_prices(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        resample_freq=resample_freq,
    )


# ---------------------------------------------------------------------------
# News
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_news(
    tickers: str | None = None,
    tags: str | None = None,
    sources: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int | None = None,
    sort_by: str | None = None,
    sort_order: str | None = None,
) -> list[dict]:
    """
    Fetch news articles from Tiingo.

    Args:
        tickers:    Comma-separated ticker symbols to filter by (optional)
        tags:       Comma-separated tags to filter by (optional)
        sources:    Comma-separated news sources to filter by (optional)
        start_date: Earliest article date, YYYY-MM-DD (optional)
        end_date:   Latest article date, YYYY-MM-DD (optional)
        limit:      Max number of articles to return (optional)
        sort_by:    "publishedDate" or "crawlDate" (optional)
        sort_order: "asc" or "desc" (optional)
    """
    return await get_client().news(
        tickers=tickers,
        tags=tags,
        sources=sources,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# ---------------------------------------------------------------------------
# Corporate actions
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_splits(
    ticker: str,
    start_ex_date: str | None = None,
    end_ex_date: str | None = None,
) -> list[dict]:
    """
    Fetch historical stock split data for a ticker.

    Args:
        ticker:        Ticker symbol
        start_ex_date: Earliest ex-date to include, YYYY-MM-DD (optional)
        end_ex_date:   Latest ex-date to include, YYYY-MM-DD (optional)
    """
    return await get_client().splits(
        ticker=ticker,
        start_ex_date=start_ex_date,
        end_ex_date=end_ex_date,
    )


@mcp.tool()
async def get_dividend_distributions(
    ticker: str,
    start_ex_date: str | None = None,
    end_ex_date: str | None = None,
) -> list[dict]:
    """
    Fetch historical dividend and distribution data for a ticker.

    Args:
        ticker:        Ticker symbol
        start_ex_date: Earliest ex-date to include, YYYY-MM-DD (optional)
        end_ex_date:   Latest ex-date to include, YYYY-MM-DD (optional)
    """
    return await get_client().dividend_distributions(
        ticker=ticker,
        start_ex_date=start_ex_date,
        end_ex_date=end_ex_date,
    )


@mcp.tool()
async def get_dividend_yield(
    ticker: str,
    start_date: str | None = None,
    end_date: str | None = None,
    columns: str | None = None,
) -> list[dict]:
    """
    Fetch historical dividend yield data for a ticker.

    Args:
        ticker:     Ticker symbol
        start_date: Start date YYYY-MM-DD (optional)
        end_date:   End date YYYY-MM-DD (optional)
        columns:    Comma-separated metric names to return (optional)
    """
    return await get_client().dividend_yield(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        columns=columns,
    )


# ---------------------------------------------------------------------------
# Fundamentals
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_fundamentals_meta() -> list[dict]:
    """
    Fetch fundamental metadata for all companies covered by Tiingo.
    Returns available metrics and their definitions.
    No parameters required.
    """
    return await get_client().fundamentals_meta()


@mcp.tool()
async def get_fundamentals_daily_metrics(
    ticker: str,
    start_date: str | None = None,
    end_date: str | None = None,
    columns: str | None = None,
) -> list[dict]:
    """
    Fetch daily fundamental metrics for a ticker (PE ratio, market cap, etc.).

    Args:
        ticker:     Ticker symbol
        start_date: Start date YYYY-MM-DD (optional)
        end_date:   End date YYYY-MM-DD (optional)
        columns:    Comma-separated metric names to return (optional)
    """
    return await get_client().fundamentals_daily(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        columns=columns,
    )


@mcp.tool()
async def get_fundamentals_statements(
    ticker: str,
    start_date: str | None = None,
    end_date: str | None = None,
    year: int | None = None,
    quarter: int | None = None,
) -> list[dict]:
    """
    Fetch historical financial statement data for a ticker.
    Covers Balance Sheet, Income Statement, Cash Flow, and Overview.

    Args:
        ticker:     Ticker symbol
        start_date: Start date YYYY-MM-DD (optional)
        end_date:   End date YYYY-MM-DD (optional)
        year:       Fiscal year, e.g. 2024 (optional)
        quarter:    Fiscal quarter 1-4, or 0 for annual (optional)
    """
    return await get_client().fundamentals_statements(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        year=year,
        quarter=quarter,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
