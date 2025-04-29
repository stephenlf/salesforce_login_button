# Demo Marimo Server

Clone this repository to your local machine.

## Setting up your External Client App

The Demo App needs an External Client App configured in your org to work. You can easily set this up yourself.

1. Go to Setup and use the Quick Find box to find the "External Client App Manager"
2. Click "New External Client App"
3. Fill out the "New External Client App" form
  1. Enter a Name and Email as appropriate
  2. Set the "Distribution State" to "Local"
  3. Check the "Enable OAuth"
  4. Set the "Callback URL" to "http://localhost:5000" (remote notebook environments may need to be configured differently)
  5. Select the OAuth Scopes you need. For trusted, internal usage, you can use `full`.
  6. Select "Enable Authorization Code and Credentials Flow"
  7. Select "Require Proof Key for Code Exchange (PKCE) extension for Supported Authorization Flows"
  8. Click "Create"
4. Open the newly created Client App, go to the "Settings" tab, and click "Consumer Key and Secret." You will save the "Consumer Key" to the `SF_OAUTH_CLIENT_ID` environment variable.

## Installing dependencies