"""Tests for server-level tool logic — specifically get_supported_tickers
which does ZIP→CSV parsing and filtering that lives in server.py."""

import csv
import io
import zipfile
from unittest.mock import AsyncMock, patch

import pytest

from tiingo_mcp.server import get_supported_tickers


def _make_zip_csv(rows: list[dict]) -> bytes:
    """Build an in-memory ZIP containing a single CSV file."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    csv_bytes = buf.getvalue().encode("utf-8")

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w") as zf:
        zf.writestr("supported_tickers.csv", csv_bytes)
    return zip_buf.getvalue()


SAMPLE_ROWS = [
    {"ticker": "AAPL", "exchange": "NASDAQ", "assetType": "Stock",
     "priceCurrency": "USD", "startDate": "1980-12-12", "endDate": ""},
    {"ticker": "SPY", "exchange": "NYSE ARCA", "assetType": "ETF",
     "priceCurrency": "USD", "startDate": "1993-01-29", "endDate": ""},
    {"ticker": "VFIAX", "exchange": "", "assetType": "Mutual Fund",
     "priceCurrency": "USD", "startDate": "2000-11-13", "endDate": ""},
    {"ticker": "FB", "exchange": "NASDAQ", "assetType": "Stock",
     "priceCurrency": "USD", "startDate": "2012-05-18", "endDate": "2022-06-08"},
]


@pytest.fixture
def mock_client():
    fake_zip = _make_zip_csv(SAMPLE_ROWS)
    mock = AsyncMock()
    mock.supported_tickers.return_value = fake_zip
    with patch("tiingo_mcp.server.get_client", return_value=mock):
        yield mock


async def test_get_supported_tickers_no_filters(mock_client):
    result = await get_supported_tickers()
    assert len(result) == 4
    tickers = [r["ticker"] for r in result]
    assert tickers == ["AAPL", "SPY", "VFIAX", "FB"]


async def test_get_supported_tickers_filter_asset_type(mock_client):
    result = await get_supported_tickers(asset_type="ETF")
    assert len(result) == 1
    assert result[0]["ticker"] == "SPY"


async def test_get_supported_tickers_filter_asset_type_case_insensitive(mock_client):
    result = await get_supported_tickers(asset_type="stock")
    tickers = [r["ticker"] for r in result]
    assert tickers == ["AAPL", "FB"]


async def test_get_supported_tickers_filter_exchange(mock_client):
    result = await get_supported_tickers(exchange="NASDAQ")
    tickers = [r["ticker"] for r in result]
    assert tickers == ["AAPL", "FB"]


async def test_get_supported_tickers_filter_exchange_case_insensitive(mock_client):
    result = await get_supported_tickers(exchange="nasdaq")
    assert len(result) == 2


async def test_get_supported_tickers_filter_both(mock_client):
    result = await get_supported_tickers(asset_type="Stock", exchange="NASDAQ")
    tickers = [r["ticker"] for r in result]
    assert tickers == ["AAPL", "FB"]


async def test_get_supported_tickers_filter_no_match(mock_client):
    result = await get_supported_tickers(asset_type="Bond")
    assert result == []


async def test_get_supported_tickers_mutual_fund(mock_client):
    result = await get_supported_tickers(asset_type="Mutual Fund")
    assert len(result) == 1
    assert result[0]["ticker"] == "VFIAX"
