from fastapi import FastAPI, Request
from salesforce_login_button.handlers.fastapi import OAuthSF

app = FastAPI()

oauth = OAuthSF(
    client_id='test-client-id',
    client_secret='test-client-secret',
    redirect_uri='http://testserver/callback',
)

@app.get('/login')
async def login():
    return await oauth.login(user_id='test-user', domain='test')

@app.get('/callback')
async def callback(request: Request):
    return await oauth.callback(request)