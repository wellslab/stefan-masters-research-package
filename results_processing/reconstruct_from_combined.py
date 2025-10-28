#!/usr/bin/env python3
"""
Reconstruct JSONs from Combined All-Models DataFrame

This script takes the harmonized combined DataFrame (from generate_all_models_dataframe.py)
and reconstructs both ground truth and model output JSON files from the cleaned/harmonized data.

Usage:
    python reconstruct_from_combined.py [--config config_reconstruct_combined.json]

The script will:
1. Load the harmonized combined DataFrame
2. Separate by data_source and model_name
3. Reconstruct JSON files from the flattened columns using _original_json as template
4. Save to organized folders: ground_truth/ and model_output/[model_name]/
5. Preserve proper naming conventions

Important: Uses harmonized flattened columns, not original JSON strings.
"""

import json
import pandas as pd
import argparse
from pathlib import Path
from typing import Dict, List, Any
import sys

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Config file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in config file: {e}")
        sys.exit(1)

def get_section_fields_from_df(df: pd.DataFrame) -> Dict[str, set]:
    """
    Extract all possible fields by section from DataFrame columns.
    Works with dot notation flattened columns like 'basic_data.name', 'contact.first_name', etc.
    """
    all_sections = {}

    # Find all columns with dot notation (section.field)
    for col in df.columns:
        if '.' in col and not col.startswith('_'):
            section_name, field_name = col.split('.', 1)

            if section_name not in all_sections:
                all_sections[section_name] = set()

            all_sections[section_name].add(field_name)

    return all_sections

def reconstruct_json_from_row(row: pd.Series, all_possible_fields: Dict[str, set]) -> Dict[str, Any]:
    """
    Reconstruct JSON from harmonized flattened columns using the original JSON as a structure template.
    """
    # Start with original JSON structure as template
    if '_original_json' in row and pd.notna(row['_original_json']):
        try:
            original_structure = json.loads(row['_original_json'])
        except json.JSONDecodeError:
            original_structure = {}
    else:
        original_structure = {}

    reconstructed = {}

    # Reconstruct each section
    for section_name, fields in all_possible_fields.items():
        section_data = None

        # Check if this section exists in original structure to maintain type
        if section_name in original_structure:
            original_section = original_structure[section_name]

            if isinstance(original_section, list):
                # Handle array sections
                section_data = []

                # Find all values for this section
                section_values = {}
                for field_name in fields:
                    col_name = f"{section_name}.{field_name}"
                    if col_name in row and pd.notna(row[col_name]):
                        value = row[col_name]
                        if value not in ["None", "Missing", ""]:
                            section_values[field_name] = str(value)

                # If we have values, create array items
                if section_values:
                    # Check if any field has multiple values (separated by " | ")
                    max_items = 1
                    for field_name, value in section_values.items():
                        if " | " in value:
                            max_items = max(max_items, len(value.split(" | ")))

                    # Create items for the array
                    for item_idx in range(max_items):
                        item = {}
                        for field_name, value in section_values.items():
                            if " | " in value:
                                # Split by separator and take appropriate item
                                parts = value.split(" | ")
                                if item_idx < len(parts) and parts[item_idx].strip():
                                    item[field_name] = parts[item_idx].strip()
                            else:
                                # Single value - only add to first item
                                if item_idx == 0:
                                    item[field_name] = value

                        if item:  # Only add non-empty items
                            section_data.append(item)

            elif isinstance(original_section, dict):
                # Handle object sections
                section_data = {}

                # Populate with harmonized values
                for field_name in fields:
                    col_name = f"{section_name}.{field_name}"
                    if col_name in row and pd.notna(row[col_name]):
                        value = row[col_name]
                        if value not in ["None", "Missing", ""]:
                            section_data[field_name] = str(value)
        else:
            # Section doesn't exist in original - create based on data
            section_values = {}
            for field_name in fields:
                col_name = f"{section_name}.{field_name}"
                if col_name in row and pd.notna(row[col_name]):
                    value = row[col_name]
                    if value not in ["None", "Missing", ""]:
                        section_values[field_name] = str(value)

            if section_values:
                # Default to object structure for new sections
                section_data = section_values

        # Add section to reconstructed JSON if it has data
        if section_data is not None:
            if isinstance(section_data, list) and section_data:
                reconstructed[section_name] = section_data
            elif isinstance(section_data, dict) and section_data:
                reconstructed[section_name] = section_data

    return reconstructed

