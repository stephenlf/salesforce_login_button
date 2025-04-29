from fastapi import FastAPI, Request
from salesforce_login_button.handlers.fastapi import OAuthSF

def create_test_app():
    app = FastAPI()

    oauth = OAuthSF(
        client_id='test-client-id',
        client_secret='test-client-secret',
        redirect_uri='http://testserver/callback',
    )
    
    app.state.oauth = oauth

    @app.get('/login')
    async def login():
        return await app.state.oauth.login(user_id='test-user', domain='test')

    @app.get('/callback')
    async def callback(request: Request):
        return await app.state.oauth.callback(request)
    
    return app