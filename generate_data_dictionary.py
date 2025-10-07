#!/usr/bin/env python3
"""
Script to generate markdown documentation from Pydantic models in automated_curation_schema.py
Creates a business-facing data dictionary with tabular views and support for nested models.
"""

import inspect
import sys
from typing import get_origin, get_args, Union
from pathlib import Path
import importlib.util

def load_schema_module():
    """Load the automated_curation_schema.py module dynamically"""
    spec = importlib.util.spec_from_file_location("automated_curation_schema", "automated_curation_schema.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def format_type_annotation(annotation):
    """Format type annotations for business-friendly display"""
    if hasattr(annotation, '__name__'):
        return annotation.__name__

    # Handle Union types (e.g., str | int)
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is Union:
        # Handle Optional types (Union[X, None])
        if len(args) == 2 and type(None) in args:
            non_none_type = args[0] if args[1] is type(None) else args[1]
            return f"Optional[{format_type_annotation(non_none_type)}]"
        else:
            return " | ".join(format_type_annotation(arg) for arg in args)

    if origin is list:
        return f"List[{format_type_annotation(args[0])}]"

    # Handle Literal types - just return the base type for the Type column
    if hasattr(annotation, '__origin__') and str(annotation.__origin__) == 'typing.Literal':
        return "Literal"

    return str(annotation).replace('typing.', '')

def extract_literal_values(annotation):
    """Extract literal values from type annotations"""
    # Handle Union types that might contain literals
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is Union:
        # Handle Optional types (Union[X, None])
        if len(args) == 2 and type(None) in args:
            non_none_type = args[0] if args[1] is type(None) else args[1]
            return extract_literal_values(non_none_type)
        else:
            # Check if any of the union args are literals
            for arg in args:
                literal_vals = extract_literal_values(arg)
                if literal_vals:
                    return literal_vals
            return ""

    if origin is list and len(args) > 0:
        # Check if list contains literals
        return extract_literal_values(args[0])

    # Handle Literal types
    if hasattr(annotation, '__origin__') and str(annotation.__origin__) == 'typing.Literal':
        values = []
        for val in annotation.__args__:
            if isinstance(val, str):
                values.append(f"'{val}'")
            else:
                values.append(str(val))
        return ", ".join(values)

    return ""

def get_field_info(field_name, field_info, model_fields):
    """Extract field information including type, required status, and description"""
    field_type = format_type_annotation(field_info.annotation)

    # Check if field is required
    is_required = field_info.default is ... or (hasattr(field_info, 'is_required') and field_info.is_required())
    required_status = "Required" if is_required else "Optional"

    # Get default value if it exists
    default_value = ""
    if field_info.default is not ... and field_info.default is not None:
        default_value = str(field_info.default)

    # Extract literal values
    accepted_values = extract_literal_values(field_info.annotation)

    return {
        'name': field_name,
        'type': field_type,
        'required': required_status,
        'default': default_value,
        'description': field_info.description or "",
        'accepted_values': accepted_values
    }

def is_nested_model(field_info, schema_models):
    """Check if a field references another model in our schema"""
    annotation = field_info.annotation

    # Handle direct model references
    if hasattr(annotation, '__name__') and annotation.__name__ in schema_models:
        return annotation.__name__

    # Handle Optional[Model] and List[Model]
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is Union and len(args) == 2 and type(None) in args:
        # Optional type
        non_none_type = args[0] if args[1] is type(None) else args[1]
        if hasattr(non_none_type, '__name__') and non_none_type.__name__ in schema_models:
            return non_none_type.__name__

    if origin is list and len(args) > 0:
        # List type
        if hasattr(args[0], '__name__') and args[0].__name__ in schema_models:
            return args[0].__name__

    return None

def generate_model_table(model_class, schema_models):
    """Generate a markdown table for a single model"""
    model_name = model_class.__name__
    fields = model_class.model_fields

    # Table header
    table = f"### {model_name}\n\n"
    table += "| Field Name | Type | Required | Accepted Values | Default | Description | Nested Model |\n"
    table += "|------------|------|----------|----------------|---------|-------------|-------------|\n"

    # Table rows
    for field_name, field_info in fields.items():
        field_data = get_field_info(field_name, field_info, fields)
        nested_model = is_nested_model(field_info, schema_models)
        nested_ref = f"[{nested_model}](#{nested_model.lower()})" if nested_model else ""

        table += f"| {field_data['name']} | {field_data['type']} | {field_data['required']} | {field_data['accepted_values']} | {field_data['default']} | {field_data['description']} | {nested_ref} |\n"

    return table + "\n"

def generate_toc(models):
    """Generate table of contents"""
    toc = "## Table of Contents\n\n"
    for model in models:
        model_name = model.__name__
        toc += f"- [{model_name}](#{model_name.lower()})\n"
    return toc + "\n"

def generate_markdown_documentation():
    """Generate complete markdown documentation"""
    # Load the schema module
    try:
        schema_module = load_schema_module()
    except Exception as e:
        print(f"Error loading automated_curation_schema.py: {e}")
        return

    # Get all Pydantic models from the module
    models = []
    schema_model_names = set()

    for name, obj in inspect.getmembers(schema_module):
        if (inspect.isclass(obj) and
            hasattr(obj, 'model_fields') and
            obj.__module__ == schema_module.__name__):
            models.append(obj)
            schema_model_names.add(name)

    # Sort models alphabetically
    models.sort(key=lambda x: x.__name__)

    # Generate markdown content
    markdown_content = """# Australian Stem Cell Registry - Data Dictionary

This document provides a comprehensive overview of the data models used in the Australian Stem Cell Registry curation system. Each model represents a specific entity or concept within the registry, with detailed field specifications for data validation and processing.

"""

    # Add table of contents
    markdown_content += generate_toc(models)

    # Add overview section
    markdown_content += """## Overview

The data dictionary below describes the structure and requirements for each data model. The models are interconnected through relationships indicated in the "Nested Model" column.

**Field Types:**
- **Required**: Field must be provided
- **Optional**: Field is not required
- **Literal Values**: Field must be one of the specified values
- **List**: Field accepts multiple values of the specified type

---

"""

    # Generate tables for each model
    for model in models:
        markdown_content += generate_model_table(model, schema_model_names)

    # Add footer
    markdown_content += """---

## Notes

1. **Nested Models**: Some fields reference other models in this schema. Click the linked model name to navigate to its definition.
2. **Literal Types**: Fields with "One of:" constraints must use exactly one of the specified values.
3. **Optional Fields**: Fields marked as "Optional" can be omitted from the data.
4. **Foreign Keys**: Some fields (like `additional_genomic_characteristation`, `loci`) reference IDs from other models.

Generated from `automated_curation_schema.py`
"""

    # Write to file
    output_path = Path("data_dictionary.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"✅ Data dictionary generated successfully: {output_path.absolute()}")
    print(f"📊 Documented {len(models)} models")

if __name__ == "__main__":
    generate_markdown_documentation()