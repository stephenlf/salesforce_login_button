import anywidget

from typing import TypedDict
from pathlib import Path

from simple_salesforce import Salesforce
from traitlets import traitlets


class OAuthToken(TypedDict):
    access_token: str
    instance_url: str
    id: str
    issued_at: str
    signature: str

class SalesforceLoginButton(anywidget.AnyWidget):
    """
    A Salesforce log in button.

    Usage: 
        First, set up the notebook server configuration to handle the login URL.
        See the README for more information.

        Then, create an instance of the button with the desired domain.
        ```python
        from salesforce_login_button import SalesforceLoginButton

        login_url = '/login'  # This should match your server config
        button = SalesforceLoginButton(domain='login', login_url=login_url)
        button
        ```

        When the button is clicked, it will redirect to the Salesforce login page
        in a popup. You can react to the `.connected` value.

        ```python
        from simple_salesforce import Salesforce
        assert button.connected
        sf: Salesforce = button.salesforce_client()
        ```
    """
    def __init__(self, domain: str, login_url: str = '/login', **kwargs):
        """
        Build a new SalesforceLoginButton widget.
        :param domain: The Salesforce domain to use for login. E.g. 'login' or
          'test'.
        :param login_url: The URL to redirect to for login, defaults to '/login'.
          This must be set up in the notebook server configuration to handle.
          Read the docs for more information.
        :param kwargs: Additional keyword arguments to pass to the parent class.
        """
        super().__init__(**kwargs)
        self.domain = traitlets.Unicode(domain).tag(sync=True)
        self.login_url = traitlets.Unicode(login_url).tag(sync=True)
        self.connected = traitlets.Bool(False).tag(sync=True)
        self.token: OAuthToken = traitlets.Dict().tag(sync=True)

    # _esm = Path(__file__).parent / 'static/index.js'
    _esm = Path(__file__).parent / 'static' / 'index.js'
    _css = Path(__file__).parent / 'static' / 'index.css'

    # True if connected, otherwise False

    def salesforce_client(self):
        """
        Returns a `simple_salesforce.Salesforce` client instance
        using the access token and instance URL from the token.
        """
        if not self.connected:
            raise ValueError("Not connected to Salesforce. Please log in first.")
        return Salesforce(
            instance_url=self.token['instance_url'],
            session_id=self.token['access_token']
        )