.PHONY: install format lint test build clean

install:
	poetry install

format:
	poetry run ruff format .
	poetry run ruff check . --fix --unsafe-fixes

lint:
	poetry run ruff check .
	poetry run mypy .

test:
	poetry run pytest

build-pyinstaller:
	poetry run pyinstaller --name upg \
		--onefile \
		--collect-data upg \
		--hidden-import=click \
		--hidden-import=pydantic \
		src/upg/cli/commands.py

build: clean install lint test build-pyinstaller

clean:
	rm -rf build dist *.spec
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

publish:
	poetry build
	poetry publish