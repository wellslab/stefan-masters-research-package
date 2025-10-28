#!/usr/bin/env python3
"""
Generate Combined DataFrame Script

This script processes both model output JSONs and ground truth JSONs into a unified
DataFrame for harmonization and entity matching/scoring.

Usage:
    python generate_combined_dataframe.py [--config config_generate.json]

The script will:
1. Load model output JSONs from the results directory
2. Load ground truth JSONs
3. Analyze all possible fields across both datasets
4. Create a combined DataFrame with flattened columns
5. Save the DataFrame and metadata to the results directory

Important: hpscreg_name will include suffixes (_m for model, _gt for ground truth)
"""

import json
import pandas as pd
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple
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

def get_all_possible_fields(json_data_list: List[Dict[str, Any]]) -> Dict[str, set]:
    """
    Analyze all JSON files to get complete field inventory.
    Returns a dict with section names as keys and sets of all possible fields as values.
    """
    all_sections = {}

    for json_data in json_data_list:
        for section_name, section_data in json_data.items():
            if section_name not in all_sections:
                all_sections[section_name] = set()

            if isinstance(section_data, list) and section_data:
                # Handle arrays (like ground truth)
                for item in section_data:
                    if isinstance(item, dict):
                        all_sections[section_name].update(item.keys())
            elif isinstance(section_data, dict):
                # Handle objects (like model output)
                all_sections[section_name].update(section_data.keys())

    return all_sections

def flatten_json_for_dataframe(json_data: Dict[str, Any], all_possible_fields: Dict[str, set], prefix: str = '') -> List[Dict[str, Any]]:
    """
    Enhanced flattening that creates multiple rows for arrays with multiple items.
    Returns a list of flattened dictionaries (rows).
    """
    # First, find the maximum number of items in any array to determine how many rows we need
    max_array_length = 1
    array_sections = {}

    for section_name, section_data in json_data.items():
        if isinstance(section_data, list) and section_data:
            array_sections[section_name] = section_data
            max_array_length = max(max_array_length, len(section_data))

    # Create rows (one for each array item)
    rows = []

    for row_idx in range(max_array_length):
        flattened = {}

        # Store original JSON for reconstruction
        flattened['_original_json'] = json.dumps(json_data)
        flattened['_array_index'] = row_idx

        for section_name, section_data in json_data.items():
            new_key = f"{prefix}{section_name}" if prefix else section_name

            if isinstance(section_data, list):
                # Handle arrays
                if row_idx < len(section_data):
                    item = section_data[row_idx]
                    if isinstance(item, dict):
                        # Flatten the object at this array index
                        if section_name in all_possible_fields:
                            for field_name in all_possible_fields[section_name]:
                                field_key = f"{new_key}.{field_name}"
                                if field_name in item:
                                    val = item[field_name]
                                    if val is not None and str(val).strip() not in ["None", "Missing", "nan", ""]:
                                        flattened[field_key] = str(val)
                                    else:
                                        flattened[field_key] = None
                                else:
                                    flattened[field_key] = None
                    else:
                        # Simple value in array
                        flattened[new_key] = str(item) if item is not None else None
                else:
                    # This row doesn't have data for this array section
                    if section_name in all_possible_fields:
                        for field_name in all_possible_fields[section_name]:
                            field_key = f"{new_key}.{field_name}"
                            flattened[field_key] = None

            elif isinstance(section_data, dict):
                # Handle objects (same for all rows)
                if section_name in all_possible_fields:
                    for field_name in all_possible_fields[section_name]:
                        field_key = f"{new_key}.{field_name}"
                        if field_name in section_data:
                            val = section_data[field_name]
                            if val is not None and str(val).strip() not in ["None", "Missing", "nan", ""]:
                                flattened[field_key] = str(val)
                            else:
                                flattened[field_key] = None
                        else:
                            flattened[field_key] = None
            else:
                # Primitive values (same for all rows)
                flattened[new_key] = section_data

        rows.append(flattened)

    return rows

