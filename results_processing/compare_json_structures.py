#!/usr/bin/env python3
"""
Compare JSON structure between ground truth and model output files.
"""

import json
import os
from pathlib import Path
from collections import defaultdict

def get_all_fields(json_obj, prefix=''):
    """Recursively extract all fields from a JSON object."""
    fields = set()

    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            current_field = f"{prefix}.{key}" if prefix else key
            fields.add(current_field)

            if isinstance(value, (dict, list)):
                fields.update(get_all_fields(value, current_field))

    elif isinstance(json_obj, list) and len(json_obj) > 0:
        # For arrays, analyze the first item to get structure
        fields.update(get_all_fields(json_obj[0], prefix))

    return fields

def analyze_json_structure(file_path):
    """Analyze the structure of a JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        fields = get_all_fields(data)
        return fields, data
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return set(), {}

def compare_structures():
    """Compare structures between ground truth and model output files."""

    gt_dir = Path("cleaned_results/cleaned_ground_truth")
    model_dir = Path("cleaned_results/gpt41")  # Use one model as representative

    print("=== JSON Structure Comparison ===\n")

    # Find a common cell line in both directories
    gt_files = list(gt_dir.glob("AIBNi001-A*.json"))
    model_files = list(model_dir.glob("AIBNi001-A.json"))

    if not gt_files or not model_files:
        print("Could not find matching AIBNi001-A files in both directories")
        return

    gt_file = gt_files[0]
    model_file = model_files[0]

    print(f"Comparing:")
    print(f"  Ground Truth: {gt_file}")
    print(f"  Model Output: {model_file}")
    print()

    # Analyze structures
    gt_fields, gt_data = analyze_json_structure(gt_file)
    model_fields, model_data = analyze_json_structure(model_file)

    print(f"Ground Truth fields: {len(gt_fields)}")
    print(f"Model Output fields: {len(model_fields)}")
    print()

    # Find differences
    gt_only = gt_fields - model_fields
    model_only = model_fields - gt_fields
    common = gt_fields & model_fields

    print(f"Common fields: {len(common)}")
    print(f"Ground Truth only: {len(gt_only)}")
    print(f"Model Output only: {len(model_only)}")
    print()

    if gt_only:
        print("Fields only in Ground Truth:")
        for field in sorted(gt_only):
            print(f"  - {field}")
        print()

    if model_only:
        print("Fields only in Model Output:")
        for field in sorted(model_only):
            print(f"  - {field}")
        print()

    # Compare top-level sections
    print("=== Top-level Section Comparison ===")
    gt_sections = set(key for key in gt_data.keys() if not key.startswith('_'))
    model_sections = set(key for key in model_data.keys() if not key.startswith('_'))

    print(f"Ground Truth sections: {sorted(gt_sections)}")
    print(f"Model Output sections: {sorted(model_sections)}")
    print()

    gt_sections_only = gt_sections - model_sections
    model_sections_only = model_sections - gt_sections
    common_sections = gt_sections & model_sections

    print(f"Common sections: {sorted(common_sections)}")
    if gt_sections_only:
        print(f"Ground Truth only sections: {sorted(gt_sections_only)}")
    if model_sections_only:
        print(f"Model Output only sections: {sorted(model_sections_only)}")
    print()

    # Sample field value comparison for common sections
    print("=== Sample Field Value Comparison ===")
    for section in sorted(common_sections):
        if section in gt_data and section in model_data:
            print(f"\n{section} section:")
            gt_section = gt_data[section]
            model_section = model_data[section]

            if isinstance(gt_section, dict) and isinstance(model_section, list):
                print(f"  Structure difference: GT=dict, Model=list")
                if model_section:
                    print(f"  GT keys: {list(gt_section.keys())}")
                    print(f"  Model keys (first item): {list(model_section[0].keys()) if isinstance(model_section[0], dict) else 'Not a dict'}")
            elif isinstance(gt_section, list) and isinstance(model_section, dict):
                print(f"  Structure difference: GT=list, Model=dict")
                if gt_section:
                    print(f"  GT keys (first item): {list(gt_section[0].keys()) if isinstance(gt_section[0], dict) else 'Not a dict'}")
                    print(f"  Model keys: {list(model_section.keys())}")
            elif isinstance(gt_section, dict) and isinstance(model_section, dict):
                gt_keys = set(gt_section.keys())
                model_keys = set(model_section.keys())
                if gt_keys != model_keys:
                    print(f"  Key differences:")
                    print(f"    GT only: {gt_keys - model_keys}")
                    print(f"    Model only: {model_keys - gt_keys}")
                else:
                    print(f"  Keys match: {sorted(gt_keys)}")

if __name__ == "__main__":
    compare_structures()