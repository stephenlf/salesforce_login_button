Clone the repo and sync
```bash
git clone git@github.com:stephenlf/salesforce_login_button.git
cd salesforce_login_button
uv sync
source .venv/bin/activate
```

Next, set up your environment. You will need to configure an external app in your Salesforce org. Read .env-template for more information.
```bash
cp .env-template .env
vi .env     # Now edit .env with your environment variables
```

Start your callback server
```bash
uvicorn demo.callback:app --host localhost --port 5000
```

Start your edit server
```bash
marimo edit demo/notebooks/demo.py
```