from fastapi import FastAPI, Request
from salesforce_login_button.server import OAuthSF, create_callback_server
import pytest

def create_test_app():
    app = FastAPI()

    oauth = OAuthSF(
        client_id='test-client-id',
        client_secret='test-client-secret',
        callback_url='http://testserver/callback',
    )
    
    app.state.oauth = oauth

    @app.get('/login')
    async def login():
        return await app.state.oauth.login(user_id='test-user', domain='test')

    @app.get('/callback')
    async def callback(request: Request):
        return await app.state.oauth.callback(request)
    
    return app

def test_build_real_app():
    app = create_callback_server('test_client', 'test_secret')
    assert 'FastAPI' in str(type(app))