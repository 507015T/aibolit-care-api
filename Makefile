generate-openapi:
	mkdir -p src/aibolit/schemas/openapi_generated; touch src/aibolit/schemas/openapi_generated/__init__.py
	uv run datamodel-codegen \
		--input docs/scripts/openapi.json \
		--input-file-type openapi \
		--output-model-type pydantic_v2.BaseModel \
		--output src/aibolit/schemas/openapi_generated/schemas.py
generate-grpc:
	uv run python -m grpc_tools.protoc \
		-Iaibolit/transport/grpc/generated=src/aibolit/transport/grpc/protos \
		--python_out=src --grpc_python_out=src \
		src/aibolit/transport/grpc/protos/schedule.proto
	uv run python -m grpc_tools.protoc \
		-Iaibolit/transport/grpc/generated=src/aibolit/transport/grpc/protos \
		--python_out=src --grpc_python_out=src \
		src/aibolit/transport/grpc/protos/user.proto
