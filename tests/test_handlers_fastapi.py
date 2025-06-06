import pytest
from unittest.mock import patch, AsyncMock
from fastapi import Request, HTTPException
from urllib.parse import parse_qs, urlparse, urlencode

from salesforce_login_button.server.oauth import OAuthSF, _encode_state, _decode_state

@pytest.fixture
def oauth():
    return OAuthSF(
        client_id='test-client-id',
        client_secret='test-client-secret',
        callback_url='http://localhost:8000/callback'
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
    assert domain == _decode_state(qs['state'][0])['domain']
    assert qs['state'][0] in oauth._verifier_store.keys()

@pytest.mark.asyncio
async def test_callback_success(oauth: OAuthSF, httpx_mock):
    # Setup a fake code_verifier in store
    user_id = 'user123'
    domain = 'example'
    state = _encode_state({
        'user_id': user_id,
        'domain': domain
    })
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
    assert httpx_mock.get_requests()[0].url.path == "/services/oauth2/token"
    
@pytest.mark.asyncio
async def test_login_domain_validation(oauth):
    with pytest.raises(HTTPException):
        await oauth.login(user_id='user123', domain='bad+domain')

@pytest.mark.asyncio
async def test_callback_missing_code(oauth):
    request = Request({
        "type": "http",
        "query_string": urlencode({"state": "some+state"})
    })
    with pytest.raises(HTTPException):
        await oauth.callback(request)

@pytest.mark.asyncio
async def test_callback_missing_verifier(oauth):
    request = Request({
        "type": "http",
        "query_string": urlencode({"code": "somecode", "state": "badstate"})
    })
    with pytest.raises(HTTPException):
        await oauth.callback(request)