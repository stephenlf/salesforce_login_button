from typing import Annotated, Callable, Coroutine
from fastapi.responses import HTMLResponse, RedirectResponse
import marimo
from fastapi import FastAPI, Form, Request, Response
from pathlib import Path

print(__name__)

# Create a marimo asgi app
server = (
    marimo.create_asgi_app()
    .with_app(path="", root=Path(__name__).parent / "notebooks" / "demo.py")
)

# Create a FastAPI app
app = FastAPI()

app.mount("/", server.build())

# Run the server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)