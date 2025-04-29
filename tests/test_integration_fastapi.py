import pytest
from httpx import AsyncClient, ASGITransport
from test_app import create_test_app
from urllib.parse import parse_qs

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
    print(f"State after login: {state}")
    print(f"Verifier store after login: {client._transport.app.state.oauth._verifier_store}")

        
    # Then simulate a callback
    response = await client.get(f"/callback?code=mockcode&state={state}")
    
    assert response.status_code == 200
    assert "window.opener.postMessage" in response.text
    
    