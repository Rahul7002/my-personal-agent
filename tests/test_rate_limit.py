import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_login_rate_limiting(client: AsyncClient):
    payload = {"email": "ratelimit_test@example.com", "password": "badpassword"}
    statuses = []

    # Send 7 rapid requests (default limit is 5/minute)
    for _ in range(7):
        res = await client.post("/api/v1/auth/login", json=payload)
        statuses.append(res.status_code)

    # Confirm that rate limiting kicked in
    assert 429 in statuses