def reconstruct_json_from_grouped_rows(group_rows: pd.DataFrame, all_possible_fields: Dict[str, set]) -> Dict[str, Any]:
    """
    Intelligently reconstruct JSON from multiple rows representing the same cell line.

    For each section:
    - Collect all unique combinations of field values across rows
    - If all rows have identical values -> create single array item
    - If rows have different values -> create multiple array items for distinct combinations
    - Always create arrays (even single-item) to maintain consistent structure
    """
    reconstructed = {}

    # Process each section
    for section_name, fields in all_possible_fields.items():
        # Collect all field combinations for this section across all rows
        section_items = []

        for idx, row in group_rows.iterrows():
            item = {}
            has_data = False

            # Extract all fields for this section from current row
            for field_name in fields:
                col_name = f"{section_name}.{field_name}"
                if col_name in row and pd.notna(row[col_name]):
                    value = str(row[col_name]).strip()
                    if value not in ["None", "Missing", ""]:
                        item[field_name] = value
                        has_data = True

            # Only add items that have at least one valid field
            if has_data:
                section_items.append(item)

        # Remove exact duplicates while preserving order
        unique_items = []
        seen = set()
        for item in section_items:
            # Create a hashable representation for duplicate detection
            item_key = tuple(sorted(item.items()))
            if item_key not in seen:
                seen.add(item_key)
                unique_items.append(item)

        # Add section to reconstructed JSON if it has data
        if unique_items:
            reconstructed[section_name] = unique_items

    return reconstructed

def reconstruct_ground_truth(df: pd.DataFrame, output_dir: Path, all_possible_fields: Dict[str, set], verbose: bool = True) -> int:
    """
    Reconstruct ground truth JSON files from DataFrame, grouping by cell line.
    """
    gt_dir = output_dir / "ground_truth"
    gt_dir.mkdir(parents=True, exist_ok=True)

    # Filter to ground truth rows
    gt_rows = df[df['data_source'] == 'ground_truth']

    if verbose:
        print(f"  Reconstructing from {len(gt_rows)} ground truth rows...")

    # Group by hpscreg_base to combine multiple rows per cell line
    grouped = gt_rows.groupby('hpscreg_base')

    if verbose:
        print(f"  Creating {len(grouped)} ground truth JSON files...")

    files_created = 0
    for hpscreg_base, group_rows in grouped:
        try:
            # Reconstruct JSON from all rows for this cell line
            reconstructed_json = reconstruct_json_from_grouped_rows(group_rows, all_possible_fields)

            # Create filename
            filename = f"{hpscreg_base}_gt.json"
            output_path = gt_dir / filename

            # Save JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(reconstructed_json, f, indent=2)

            files_created += 1

        except Exception as e:
            if verbose:
                print(f"    ERROR: Could not reconstruct {hpscreg_base}: {e}")

    if verbose:
        print(f"    ✓ Created {files_created} ground truth JSON files in {gt_dir}")

    return files_created

def reconstruct_model_outputs(df: pd.DataFrame, output_dir: Path, all_possible_fields: Dict[str, set], verbose: bool = True) -> int:
    """
    Reconstruct model output JSON files from DataFrame, organized by model and grouped by cell line.
    """
    # Filter to model output rows
    model_rows = df[df['data_source'] == 'model_output']

    if verbose:
        print(f"  Reconstructing from {len(model_rows)} model output rows...")

    total_files_created = 0

    # Group by model_name first
    for model_name in model_rows['model_name'].unique():
        model_specific_rows = model_rows[model_rows['model_name'] == model_name]

        # Create model-specific directory
        model_dir = output_dir / "model_output" / model_name
        model_dir.mkdir(parents=True, exist_ok=True)

        # Group by hpscreg_base within this model
        grouped = model_specific_rows.groupby('hpscreg_base')

        if verbose:
            print(f"    Processing {model_name}: {len(model_specific_rows)} rows → {len(grouped)} files")

        files_created = 0
        for hpscreg_base, group_rows in grouped:
            try:
                # Reconstruct JSON from all rows for this cell line
                reconstructed_json = reconstruct_json_from_grouped_rows(group_rows, all_possible_fields)

                # Create filename
                filename = f"{hpscreg_base}_m.json"
                output_path = model_dir / filename

                # Save JSON file
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(reconstructed_json, f, indent=2)

                files_created += 1

            except Exception as e:
                if verbose:
                    print(f"      ERROR: Could not reconstruct {hpscreg_base}: {e}")

        if verbose:
            print(f"      ✓ Created {files_created} files in {model_dir}")

        total_files_created += files_created

    return total_files_created

