#!/usr/bin/env python3
"""
Reconstruct JSONs Script

This script takes a harmonized DataFrame and reconstructs both ground truth and
model output JSON files from the cleaned/harmonized data.

Usage:
    python reconstruct.py [--config config_reconstruct.json]

The script will:
1. Load the harmonized DataFrame
2. Separate ground truth and model output rows
3. Reconstruct JSON files from the flattened columns
4. Save to separate folders (ground_truth/ and model_output/)
5. Preserve proper naming conventions (_gt and _m suffixes)

Important: The script uses the harmonized flattened columns, not the original JSON strings,
so any changes you made to the DataFrame will be reflected in the output JSONs.
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

def get_all_possible_fields_from_df(df: pd.DataFrame) -> Dict[str, set]:
    """
    Extract all possible fields from DataFrame columns.
    This reconstructs the field mapping from the flattened column names.
    """
    all_sections = {}

    # Find all _json columns to identify sections
    json_columns = [col for col in df.columns if col.endswith('_json')]

    for json_col in json_columns:
        section_name = json_col[:-5]  # Remove '_json' suffix

        # Find all columns that belong to this section
        section_columns = [col for col in df.columns
                          if col.startswith(f"{section_name}_") and not col.endswith('_json')]

        # Extract field names
        fields = set()
        for col in section_columns:
            field_name = col[len(f"{section_name}_"):]  # Remove section prefix
            fields.add(field_name)

        all_sections[section_name] = fields

    return all_sections

def reconstruct_json_from_row(row: pd.Series, all_possible_fields: Dict[str, set]) -> Dict[str, Any]:
    """
    Reconstruct JSON from harmonized flattened columns.

    This function builds the JSON structure from the individual flattened columns
    (which may have been edited for harmonization) rather than just parsing
    the original JSON strings.
    """
    reconstructed = {}

    # Get all columns that end with '_json' to know what sections exist
    json_columns = [col for col in row.index if col.endswith('_json')]

    for json_col in json_columns:
        # Extract the base key name (remove '_json' suffix)
        base_key = json_col[:-5]  # Remove '_json'

        # Parse the original JSON to get the structure template
        if pd.notna(row[json_col]):
            try:
                original_structure = json.loads(row[json_col])

                # If it's a list of dictionaries, rebuild it from flattened columns
                if isinstance(original_structure, list):
                    rebuilt_list = []

                    if original_structure and isinstance(original_structure[0], dict):
                        # Get all possible field names for this section
                        if base_key in all_possible_fields:
                            field_columns = [f"{base_key}_{field}" for field in all_possible_fields[base_key]]
                            field_columns = [col for col in field_columns if col in row.index]

                            # Group fields by their base names
                            fields = {}
                            for col in field_columns:
                                field_name = col[len(f"{base_key}_"):]  # Remove section prefix
                                fields[field_name] = row[col]

                            # Handle multiple items in lists (separated by " | ")
                            max_items = 1
                            for field_name, value in fields.items():
                                if pd.notna(value) and isinstance(value, str) and " | " in value:
                                    max_items = max(max_items, len(value.split(" | ")))

                            # Create items
                            for item_idx in range(max_items):
                                item = {}
                                for field_name, value in fields.items():
                                    if pd.notna(value):
                                        if isinstance(value, str) and " | " in value:
                                            # Split by separator and take the appropriate item
                                            parts = value.split(" | ")
                                            if item_idx < len(parts):
                                                item[field_name] = parts[item_idx]
                                            # else: this item doesn't have this field
                                        else:
                                            # Single value - only add to first item
                                            if item_idx == 0:
                                                item[field_name] = value

                                if item:  # Only add non-empty items
                                    rebuilt_list.append(item)

                    reconstructed[base_key] = rebuilt_list if rebuilt_list else []
                else:
                    # For non-list structures, keep original
                    reconstructed[base_key] = original_structure

            except json.JSONDecodeError:
                # If parsing fails, create empty list
                reconstructed[base_key] = []
        else:
            reconstructed[base_key] = []

    return reconstructed

def reconstruct_ground_truth(df: pd.DataFrame, output_dir: Path, all_possible_fields: Dict[str, set], verbose: bool = True) -> int:
    """
    Reconstruct ground truth JSON files from DataFrame.
    Returns number of files created.
    """
    gt_dir = output_dir / "ground_truth"
    gt_dir.mkdir(parents=True, exist_ok=True)

    # Filter to ground truth rows
    gt_rows = df[df['data_source'] == 'ground_truth']

    if verbose:
        print(f"  Reconstructing {len(gt_rows)} ground truth files...")

    files_created = 0
    for idx, row in gt_rows.iterrows():
        try:
            # Reconstruct JSON from harmonized data
            reconstructed_json = reconstruct_json_from_row(row, all_possible_fields)

            # Get filename - use hpscreg_name which should include _gt suffix
            hpscreg_name = row['hpscreg_name']
            if not hpscreg_name.endswith('_gt'):
                hpscreg_name = f"{hpscreg_name}_gt"

            filename = f"{hpscreg_name}.json"
            output_path = gt_dir / filename

            # Save JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(reconstructed_json, f, indent=2)

            files_created += 1

        except Exception as e:
            if verbose:
                print(f"    ERROR: Could not reconstruct {row.get('hpscreg_name', 'unknown')}: {e}")

    if verbose:
        print(f"    ✓ Created {files_created} ground truth JSON files in {gt_dir}")

    return files_created

def reconstruct_model_output(df: pd.DataFrame, output_dir: Path, all_possible_fields: Dict[str, set], verbose: bool = True) -> int:
    """
    Reconstruct model output JSON files from DataFrame.
    Returns number of files created.
    """
    model_dir = output_dir / "model_output"
    model_dir.mkdir(parents=True, exist_ok=True)

    # Filter to model output rows
    model_rows = df[df['data_source'] == 'model_output']

    if verbose:
        print(f"  Reconstructing {len(model_rows)} model output files...")

    files_created = 0
    for idx, row in model_rows.iterrows():
        try:
            # Reconstruct JSON from harmonized data
            reconstructed_json = reconstruct_json_from_row(row, all_possible_fields)

            # Get filename - use hpscreg_name which should include _m suffix
            hpscreg_name = row['hpscreg_name']
            if not hpscreg_name.endswith('_m'):
                hpscreg_name = f"{hpscreg_name}_m"

            filename = f"{hpscreg_name}.json"
            output_path = model_dir / filename

            # Save JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(reconstructed_json, f, indent=2)

            files_created += 1

        except Exception as e:
            if verbose:
                print(f"    ERROR: Could not reconstruct {row.get('hpscreg_name', 'unknown')}: {e}")

    if verbose:
        print(f"    ✓ Created {files_created} model output JSON files in {model_dir}")

    return files_created

def validate_reconstruction(df: pd.DataFrame, output_dir: Path, verbose: bool = True) -> Dict[str, Any]:
    """
    Validate the reconstruction by checking file counts and basic structure.
    """
    validation_results = {
        'ground_truth_files': 0,
        'model_output_files': 0,
        'total_files': 0,
        'expected_gt': len(df[df['data_source'] == 'ground_truth']),
        'expected_model': len(df[df['data_source'] == 'model_output']),
    }

    # Count created files
    gt_dir = output_dir / "ground_truth"
    model_dir = output_dir / "model_output"

    if gt_dir.exists():
        validation_results['ground_truth_files'] = len(list(gt_dir.glob('*.json')))

    if model_dir.exists():
        validation_results['model_output_files'] = len(list(model_dir.glob('*.json')))

    validation_results['total_files'] = (validation_results['ground_truth_files'] +
                                       validation_results['model_output_files'])

    if verbose:
        print(f"\n📊 Validation Results:")
        print(f"  Ground truth files: {validation_results['ground_truth_files']}/{validation_results['expected_gt']}")
        print(f"  Model output files: {validation_results['model_output_files']}/{validation_results['expected_model']}")
        print(f"  Total files created: {validation_results['total_files']}")

        # Check for discrepancies
        if validation_results['ground_truth_files'] != validation_results['expected_gt']:
            print(f"  ⚠️  WARNING: Ground truth file count mismatch")
        if validation_results['model_output_files'] != validation_results['expected_model']:
            print(f"  ⚠️  WARNING: Model output file count mismatch")

    return validation_results

def main():
    parser = argparse.ArgumentParser(description='Reconstruct JSON files from harmonized DataFrame')
    parser.add_argument('--config', default='results_processing/config_reconstruct.json',
                       help='Path to configuration file')
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Set up paths
    dataframe_path = Path(config['dataframe_path'])
    output_path = Path(config['output_path'])
    overwrite_existing = config.get('overwrite_existing', True)
    verbose = config.get('verbose', True)

    if verbose:
        print("🔧 Reconstruct JSONs from DataFrame")
        print("=" * 40)
        print(f"DataFrame path: {dataframe_path}")
        print(f"Output path: {output_path}")
        print(f"Overwrite existing: {overwrite_existing}")

    # Check if dataframe exists
    if not dataframe_path.exists():
        print(f"ERROR: DataFrame file not found: {dataframe_path}")
        sys.exit(1)

    # Load DataFrame
    if verbose:
        print(f"\n📂 Loading DataFrame...")

    try:
        if dataframe_path.suffix == '.pkl':
            df = pd.read_pickle(dataframe_path)
        elif dataframe_path.suffix == '.csv':
            df = pd.read_csv(dataframe_path)
        else:
            print(f"ERROR: Unsupported file format: {dataframe_path.suffix}")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not load DataFrame: {e}")
        sys.exit(1)

    if verbose:
        print(f"DataFrame loaded: {df.shape}")
        print(f"Data sources: {df['data_source'].value_counts().to_dict()}")

    # Check for required columns
    required_columns = ['data_source', 'hpscreg_name']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"ERROR: Missing required columns: {missing_columns}")
        sys.exit(1)

    # Create output directory
    if output_path.exists() and not overwrite_existing:
        print(f"ERROR: Output directory exists and overwrite_existing=False: {output_path}")
        sys.exit(1)

    output_path.mkdir(parents=True, exist_ok=True)

    # Extract field mapping from DataFrame
    if verbose:
        print(f"\n🔍 Analyzing DataFrame structure...")
    all_possible_fields = get_all_possible_fields_from_df(df)

    if verbose:
        total_fields = sum(len(fields) for fields in all_possible_fields.values())
        print(f"Found {len(all_possible_fields)} sections with {total_fields} total fields")

    # Reconstruct JSONs
    if verbose:
        print(f"\n⚙️  Reconstructing JSON files...")

    gt_count = reconstruct_ground_truth(df, output_path, all_possible_fields, verbose)
    model_count = reconstruct_model_output(df, output_path, all_possible_fields, verbose)

    # Validate results
    validation_results = validate_reconstruction(df, output_path, verbose)

    # Save reconstruction metadata
    metadata = {
        'dataframe_path': str(dataframe_path),
        'output_path': str(output_path),
        'reconstruction_timestamp': pd.Timestamp.now().isoformat(),
        'input_dataframe_shape': df.shape,
        'files_created': {
            'ground_truth': gt_count,
            'model_output': model_count,
            'total': gt_count + model_count
        },
        'validation_results': validation_results,
        'sections_and_fields': {k: len(v) for k, v in all_possible_fields.items()},
        'config_used': config
    }

    metadata_path = output_path / 'reconstruction_metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    if verbose:
        print(f"✓ Saved reconstruction metadata: {metadata_path}")

    if verbose:
        print(f"\n🎉 RECONSTRUCTION COMPLETE!")
        print(f"📁 Output directory: {output_path}")
        print(f"📄 Ground truth JSONs: {output_path / 'ground_truth'}")
        print(f"📄 Model output JSONs: {output_path / 'model_output'}")
        print(f"📊 Total files created: {gt_count + model_count}")
        print(f"\nThe JSONs now reflect any harmonization changes you made to the DataFrame!")

if __name__ == "__main__":
    main()