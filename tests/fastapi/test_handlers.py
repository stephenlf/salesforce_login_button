import pytest
from unittest.mock import patch, AsyncMock
from fastapi import Request
from urllib.parse import parse_qs, urlparse, urlencode

from salesforce_login_button.handlers.fastapi import OAuthSF

@pytest.fixture
def oauth():
    return OAuthSF(
        client_id='test-client-id',
        client_secret='test-client-secret',
        redirect_uri='http://localhost:8000/callback'
    )

@pytest.mark.asyncio
async def test_login_generates_redirect(oauth: OAuthSF):
    domain = 'test'
    response = await oauth.login(user_id='user123', domain=domain)
    location = urlparse(response.headers['location'])
    qs = parse_qs(location.query)
    assert response.status_code == 307 # Redirect
    assert f"{domain}.my.salesforce.com" in location.netloc
    assert "code_challenge" in qs
    assert domain in qs['state'][0]

@pytest.mark.asyncio
async def test_callback_success(oauth: OAuthSF, httpx_mock):
    # Setup a fake code_verifier in store
    user_id = 'user123'
    domain = 'example'
    state = f'{user_id}+{domain}'
    oauth._verifier_store[state] = 'test_code_verifier'
    
    # Mock the httpx.AsyncClient().post call
    httpx_mock.add_response(
        method="POST",
        url="https://example.my.salesforce.com/services/oauth2/token",
        status_code=200,
        json={
            "access_token": "mock-token",
            "instance_url": "https://test.my.salesforce.com",
            "state": state,
        }
    )
    
    # Simulate a Salesforce callback
    request = Request({
        "type": "http",
        "query_string": urlencode({"code": "mock-code", "state": state})
    })
    
    html_response = await oauth.callback(request)
    
    body = html_response.body.decode()
    assert isinstance(body, str)
    assert "window.opener.postMessage" in body
    
@pytest.mark.asyncio
async def test_login_domain_validation(oauth):
    with pytest.raises(ValueError):
        await oauth.login(user_id='user123', domain='bad+domain')

@pytest.mark.asyncio
async def test_callback_missing_code(oauth):
    request = Request({
        "type": "http",
        "query_string": urlencode({"state": "some+state"})
    })
    with pytest.raises(ValueError):
        await oauth.callback(request)

@pytest.mark.asyncio
async def test_callback_missing_verifier(oauth):
    request = Request({
        "type": "http",
        "query_string": urlencode({"code": "somecode", "state": "badstate"})
    })
    with pytest.raises(ValueError):
        await oauth.callback(request)