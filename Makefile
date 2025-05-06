generate-openapi:
	mkdir -p openapi/generated/schemas
	uv run datamodel-codegen \
		--input openapi/openapi.json \
		--output-model-type pydantic_v2.BaseModel \
		--output src/aibolit/openapi/generated/schemas/medication_schedule.py
generate-grpc:
	uv run python -m grpc_tools.protoc \
	-I ./src/aibolit/grpc_service/proto --python_out=./src/aibolit/grpc_service/generated/ \
	--grpc_python_out=./src/aibolit/grpc_service/generated/ \
	./src/aibolit/grpc_service/proto/schedule.proto
	uv run python -m grpc_tools.protoc \
	-I ./src/aibolit/grpc_service/proto --python_out=./src/aibolit/grpc_service/generated/ \
	--grpc_python_out=./src/aibolit/grpc_service/generated/ \
	./src/aibolit/grpc_service/proto/user.proto
