import os
import json
from jsonschema import validate, ValidationError
from jinja2 import Environment, FileSystemLoader

# Adjust these paths if your folder names differ
SCHEMA_DIR   = os.path.join(os.path.dirname(__file__), "../schemas")
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../templates")

# Set up Jinja
env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    trim_blocks=True,
    lstrip_blocks=True
)

def load_and_render(purpose: str, data: dict) -> str:
    # Load schema
    schema_path = os.path.join(SCHEMA_DIR, f"{purpose}.schema.json")
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)

    # Validate inputs
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        raise ValueError(f"Invalid prompt data for {purpose}: {e.message}")

    # Render template
    template = env.get_template(f"{purpose}.j2")
    return template.render(**data)
