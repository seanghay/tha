build:
	rm -rf dist/
	uv build

upload:
	uv publish

test:
	uv run python tests.py

lint:
	uv run ruff check tha tests.py
	uv run ruff format --check tha tests.py
