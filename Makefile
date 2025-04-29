.PHONY: lint format test build clean

# Lint with ruff
lint:
	uvx ruff check -- src/

# Format with black
format:
	uvx black -- src/ tests/

# Run tests with pytest
test:
	uv run pytest --cov=salesforce_login_button --cov-report=term tests/

test.local:
	uv run pytest --cov=salesforce_login_button --cov-report=html tests/
	python3 -c 'import webbrowser; from pathlib import Path; webbrowser.open(str(Path().parent.resolve() / "htmlcov" / "index.html"))'

# Clean build artifacts
clean:
	rm -rf dist/ build/ *.egg-info
