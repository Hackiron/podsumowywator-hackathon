.PHONY: run format

run:
	poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

format:
	poetry run ruff format . 