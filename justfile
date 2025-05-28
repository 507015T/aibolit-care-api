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

# Run all tests
[group('testing')]
tests:
    uv run pytest .

# Run E2E tests for gRPC
[group('testing')]
test-grpc:
    uv run pytest tests/grpc/ -s -v

# Run E2E tests for REST API
[group('testing')]
test-api:
    uv run pytest tests/users/test_views.py -s -v
    uv run pytest tests/schedules/test_views.py -s -v

# Run unit tests for plan generation, time rounding, timeframe check
[group('testing')]
test-utils:
    uv run pytest tests/schedules/test_services_utils.py -s -v

# Run all tests and calculate coverage
[group('testing')]
test-all-coverage:
    uv run pytest --cov=src

# --- Docker-database ---

# Build and run database
[group('database')]
db-start:
    docker compose up -d db --build

# Run database
[group('database')]
db:
    docker compose up -d db

# Stop database
[group('database')]
db-stop:
    docker compose down

# Stop and clear database
[group('database')]
db-clear:
    docker compose down -v db

# --- Full App in Docker ---

# Start app in Docker
[group('start')]
start:
    docker compose up --build

# Stop app in Docker
[group('start')]
stop:
    docker compose down

# Stop and clear app container in Docker
[group('start')]
stop-clear:
    docker compose down -v

# --- Locally start app ---

# Start app locally(only REST)
[group('app')]
api:
    uv run uvicorn src.aibolit.main:make_app --factory

# Start app locally(only gRPC)
[group('app')]
grpc:
    uv run src/aibolit/transport/grpc/grpc_client.py

# Start app locally(gRPC + REST)
[group('app')]
app:
    ./src/aibolit/main.py

# --- Generate-code ---

# Generate pydantic schemas from openapi
[group('generating')]
generate-openapi:
    cd docs/openapi/ && uv run convert_script.py && cd ../..
    uv run datamodel-codegen \
        --input docs/openapi/openapi.json \
        --input-file-type openapi \
        --output-model-type pydantic_v2.BaseModel \
        --output src/aibolit/schemas/openapi_generated.py

# Generate Python code from .proto files for gRPC
[group('generating')]
generate-grpc:
    mkdir -p src/aibolit/grpc/generated
    touch src/aibolit/grpc/generated/__init__.py
    uv run -m grpc_tools.protoc \
        -Iaibolit/grpc/generated=src/aibolit/grpc/protos \
        --python_out=src --grpc_python_out=src \
        src/aibolit/grpc/protos/schedules.proto
    uv run -m grpc_tools.protoc \
        -Iaibolit/grpc/generated=src/aibolit/grpc/protos \
        --python_out=src --grpc_python_out=src \
        src/aibolit/grpc/protos/users.proto
