import os
import dotenv

from fastapi import FastAPI, Request, HTTPException
from salesforce_login_button.handlers.fastapi import OAuthSF
from starlette.middleware.sessions import SessionMiddleware

dotenv.load_dotenv()

_host = os.environ.get("SF_OAUTH_HOST", "localhost")
_port = os.environ.get("SF_OAUTH_PORT", 5000)
_hostname = f'http://{_host}:{_port}/callback'

def create_app():
    app = FastAPI()

    app.add_middleware(SessionMiddleware, secret_key='your-session-secret')

    # Create an OAuthSF instance
    oauth = OAuthSF(
        client_id=os.environ.get("SF_OAUTH_CLIENT_ID"),
        client_secret=os.environ.get("SF_OAUTH_CLIENT_SECRET"),
        callback_url=_hostname,  # Must match your Salesforce Connected App settings
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
        
        user_id = request.query_params.get('user_id')
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

if __name__ == '__main__':
    import uvicorn
    app = create_app()
    uvicorn.run(app, host=_host, port=_port)
