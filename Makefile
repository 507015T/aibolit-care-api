generate-openapi:
	mkdir -p openapi/generated/schemas
	uv run datamodel-codegen \
		--input openapi/openapi.json \
		--output-model-type pydantic_v2.BaseModel \
		--output openapi/generated/schemas/medication_schedule.py
