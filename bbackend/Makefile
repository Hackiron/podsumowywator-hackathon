.PHONY: run format test

run:
	poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

format:
	poetry run ruff format .

dev:
	watchexec -w . "make run"

test:
	poetry run pytest -v

test-watch:
	poetry run ptw