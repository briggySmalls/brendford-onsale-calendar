.PHONY: check fix test

check:
	uv run pre-commit run --all-files

fix:
	uv run ruff check --fix

test:
	uv run pytest -vv
