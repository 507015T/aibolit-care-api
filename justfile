# Directories for source code and tests
SOURCE_DIR := "src/aibolit/"
TESTS_DIR := "tests"

# Default command: list available commands
default:
    @just --list

# Environment variables file
set dotenv-filename := ".env"

# Run all checks: linters and formatting validation
lint: ruff-check format-check

# --- Dependency Management ---

# Update project dependencies
[group('dependencies')]
update:
    uv sync --upgrade

# --- Linters and Formatting ---

# Automatically format code
[group('linters')]
format:
    uv run ruff format .

# Check formatting without modifying files
[group('linters')]
format-check:
    uv run ruff format .

# Lint code using Ruff
[group('linters')]
ruff-check:
    uv run ruff check {{ SOURCE_DIR }}
    uv run ruff check {{ TESTS_DIR }}

# Fix code using Ruff
[group('linters')]
ruff:
    uv run ruff check --fix --unsafe-fixes {{ SOURCE_DIR }}
    uv run ruff check --fix --unsafe-fixes {{ TESTS_DIR }}

# --- Testing ---

# Run tests using pytest
[group('testing')]
tests:
    uv run pytest .


# --- Building ---

# Build DataBase
[group('building')]
build-depends:
    docker compose -f .docker/docker-compose-local.yml up -d --remove-orphans --build

# --- Generate-code ---

[group('openapi')]
generate-openapi:
    cd docs/scripts/ && uv run convert_script.py && cd ../..
    mkdir -p src/aibolit/schemas/openapi_generated
    touch src/aibolit/schemas/openapi_generated/__init__.py
    uv run datamodel-codegen \
        --input docs/scripts/openapi.json \
        --input-file-type openapi \
        --output-model-type pydantic_v2.BaseModel \
        --output src/aibolit/schemas/openapi_generated/schemas.py

[group('grpc')]
generate-grpc:
	uv run -m grpc_tools.protoc \
		-Iaibolit/transport/grpc/generated=src/aibolit/transport/grpc/protos \
		--python_out=src --grpc_python_out=src \
		src/aibolit/transport/grpc/protos/schedule.proto
	uv run -m grpc_tools.protoc \
		-Iaibolit/transport/grpc/generated=src/aibolit/transport/grpc/protos \
		--python_out=src --grpc_python_out=src \
		src/aibolit/transport/grpc/protos/user.proto