def main():
    parser = argparse.ArgumentParser(description='Reconstruct JSON files from combined harmonized DataFrame')
    parser.add_argument('--config', default='config_reconstruct_combined.json',
                       help='Path to configuration file')
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Set up paths
    dataframe_path = Path(config['dataframe_path'])
    output_dir = Path(config['output_path'])
    overwrite_existing = config.get('overwrite_existing', True)
    verbose = config.get('verbose', True)

    if verbose:
        print("🔧 Reconstruct JSONs from Combined DataFrame")
        print("=" * 45)
        print(f"Input DataFrame: {dataframe_path}")
        print(f"Output directory: {output_dir}")
        print(f"Overwrite existing: {overwrite_existing}")

    # Load DataFrame
    if verbose:
        print(f"\n📂 Loading DataFrame...")

    if not dataframe_path.exists():
        print(f"ERROR: DataFrame file not found: {dataframe_path}")
        sys.exit(1)

    df = pd.read_csv(dataframe_path)

    if verbose:
        print(f"Loaded DataFrame: {df.shape}")
        print(f"Data sources: {df['data_source'].value_counts().to_dict()}")
        if 'model_name' in df.columns:
            print(f"Models: {sorted(df['model_name'].unique())}")

    # Create output directory
    if output_dir.exists() and not overwrite_existing:
        print(f"ERROR: Output directory exists and overwrite_existing=False: {output_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Analyze fields
    if verbose:
        print(f"\n🔍 Analyzing fields...")

    all_possible_fields = get_section_fields_from_df(df)

    if verbose:
        total_fields = sum(len(fields) for fields in all_possible_fields.values())
        print(f"Field analysis complete:")
        for section, fields in all_possible_fields.items():
            print(f"  {section}: {len(fields)} fields")
        print(f"Total unique fields: {total_fields}")

    # Reconstruct files
    if verbose:
        print(f"\n🔨 Reconstructing JSON files...")

    # Reconstruct ground truth
    gt_files_created = reconstruct_ground_truth(df, output_dir, all_possible_fields, verbose)

    # Reconstruct model outputs
    model_files_created = reconstruct_model_outputs(df, output_dir, all_possible_fields, verbose)

    # Save metadata
    metadata = {
        'source_dataframe': str(dataframe_path),
        'output_directory': str(output_dir),
        'total_input_rows': len(df),
        'ground_truth_files_created': gt_files_created,
        'model_output_files_created': model_files_created,
        'total_files_created': gt_files_created + model_files_created,
        'sections_and_fields': {k: len(v) for k, v in all_possible_fields.items()},
        'models_processed': sorted(df[df['data_source'] == 'model_output']['model_name'].unique().tolist()) if 'model_name' in df.columns else [],
        'config_used': config
    }

    metadata_path = output_dir / "reconstruction_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    if verbose:
        print(f"\n🎉 RECONSTRUCTION COMPLETE!")
        print(f"📊 Files created: {gt_files_created + model_files_created}")
        print(f"  Ground truth: {gt_files_created}")
        print(f"  Model outputs: {model_files_created}")
        print(f"📁 Output directory: {output_dir}")
        print(f"📋 Metadata saved: {metadata_path}")

        print(f"\nDirectory structure:")
        print(f"  {output_dir}/")
        print(f"  ├── ground_truth/          # {gt_files_created} files")
        print(f"  ├── model_output/")
        for model in metadata['models_processed']:
            model_count = len(df[(df['data_source'] == 'model_output') & (df['model_name'] == model)])
            print(f"  │   ├── {model}/           # {model_count} files")
        print(f"  └── reconstruction_metadata.json")

if __name__ == "__main__":
    main()