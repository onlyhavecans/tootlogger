# List available recipes
default:
    @just --list

# Remove all build, test, coverage and Python artifacts
clean: clean-build clean-pyc clean-test

# Remove build artifacts
clean-build:
    rm -fr build/
    rm -fr dist/
    rm -fr .eggs/
    find . -name '*.egg-info' -exec rm -fr {} +
    find . -name '*.egg' -exec rm -f {} +

# Remove Python file artifacts
clean-pyc:
    find . -name '*.pyc' -exec rm -f {} +
    find . -name '*.pyo' -exec rm -f {} +
    find . -name '*~' -exec rm -f {} +
    find . -name '__pycache__' -exec rm -fr {} +

# Remove test and coverage artifacts
clean-test:
    rm -fr .tox/
    rm -f .coverage
    rm -fr htmlcov/
    rm -fr .pytest_cache
    rm -fr .ruff_cache

# Build distribution
build: clean
    uv build
    ls -l dist

# Upload to PyPI
upload: build
    uv publish

# Run linter
lint:
    uv run ruff check .

# Run formatter check
format-check:
    uv run ruff format --check .

# Format code
format:
    uv run ruff format .

# Fix linting issues
fix:
    uv run ruff check --fix .
