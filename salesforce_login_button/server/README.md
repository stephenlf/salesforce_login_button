## 🔐 Salesforce OAuth Login (PKCE) via FastAPI

This module provides a secure, testable OAuth 2.0 login flow for authenticating users to Salesforce using **PKCE** (Proof Key for Code Exchange). It is designed for internal use and integrates cleanly into FastAPI applications.

---

### Usage

To integrate Salesforce OAuth handlers into your FastAPI app:

1. **Instantiate** the `OAuthSF` class with your Salesforce app credentials.
2. **Store** the instance on `app.state` to maintain session state across requests.
3. **Create `/login` and `/callback` routes** that delegate to the `OAuthSF` methods.

Here’s a complete example:

```python
from fastapi import FastAPI, Request, HTTPException
from salesforce_login_button.server import OAuthSF
from starlette.middleware.sessions import SessionMiddleware

def create_app():
    app = FastAPI()

    app.add_middleware(SessionMiddleware, secret_key='your-session-secret')

    # Create an OAuthSF instance
    oauth = OAuthSF(
        client_id='your-salesforce-client-id',
        client_secret='your-salesforce-client-secret',
        redirect_uri='https://yourapp.com/callback',  # Must match your Salesforce Connected App settings
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
```

---

### Important Notes

- `redirect_uri` **must match** the redirect URI configured in your Salesforce Connected App.
- `user_id` and `domain` passed into `/login` can be dynamic if needed — they are encoded into the `state` parameter for security and continuity.
- After successful authentication, the `/callback` route automatically sends the token back to the frontend via a secure `window.postMessage()` script.

---

### Features

- Standards-compliant [OAuth 2.0 Authorization Code flow with PKCE](https://tools.ietf.org/html/rfc7636)
- Stateless FastAPI endpoints (`/login` and `/callback`)
- Base64-encoded JSON `state` payload with type-safe parsing
- One-time use `code_verifier` to prevent replay attacks
- Clean error handling with `HTTPException` (400, 401)
- 100% tested with in-memory integration tests using `httpx.AsyncClient`

---

### Endpoints

- `GET /login`:  
  Generates an authorization URL for Salesforce, including:
  - `code_challenge` (SHA-256 of `code_verifier`)
  - Encoded `state` (`user_id`, `domain`, optional `csrf_token`)
  - Redirects to Salesforce OAuth page

- `GET /callback`:  
  Handles Salesforce redirect, validates:
  - `code` and `state` are present
  - `code_verifier` matches the original challenge
  - Exchanges `code` for an access token
  - Returns success via `window.postMessage()` script (for popup integration)

---

### Test Coverage

- ✅ Happy path flow: `/login` → `/callback`
- ✅ Session expiration: missing or reused `state`
- ✅ Invalid domain rejection (`+` or other bad chars)
- ✅ Missing `code` or `state` parameters
- ✅ Replay attack protection (verifier only usable once)
- ✅ Fuzzed `/callback` inputs (malformed or partial)
- ✅ 100% test coverage (measured via `pytest --cov`)

Tests are run fully in-memory using `ASGITransport` and `pytest-httpx`, with no need to spin up a real webserver.

---

### Dev Tools

This project uses:

- `pytest-asyncio` for async test support
- `pytest-httpx` for mocking external HTTP calls (Salesforce `/token`)
- `httpx.AsyncClient` for in-memory FastAPI test client
- `TypedDict` + Base64-encoded JSON for safely structured OAuth state

---

### ⚠️ Notes

- This module assumes a trusted internal usage model — CSRF protection is not included by default
- For external-facing apps, consider:
  - Expiring/verifying `state` values more strictly
  - Signing `state` payloads with HMAC for tamper detection
  - Encrypting the `code_verifier` if stored client-side