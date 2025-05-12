#!/usr/bin/env -S uv run --script
import json
import yaml
import requests

url = "http://127.0.0.1:8000/openapi.json"

response = requests.get(url)
openapi_json = response.json()

with open("openapi.json", "w") as j:
    json.dump(openapi_json, j, indent=2)
with open("openapi.yaml", "w") as y:
    yaml.dump(openapi_json, y, indent=2)

print("Done!")
