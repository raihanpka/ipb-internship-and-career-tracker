.PHONY: up down start-local test coverage

up:
	docker compose up -d --remove-orphans

down:
	docker compose down --remove-orphans

start-local:
	poetry run uvicorn app_backend.main:app --reload

load-fixtures:
	poetry run python -m app_backend.scripts.load_fixtures

test:
ifdef filter
	poetry run pytest $(filter) -vv
else
	poetry run pytest -vv
endif

coverage: test
	poetry run pytest --cov-report term-missing --cov=app_backend

install:
	poetry install

dev:
	poetry install --with dev
