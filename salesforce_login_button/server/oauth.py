import secrets
import base64
import hashlib
import urllib
import httpx
import json

from typing import TypedDict

from fastapi import Request, Response, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse

class OAuthSF:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        callback_url: str,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback_url = callback_url
        self._verifier_store = dict() # In-memory PKCE code_verifier cache
    
    def _generate_pkce_pair(self):
        code_verifier = secrets.token_urlsafe(64)[:128] # 128 char is the strict upper len limit
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip('=') # Strip trailing, url-unsafe padding character; RFC 7636 sec.4.2 says "no padding"
        return code_verifier, code_challenge
    
    async def login(self, user_id: str, domain: str) -> Response:
        if '+' in domain:
            raise HTTPException(400, 'Domain cannot contain the "+" character')
        
        state = _encode_state({
            'user_id': user_id,
            'domain': domain
        })
        code_verifier, code_challenge = self._generate_pkce_pair()
        self._verifier_store[state] = code_verifier
        
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.callback_url,
            'code_challenge': code_challenge,
            'state': state, # If not quoted, then `request.query_params.get("state")` will turn '+' into ' '
        }
        url = f'https://{domain}.my.salesforce.com/services/oauth2/authorize?{urllib.parse.urlencode(params)}'
        return RedirectResponse(url)
    
    async def callback(self, request: Request) -> dict:
        """
        Handle the Salesforce callback. Exchange code + verifier for tokens.

        Args:
            request (Request): _description_

        Returns:
            dict: Salesforce token, with the following keys:
            
                access_token
                signature
                scope
                id_token
                instance_url
                id
                token_type
                issued_at: (timestamp, mili)
                state: (only if provided)
                refresh_token: (if set up in connected app)
            
            See "Salesforce Grants an Access Token" at
            https://help.salesforce.com/s/articleView?id=xcloud.remoteaccess_oauth_web_server_flow.htm&type=5
        """
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        
        if not code or not state:
            raise HTTPException(400, "Missing code or state in callback")
        
        code_verifier = self._verifier_store.pop(state, None)
        if not code_verifier:
            raise HTTPException(401, "Missing code_verifier. Session expired?")
        
        decoded_state = _decode_state(state)
        token_url = f'https://{decoded_state['domain']}.my.salesforce.com/services/oauth2/token'
        
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.callback_url,
            'code_verifier': code_verifier,
            'format': 'json',
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(token_url, data=data)
            resp.raise_for_status()

        return _write_to_window(resp.read().decode('utf-8'))

class _OAuthState(TypedDict):
    user_id: str
    domain: str

def _encode_state(state: _OAuthState) -> str:
    return base64.urlsafe_b64encode(json.dumps(state).encode()).decode()

def _decode_state(encoded_state: str) -> _OAuthState:
    return json.loads(base64.urlsafe_b64decode(encoded_state.encode()).decode())
    
def _write_to_window(content: str) -> HTMLResponse:
    """
    Javascript script that will `postMessage` `content` back to
    `window.location.origin`. The Salesforce OAuth flow happens in a popup.
    Use this function to send data from the popup back to the notebook.
    """
    replace_map = {
        '\\': '\\\\',
        r'${': r'\${',
        '\n': ' ',
    }
    for key in replace_map:
        content = content.replace(key, replace_map[key])
    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="color-scheme" content="dark light" />
  <title>SF OAuth Writeback</title>
</head>
<body>
  <p>You may close this tab</p>
  <script>
    const token = `{content}`;
    window.opener.postMessage(token, window.location.origin);
    window.close();
  </script>
</body>
</html>""")