import pytest
import respx
from httpx import AsyncClient, Response

@pytest.mark.anyio
@respx.mock
async def test_chat_endpoint_mocked(client: AsyncClient):
    # 1. Mock Ollama's /api/chat endpoint with the expected schema
    respx.post("http://localhost:11434/api/chat").mock(
        return_value=Response(
            200,
            json={
                "model": "llama3.2:1b",
                "message": {
                    "role": "assistant",
                    "content": "Mocked AI reply"
                },
                "done": True
            }
        )
    )

    user_payload = {
        "email": "pytest_user@example.com",
        "password": "StrongPassword123!"
    }

    # 2. Register user
    reg_res = await client.post("/api/v1/auth/register", json=user_payload)
    assert reg_res.status_code in [201, 200]

    # 3. Login to get access token
    good_login = await client.post("/api/v1/auth/login", json=user_payload)
    assert good_login.status_code in [201, 200]
    token = good_login.json()["access_token"]

    # 4. Attach Bearer token to headers
    headers = {
        "Authorization": f"Bearer {token}"
    }

    chat_payload = {
        "prompt": "Hello AI",
        "system_prompt": "You are an expert backend engineer. Be concise and precise."
    }

    # 5. Call the protected endpoint
    response = await client.post("/api/v1/chat/ask", json=chat_payload, headers=headers)

    print("\n" + "=" * 50)
    print(f"[TEST DEBUG] HTTP Status: {response.status_code}")
    print(f"[TEST DEBUG] Response JSON: {response.json()}")
    print("=" * 50 + "\n")

    # 6. Assertions
    assert response.status_code == 200
    res_data = response.json()
    assert "response" in res_data or "message" in res_data