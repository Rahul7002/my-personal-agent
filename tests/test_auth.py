import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture(autouse=True)
def disable_limiter():
    """Disable SlowAPI rate limiting specifically for auth flow tests."""
    app.state.limiter.enabled = False
    yield
    app.state.limiter.enabled = True

@pytest.mark.anyio
async def test_register_and_login_flow(client: AsyncClient):
    user_payload = {
        "email": "pytest_user@example.com",
        "password": "StrongPassword123!"
    }

    # 1. Register new user
    reg_res = await client.post("/api/v1/auth/register", json=user_payload)
    assert reg_res.status_code in [201, 200]
    reg_data = reg_res.json()
    print(f"********************* Status: {reg_data}, {reg_res}")
    assert reg_data["email"] == user_payload["email"]

    # 2. Duplicate registration fails
    dup_res = await client.post("/api/v1/auth/register", json=user_payload)
    assert dup_res.status_code in [400, 409]

    # 3. Login with wrong password -> expects 401
    bad_login = await client.post(
        "/api/v1/auth/login",
        json={"email": user_payload["email"], "password": "WrongPassword!"}
    )
    assert bad_login.status_code == 401

    # 4. Login with correct password -> expects 200
    good_login = await client.post("/api/v1/auth/login", json=user_payload)
    assert good_login.status_code == 200
    assert "access_token" in good_login.json()