import pytest
from httpx import AsyncClient, ASGITransport
from test_app import app
from urllib.parse import parse_qs

@pytest.fixture
async def client():
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
        
    # Then simulate a callback
    response = await client.get("/callback?code=mockcode&state=test-user+test")
    
    assert response.status_code == 200
    assert "window.opener.postMessage" in response.text
    
    