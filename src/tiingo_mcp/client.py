"""
Thin async wrapper around the Tiingo REST API.

All methods return the raw parsed JSON (list or dict) from Tiingo.
The caller (MCP server) is responsible for presenting it to Claude.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

BASE_URL = "https://api.tiingo.com"
TIMEOUT = 30.0


class TiingoClient:
    def __init__(self, api_key: str) -> None:
        self._http = httpx.AsyncClient(
            base_url=BASE_URL,
            headers={"Authorization": f"Token {api_key}", "Content-Type": "application/json"},
            timeout=TIMEOUT,
        )

    async def aclose(self) -> None:
        await self._http.aclose()

    async def get(self, path: str, **params: Any) -> Any:
        """GET *path* with any non-None keyword args as query parameters."""
        filtered = {k: v for k, v in params.items() if v is not None}
        resp = await self._http.get(path, params=filtered)
        resp.raise_for_status()
        return resp.json()

    # ── Daily equity prices ───────────────────────────────────────────────

    async def ticker_metadata(self, ticker: str) -> dict:
        return await self.get(f"/tiingo/daily/{ticker}")

    async def end_of_day_prices(
        self,
        ticker: str,
        start_date: str | None = None,
        end_date: str | None = None,
        resample_freq: str | None = None,
    ) -> list[dict]:
        return await self.get(
            f"/tiingo/daily/{ticker}/prices",
            startDate=start_date,
            endDate=end_date,
            resampleFreq=resample_freq,
        )

    # ── News ──────────────────────────────────────────────────────────────

    async def news(
        self,
        tickers: str | None = None,
        tags: str | None = None,
        sources: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> list[dict]:
        return await self.get(
            "/tiingo/news",
            tickers=tickers,
            tags=tags,
            sources=sources,
            startDate=start_date,
            endDate=end_date,
            limit=limit,
            sortBy=sort_by,
            sortOrder=sort_order,
        )

    # ── Corporate actions ─────────────────────────────────────────────────

    async def splits(
        self, ticker: str, start_ex_date: str | None = None, end_ex_date: str | None = None
    ) -> list[dict]:
        return await self.get(
            f"/tiingo/corporate-actions/{ticker}/splits", startExDate=start_ex_date, endExDate=end_ex_date
        )

    async def dividend_distributions(
        self, ticker: str, start_ex_date: str | None = None, end_ex_date: str | None = None
    ) -> list[dict]:
        return await self.get(
            f"/tiingo/corporate-actions/{ticker}/distributions",
            startExDate=start_ex_date,
            endExDate=end_ex_date,
        )

    async def dividend_yield(
        self,
        ticker: str,
        start_date: str | None = None,
        end_date: str | None = None,
        columns: str | None = None,
    ) -> list[dict]:
        return await self.get(
            f"/tiingo/corporate-actions/{ticker}/distribution-yield",
            startDate=start_date,
            endDate=end_date,
            columns=columns,
        )

    async def search_tickers(self, query: str) -> list[dict]:
        """Search for tickers by name or symbol.  Returns permaTicker which
        is stable across renames, plus isActive flag."""
        return await self.get("/tiingo/utilities/search", query=query)

    # ── Supported tickers (full universe with delisted) ───────────────────

    async def supported_tickers(self) -> bytes:
        """Download the supported_tickers.zip CSV from Tiingo's media server.
        Returns raw ZIP bytes; caller unpacks."""
        resp = await self._http.get("https://apimedia.tiingo.com/docs/tiingo/daily/supported_tickers.zip")
        resp.raise_for_status()
        return resp.content

    # ── Fundamentals ──────────────────────────────────────────────────────

    async def fundamentals_meta(self) -> list[dict]:
        return await self.get("/tiingo/fundamentals/meta")

    async def fundamentals_daily(
        self,
        ticker: str,
        start_date: str | None = None,
        end_date: str | None = None,
        columns: str | None = None,
    ) -> list[dict]:
        return await self.get(
            f"/tiingo/fundamentals/{ticker}/daily", startDate=start_date, endDate=end_date, columns=columns
        )

    async def fundamentals_statements(
        self,
        ticker: str,
        start_date: str | None = None,
        end_date: str | None = None,
        year: int | None = None,
        quarter: int | None = None,
    ) -> list[dict]:
        return await self.get(
            f"/tiingo/fundamentals/{ticker}/statements",
            startDate=start_date,
            endDate=end_date,
            year=year,
            quarter=quarter,
        )


# ---------------------------------------------------------------------------
# Module-level singleton — created lazily on first use
# ---------------------------------------------------------------------------

_client: TiingoClient | None = None


def get_client() -> TiingoClient:
    global _client
    if _client is None:
        api_key = os.environ.get("TIINGO_API_KEY")
        if not api_key:
            raise RuntimeError(
                "TIINGO_API_KEY environment variable is not set.\n"
                "Add it to your shell profile or pass it when starting the server."
            )
        _client = TiingoClient(api_key)
    return _client
