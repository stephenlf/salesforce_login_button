import os
import marimo

from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.sessions import SessionMiddleware
from salesforce_login_button.handlers.fastapi import OAuthSF

# Create a marimo asgi app
marimo_server = (
    marimo.create_asgi_app()
    .with_dynamic_directory(path="", directory=Path(__name__).parent / "notebooks")
)

# Create a FastAPI app
app = FastAPI()
app.mount("/", marimo_server.build())
app.add_middleware(SessionMiddleware, 'my_secret_key')

# Set up Salesforce OAuth handlers
sf_oauth = OAuthSF(
    client_id=os.environ.get('SF_CLIENT_ID'),
    client_secret=os.environ.get('SF_CLIENT_SECRET'),
    callback_url="http://localhost:5000/sf/callback",
)

app.state.sf_oauth = sf_oauth

@app.get('/ping')
async def ping():
    return 'pong'

# @app.get('/sf/login')
# async def login(request: Request):
#     """
#     Starts the OAuth flow. Send the user here in a popup window.
    
#     Expects:
#         - `domain` query parameter supplied by the client
#         - `user_id` stored in the session (e.g., set by your auth middleware)
#     """
#     domain = request.query_params.get('domain')
#     if not domain:
#         raise HTTPException(status_code=400, detail="Missing 'domain' query parameter")
    
#     user_id = request.session.get('user_id')
#     if not user_id:
#         raise HTTPException(status_code=401, detail="User not authenticated.")
#     return await app.state.oauth.login(user_id=user_id, domain=domain)

# @app.get('/sf/callback')
# async def callback(request: Request):
#     """
#     Handles Salesforce's redirect back to your app after user login.

#     This endpoint returns an HTML doc that sends the Salesforce token to the
#     originating window and closes the popup.
#     """
#     return await app.state.oauth.callback(request)


# Run with `uvicorn demo.marimo_demo:app --host localhost --port 5000`

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=5000, log_level="info")