MAIN_MODULE = src.app.main

install:
	@echo "Installing dependencies..."
	uv sync

run:
	@echo "Running the application..."
	uv run python -m $(MAIN_MODULE)

debug:
	@echo "Running the application in debug mode..."
	uv run python -m pdb -m $(MAIN_MODULE)

lint:
	@echo "Running linters..."
	uv run ruff check src

lint-strict:
	@echo "Running strict linters..."
	uv run ruff check src

clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

.PHONY: install run debug lint lint-strict clean test