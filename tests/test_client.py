"""Tests for TiingoClient — uses respx to mock HTTP."""

import pytest
import respx
import httpx

from tiingo_mcp.client import TiingoClient

BASE = "https://api.tiingo.com"


@pytest.fixture
def client():
    return TiingoClient(api_key="test-key")


@respx.mock
async def test_ticker_metadata(client):
    respx.get(f"{BASE}/tiingo/daily/AAPL").mock(
        return_value=httpx.Response(200, json={"ticker": "AAPL", "name": "Apple Inc"})
    )
    result = await client.ticker_metadata("AAPL")
    assert result["ticker"] == "AAPL"


@respx.mock
async def test_end_of_day_prices(client):
    respx.get(f"{BASE}/tiingo/daily/AAPL/prices").mock(
        return_value=httpx.Response(200, json=[{"date": "2024-01-02", "adjClose": 185.2}])
    )
    result = await client.end_of_day_prices("AAPL", start_date="2024-01-02", end_date="2024-01-02")
    assert len(result) == 1
    assert result[0]["adjClose"] == 185.2


@respx.mock
async def test_end_of_day_prices_omits_none_params(client):
    route = respx.get(f"{BASE}/tiingo/daily/MSFT/prices").mock(
        return_value=httpx.Response(200, json=[])
    )
    await client.end_of_day_prices("MSFT")
    assert "startDate" not in str(route.calls[0].request.url)


@respx.mock
async def test_splits(client):
    respx.get(f"{BASE}/tiingo/corporate-actions/AAPL/splits").mock(
        return_value=httpx.Response(200, json=[{"exDate": "2020-08-31", "splitFactor": 4.0}])
    )
    result = await client.splits("AAPL")
    assert result[0]["splitFactor"] == 4.0


@respx.mock
async def test_http_error_raises(client):
    respx.get(f"{BASE}/tiingo/daily/FAKE/prices").mock(
        return_value=httpx.Response(404, text="Not Found")
    )
    with pytest.raises(httpx.HTTPStatusError):
        await client.end_of_day_prices("FAKE")
