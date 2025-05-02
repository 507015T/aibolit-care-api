generate-openapi:
	mkdir -p openapi/generated/schemas
	uv run datamodel-codegen \
		--input openapi/openapi.json \
		--output-model-type pydantic_v2.BaseModel \
		--output openapi/generated/schemas/medication_schedule.py

generate-grpc:
	touch grpc_server/__init__.py
	uv run python -m grpc_tools.protoc \
	-I ./grpc_server/protos --python_out=./grpc_server \
	--grpc_python_out=./grpc_server ./grpc_server/protos/medications.proto
