Awesome — here’s a clean, professional **README snippet** you can drop into your repo:

---

## 🔐 Salesforce OAuth Login (PKCE) via FastAPI

This module provides a secure, testable OAuth 2.0 login flow for authenticating users to Salesforce using **PKCE** (Proof Key for Code Exchange). It is designed for internal use and integrates cleanly into FastAPI applications.

---

### ✅ Features

- Standards-compliant [OAuth 2.0 Authorization Code flow with PKCE](https://tools.ietf.org/html/rfc7636)
- Stateless FastAPI endpoints (`/login` and `/callback`)
- Base64-encoded JSON `state` payload with type-safe parsing
- One-time use `code_verifier` to prevent replay attacks
- Clean error handling with `HTTPException` (400, 401)
- 100% tested with in-memory integration tests using `httpx.AsyncClient`

---

### 📦 Endpoints

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

### 🧪 Test Coverage

- ✅ Happy path flow: `/login` → `/callback`
- ✅ Session expiration: missing or reused `state`
- ✅ Invalid domain rejection (`+` or other bad chars)
- ✅ Missing `code` or `state` parameters
- ✅ Replay attack protection (verifier only usable once)
- ✅ Fuzzed `/callback` inputs (malformed or partial)
- ✅ 100% test coverage (measured via `pytest --cov`)

Tests are run fully in-memory using `ASGITransport` and `pytest-httpx`, with no need to spin up a real webserver.

---

### 🧰 Dev Tools

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