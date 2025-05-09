generate-openapi:
	mkdir -p openapi/generated/schemas
	uv run datamodel-codegen \
		--input openapi/openapi.json \
		--output-model-type pydantic_v2.BaseModel \
		--output src/aibolit/openapi/generated/schemas/medication_schedule.py
generate-grpc:
	uv run python -m grpc_tools.protoc \
		-Iaibolit/transport/grpc/generated=src/aibolit/transport/grpc/protos \
		--python_out=src --grpc_python_out=src \
		src/aibolit/transport/grpc/protos/schedule.proto
	uv run python -m grpc_tools.protoc \
		-Iaibolit/transport/grpc/generated=src/aibolit/transport/grpc/protos \
		--python_out=src --grpc_python_out=src \
		src/aibolit/transport/grpc/protos/user.proto