def load_all_json_data(results_dir: Path, ground_truth_dir: Path, verbose: bool = True) -> Tuple[List[Dict], List[Path], List[Path]]:
    """
    Load all JSON data from both model outputs and ground truth for field analysis.
    Returns: (all_json_data, model_json_paths, gt_json_paths)
    """
    all_json_data = []
    model_json_paths = []
    gt_json_paths = []

    # Load model output JSONs
    if not results_dir.exists():
        print(f"ERROR: Results directory not found: {results_dir}")
        sys.exit(1)

    article_dirs = [d for d in results_dir.iterdir() if d.is_dir()]
    if verbose:
        print(f"Found {len(article_dirs)} article directories in model outputs")

    for article_dir in article_dirs:
        # Skip non-PMID directories
        if article_dir.name.endswith('_EXCEPTION.txt'):
            continue

        json_files = list(article_dir.glob('*.json'))
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    all_json_data.append(json_data)
                    model_json_paths.append(json_file)
            except Exception as e:
                if verbose:
                    print(f"WARNING: Error loading {json_file}: {e}")

    # Load ground truth JSONs
    if not ground_truth_dir.exists():
        print(f"ERROR: Ground truth directory not found: {ground_truth_dir}")
        sys.exit(1)

    gt_files = list(ground_truth_dir.glob('*.json'))
    if verbose:
        print(f"Found {len(gt_files)} ground truth files")

    for gt_file in gt_files:
        try:
            with open(gt_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                all_json_data.append(json_data)
                gt_json_paths.append(gt_file)
        except Exception as e:
            if verbose:
                print(f"WARNING: Error loading {gt_file}: {e}")

    if verbose:
        print(f"Total JSON files loaded: {len(all_json_data)}")
        print(f"  Model outputs: {len(model_json_paths)}")
        print(f"  Ground truth: {len(gt_json_paths)}")

    return all_json_data, model_json_paths, gt_json_paths

def process_model_outputs(results_dir: Path, all_possible_fields: Dict[str, set], verbose: bool = True) -> pd.DataFrame:
    """
    Process model output JSON files and create DataFrame rows.
    Note: hpscreg_name will include '_m' suffix to distinguish from ground truth.
    """
    all_rows = []

    article_dirs = [d for d in results_dir.iterdir() if d.is_dir()]

    for article_dir in article_dirs:
        pmid = article_dir.name

        # Skip non-PMID directories
        if pmid.endswith('_EXCEPTION.txt'):
            continue

        json_files = list(article_dir.glob('*.json'))

        if verbose and json_files:
            print(f"  Processing PMID {pmid}: {len(json_files)} files")

        for json_file in json_files:
            try:
                # Extract base hpscreg name from filename and add _m suffix
                hpscreg_base = json_file.stem
                if hpscreg_base.endswith('_m'):
                    hpscreg_base = hpscreg_base[:-2]  # Remove existing '_m' suffix
                hpscreg_name = f"{hpscreg_base}_m"  # Always add _m suffix

                # Load JSON data
                with open(json_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)

                # Flatten the JSON data (returns list of rows)
                flattened_rows = flatten_json_for_dataframe(json_data, all_possible_fields)

                # Add metadata columns to each row
                for row_idx, flattened_data in enumerate(flattened_rows):
                    # For multiple rows, modify the hpscreg_name to indicate array index
                    row_hpscreg_name = f"{hpscreg_name}" if len(flattened_rows) == 1 else f"{hpscreg_name}#{row_idx}"

                    row_data = {
                        'data_source': 'model_output',
                        'hpscreg_name': row_hpscreg_name,  # May include array index
                        'hpscreg_base': hpscreg_base,  # Base name without suffix
                        'publication_pmid': pmid,
                        'json_filename': json_file.name,
                        'json_filepath': str(json_file.relative_to(results_dir)),
                        **flattened_data
                    }

                    all_rows.append(row_data)

            except Exception as e:
                if verbose:
                    print(f"    ERROR: Could not process {json_file}: {e}")
                continue

    return pd.DataFrame(all_rows)

def process_ground_truth(ground_truth_dir: Path, all_possible_fields: Dict[str, set], verbose: bool = True) -> pd.DataFrame:
    """
    Process ground truth JSON files and create DataFrame rows.
    Note: hpscreg_name will include '_gt' suffix to distinguish from model output.
    """
    all_rows = []

    gt_files = list(ground_truth_dir.glob('*.json'))

    for gt_file in gt_files:
        try:
            # Extract base hpscreg name from filename and add _gt suffix
            hpscreg_base = gt_file.stem
            if hpscreg_base.endswith('_gt'):
                hpscreg_base = hpscreg_base[:-3]  # Remove existing '_gt' suffix
            hpscreg_name = f"{hpscreg_base}_gt"  # Always add _gt suffix

            # Load JSON data
            with open(gt_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            # Flatten the JSON data (returns list of rows)
            flattened_rows = flatten_json_for_dataframe(json_data, all_possible_fields)

            # Extract PMID from publications if available
            pmid = None
            if 'publications' in json_data and json_data['publications']:
                for pub in json_data['publications']:
                    if isinstance(pub, dict) and 'pmid' in pub:
                        pmid = pub['pmid']
                        if pmid and pmid != "Missing":
                            break

            # Add metadata columns to each row
            for row_idx, flattened_data in enumerate(flattened_rows):
                # For multiple rows, modify the hpscreg_name to indicate array index
                row_hpscreg_name = f"{hpscreg_name}" if len(flattened_rows) == 1 else f"{hpscreg_name}#{row_idx}"

                row_data = {
                    'data_source': 'ground_truth',
                    'hpscreg_name': row_hpscreg_name,  # May include array index
                    'hpscreg_base': hpscreg_base,  # Base name without suffix
                    'publication_pmid': pmid,
                    'json_filename': gt_file.name,
                    'json_filepath': str(gt_file),
                    **flattened_data
                }

                all_rows.append(row_data)

        except Exception as e:
            if verbose:
                print(f"ERROR: Could not process {gt_file}: {e}")
            continue

    return pd.DataFrame(all_rows)

def save_dataframe(df: pd.DataFrame, output_dir: Path, filename: str, formats: List[str], verbose: bool = True):
    """Save DataFrame in specified formats."""
    output_dir.mkdir(parents=True, exist_ok=True)

    for fmt in formats:
        if fmt == 'csv':
            csv_path = output_dir / f"{filename}.csv"
            df.to_csv(csv_path, index=False)
            if verbose:
                print(f"✓ Saved DataFrame to CSV: {csv_path}")
        elif fmt == 'pkl':
            pkl_path = output_dir / f"{filename}.pkl"
            df.to_pickle(pkl_path)
            if verbose:
                print(f"✓ Saved DataFrame to Pickle: {pkl_path}")
        elif fmt == 'excel':
            try:
                excel_path = output_dir / f"{filename}.xlsx"
                df.to_excel(excel_path, index=False)
                if verbose:
                    print(f"✓ Saved DataFrame to Excel: {excel_path}")
            except ImportError:
                if verbose:
                    print(f"WARNING: Could not save Excel file - openpyxl not installed")

def main():
    parser = argparse.ArgumentParser(description='Generate combined DataFrame from model outputs and ground truth')
    parser.add_argument('--config', default='results_processing/config_generate.json',
                       help='Path to configuration file')
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Set up paths
    results_dir = Path(config['results_path'])
    ground_truth_dir = Path(config['ground_truth_path'])
    output_filename = config['output_filename']
    save_formats = config.get('save_formats', ['csv'])
    include_metadata = config.get('include_metadata', True)
    verbose = config.get('verbose', True)

    if verbose:
        print("🔬 Generate Combined DataFrame")
        print("=" * 40)
        print(f"Results path: {results_dir}")
        print(f"Ground truth path: {ground_truth_dir}")
        print(f"Output filename: {output_filename}")
        print(f"Save formats: {save_formats}")

    # Load all JSON data for field analysis
    if verbose:
        print("\n📂 Loading JSON data...")
    all_json_data, _, _ = load_all_json_data(results_dir, ground_truth_dir, verbose)

    # Analyze all possible fields
    if verbose:
        print("\n🔍 Analyzing fields...")
    all_possible_fields = get_all_possible_fields(all_json_data)

    if verbose:
        total_fields = sum(len(fields) for fields in all_possible_fields.values())
        print(f"Field analysis complete:")
        for section, fields in all_possible_fields.items():
            print(f"  {section}: {len(fields)} fields")
        print(f"Total unique fields: {total_fields}")

    # Process datasets
    if verbose:
        print("\n⚙️  Processing datasets...")

    print("Processing model outputs...")
    model_df = process_model_outputs(results_dir, all_possible_fields, verbose)
    if verbose:
        print(f"Model output DataFrame: {model_df.shape}")

    print("Processing ground truth...")
    gt_df = process_ground_truth(ground_truth_dir, all_possible_fields, verbose)
    if verbose:
        print(f"Ground truth DataFrame: {gt_df.shape}")

    # Combine datasets
    if verbose:
        print("\n🔗 Combining datasets...")
    combined_df = pd.concat([model_df, gt_df], ignore_index=True, sort=False)

    # Analyze overlap based on base names
    model_bases = set(model_df['hpscreg_base'])
    gt_bases = set(gt_df['hpscreg_base'])
    common_bases = model_bases.intersection(gt_bases)

    if verbose:
        print(f"Combined DataFrame shape: {combined_df.shape}")
        print(f"Total cell lines: {len(combined_df)}")
        print(f"  Model outputs: {len(model_df)}")
        print(f"  Ground truth: {len(gt_df)}")
        print(f"\nCell line overlap analysis (by base name):")
        print(f"  Common (in both datasets): {len(common_bases)}")
        print(f"  Model output only: {len(model_bases - gt_bases)}")
        print(f"  Ground truth only: {len(gt_bases - model_bases)}")

    # Save results
    output_dir = results_dir
    if verbose:
        print(f"\n💾 Saving results to: {output_dir}")

    save_dataframe(combined_df, output_dir, output_filename, save_formats, verbose)

    # Save metadata if requested
    if include_metadata:
        metadata = {
            'total_rows': len(combined_df),
            'model_output_rows': len(model_df),
            'ground_truth_rows': len(gt_df),
            'total_columns': len(combined_df.columns),
            'unique_hpscreg_names': combined_df['hpscreg_name'].nunique(),
            'unique_hpscreg_bases': combined_df['hpscreg_base'].nunique(),
            'unique_pmids': combined_df['publication_pmid'].nunique(),
            'common_cell_lines': len(common_bases),
            'sections_and_fields': {k: len(v) for k, v in all_possible_fields.items()},
            'config_used': config
        }

        metadata_path = output_dir / f"{output_filename}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        if verbose:
            print(f"✓ Saved processing metadata: {metadata_path}")

    if verbose:
        print(f"\n🎉 PROCESSING COMPLETE!")
        print(f"📊 Combined DataFrame: {combined_df.shape}")
        print(f"📁 Files saved to: {output_dir}")
        print(f"🚀 Ready for harmonization!")
        print(f"\nNext steps:")
        print(f"1. Load the DataFrame: pd.read_csv('{output_dir / output_filename}.csv')")
        print(f"2. Harmonize the flattened columns")
        print(f"3. Use reconstruct.py to generate cleaned JSONs")

if __name__ == "__main__":
    main()