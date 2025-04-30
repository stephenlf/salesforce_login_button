import os
from fastapi import FastAPI, Request, HTTPException
from salesforce_login_button.server import OAuthSF
from starlette.middleware.sessions import SessionMiddleware

def create_callback_server(
    client_id: str = os.environ.get('SF_OAUTH_CLIENT_ID'),
    client_secret: str = os.environ.get('SF_OAUTH_CLIENT_SECRET'),
    callback_url: str = 'http://localhost/sf/callback'
) -> FastAPI:
    app = FastAPI()

    app.add_middleware(SessionMiddleware, secret_key='your-session-secret')
    
    if client_id is None or client_secret is None:
        raise ValueError('Neither client_id nor client_secret may be empty')

    # Create an OAuthSF instance
    oauth = OAuthSF(
        client_id=client_id,
        client_secret=client_secret,
        callback_url=callback_url,  # Must match your Salesforce Connected App settings
    )

    # Store the instance on app.state for shared access
    app.state.oauth = oauth

    @app.get('/login')
    async def login(request: Request):
        """
        Starts the OAuth flow. Send the user here in a popup window.
        
        Expects:
          - `domain` query parameter supplied by the client
          - `user_id` stored in the session (e.g., set by your auth middleware)
        """
        domain = request.query_params.get('domain')
        if not domain:
          raise HTTPException(status_code=400, detail="Missing 'domain' query parameter")
        
        user_id = request.session.get('user_id')
        if not user_id:
          raise HTTPException(status_code=401, detail="User not authenticated.")
        return await app.state.oauth.login(user_id=user_id, domain=domain)

    @app.get('/callback')
    async def callback(request: Request):
        """
        Handles Salesforce's redirect back to your app after user login.

        This endpoint returns an HTML doc that sends the Salesforce token to the
        originating window and closes the popup.
        """
        return await app.state.oauth.callback(request)

    return app