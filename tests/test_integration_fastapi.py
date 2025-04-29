import pytest
import random
import string

from httpx import AsyncClient, ASGITransport
from test_app import create_test_app
from urllib.parse import parse_qs, urlencode
from fastapi import HTTPException

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@pytest.fixture
async def client():
    app = create_test_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

@pytest.mark.asyncio
async def test_login_redirect(client):
    response = await client.get("/login")
    assert response.status_code == 307

@pytest.mark.asyncio
async def test_callback_flow(client, httpx_mock):
    # Mock the Salesforce /token response
    httpx_mock.add_response(
        url="https://test.my.salesforce.com/services/oauth2/token",
        method="POST",
        json={"access_token": "mock-token"}
    )
    
    # First, log in to get the verifier stored
    res = await client.get("/login")
    state = parse_qs(res.headers['location'])['state'][0]

        
    # Then simulate a callback
    response = await client.get(f"/callback?code=mockcode&state={state}")
    
    assert response.status_code == 200
    assert "window.opener.postMessage" in response.text
    
@pytest.mark.asyncio
@pytest.mark.parametrize("mutation", range(20))
async def test_fuzz_callback_flow(client, mutation):
    """Fuzz '/callback' endpoint with random codes and states."""
    
    random.seed = mutation
    
    query_params = {}
    # Include bogus `code` or omit entirely
    if random.choice([True, False]):
        query_params["code"] = random_string(20)
    # Include bogus `state` or omit entirely
    if random.choice([True, False]):
        query_params["state"] = random_string(20)
    # Typo in param names
    if random.choice([True, False]):
        query_params["codex"] = random_string(20)
        
    query = urlencode(query_params)
    response = await client.get(f"/callback?{query}")
    
    assert response.status_code in (200, 400, 401)

@pytest.mark.asyncio
async def test_session_replay_attack(client, httpx_mock):
    """Test that repeated calls to '/callback' fail after the first call"""
        # Mock the Salesforce /token response
    httpx_mock.add_response(
        url="https://test.my.salesforce.com/services/oauth2/token",
        method="POST",
        json={"access_token": "mock-token"}
    )
    
    # First, log in to get the verifier stored
    res = await client.get("/login")
    state = parse_qs(res.headers['location'])['state'][0]

        
    # Then simulate a callback
    response = await client.get(f"/callback?code=mockcode&state={state}")
    response.raise_for_status()
    
    unauthorized = await client.get(f"/callback?code=mockcode&state={state}")
    assert unauthorized.status_code == 401
    