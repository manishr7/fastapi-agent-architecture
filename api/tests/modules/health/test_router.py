import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_envelope(client: AsyncClient) -> None:
    response = await client.get("/api/v6/health")
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"data", "meta", "error"}
    assert body["error"] is None
    assert body["data"]["status"] == "ok"
    assert "correlation_id" in body["meta"]
    assert "request_id" in body["meta"]
    assert body["meta"]["correlation_id"] == response.headers["X-Correlation-ID"]
    assert body["meta"]["request_id"] == response.headers["X-Request-ID"]
