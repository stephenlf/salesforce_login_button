import pytest
from unittest.mock import patch, AsyncMock
from fastapi import Request
from starlette.datastructures import QueryParams
from urllib.parse import parse_qs, urlparse

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