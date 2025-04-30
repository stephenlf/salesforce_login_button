import dotenv
import os
dotenv.load_dotenv('.env')

from salesforce_login_button.server import create_callback_server

app = create_callback_server(
    os.environ.get('SF_OAUTH_CLIENT_ID'),
    os.environ.get('SF_OAUTH_CLIENT_SECRET')
)