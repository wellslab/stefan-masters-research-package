"""
Field-wise recall calculation across all models and cell lines.

This module calculates recall performance on a per-field basis for each model,
providing insights into which specific fields each model can curate accurately.
"""

import json
import os
from typing import Dict, Any, List, Tuple, Set
from collections import defaultdict
from pathlib import Path


# Arrays that should contain only one item
SINGLE_ITEM_ARRAYS = {
    'publications',
    'donor',
    'genomic_characterisation',
    'induced_derivation',
    'culture_medium',
    'embryonic_derivation',
    'basic_data',
    'generator',
    'undifferentiated_characterisation'
}

# Arrays that can contain multiple items
MULTI_ITEM_ARRAYS = {
    'contact',
    'genomic_modifications',
    'differentiation_results',
    'ethics'
}

# Matching fields for multi-item arrays
MULTI_ITEM_MATCHING_FIELDS = {
    'contact': 'last_name',
    'differentiation_results': 'cell_type',
    'ethics': 'ethics_number',
    'genomic_modifications': 'loci_name'
}


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON file and return parsed data."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ValueError(f"Error loading JSON file {file_path}: {e}")


def is_missing_value(value: Any) -> bool:
    """Check if a value is considered missing."""
    return value is None or str(value).strip() in ["", "Missing", "None"]


def get_field_path(section_name: str, field_name: str) -> str:
    """Get the full field path for a field."""
    return f"{section_name}.{field_name}"


def extract_all_field_paths(data: Dict[str, Any]) -> Set[str]:
    """Extract all possible field paths from a JSON structure."""
    field_paths = set()

    for section_name, section_data in data.items():
        if not isinstance(section_data, list):
            continue

        for item in section_data:
            if isinstance(item, dict):
                for field_name in item.keys():
                    field_paths.add(get_field_path(section_name, field_name))

    return field_paths


def match_multi_item_arrays(gt_items: List[Dict], model_items: List[Dict],
                           matching_field: str) -> List[Tuple[Dict, Dict]]:
    """
    Match items in multi-item arrays based on a key field.

    Returns list of (gt_item, model_item) pairs that matched.
    """
    matched_pairs = []
    used_model_indices = set()

    for gt_item in gt_items:
        gt_key_value = gt_item.get(matching_field)
        if is_missing_value(gt_key_value):
            continue

        # Find matching model items
        matching_model_indices = []
        for i, model_item in enumerate(model_items):
            if i in used_model_indices:
                continue

            model_key_value = model_item.get(matching_field)
            if not is_missing_value(model_key_value):
                if str(gt_key_value).strip() == str(model_key_value).strip():
                    matching_model_indices.append(i)

        # Only use if exactly one match (conservative approach)
        if len(matching_model_indices) == 1:
            model_idx = matching_model_indices[0]
            matched_pairs.append((gt_item, model_items[model_idx]))
            used_model_indices.add(model_idx)

    return matched_pairs


def calculate_field_recall_for_cell_line(gt_data: Dict[str, Any],
                                       model_data: Dict[str, Any]) -> Dict[str, Tuple[int, int]]:
    """
    Calculate field recall for a single cell line.

    Returns:
        Dict mapping field_path -> (matched_count, total_gt_count)
    """
    field_stats = defaultdict(lambda: [0, 0])  # [matched, total_gt]

    # Get all sections
    all_sections = set(gt_data.keys()) | set(model_data.keys())

    for section_name in all_sections:
        gt_section = gt_data.get(section_name, [])
        model_section = model_data.get(section_name, [])

        if not isinstance(gt_section, list) or not isinstance(model_section, list):
            continue

        if section_name in SINGLE_ITEM_ARRAYS:
            # Handle single-item arrays
            if len(gt_section) == 1:
                gt_item = gt_section[0]
                model_item = model_section[0] if len(model_section) == 1 else {}

                # Compare all fields in the GT item
                for field_name, gt_value in gt_item.items():
                    if not is_missing_value(gt_value):
                        field_path = get_field_path(section_name, field_name)
                        field_stats[field_path][1] += 1  # total_gt count

                        model_value = model_item.get(field_name) if model_item else None
                        if not is_missing_value(model_value):
                            if str(gt_value).strip() == str(model_value).strip():
                                field_stats[field_path][0] += 1  # matched count

        elif section_name in MULTI_ITEM_ARRAYS:
            # Handle multi-item arrays
            matching_field = MULTI_ITEM_MATCHING_FIELDS.get(section_name)
            if not matching_field:
                continue

            # Match items based on key field
            matched_pairs = match_multi_item_arrays(gt_section, model_section, matching_field)

            # Process matched pairs
            for gt_item, model_item in matched_pairs:
                for field_name, gt_value in gt_item.items():
                    if not is_missing_value(gt_value):
                        field_path = get_field_path(section_name, field_name)
                        field_stats[field_path][1] += 1  # total_gt count

                        model_value = model_item.get(field_name)
                        if not is_missing_value(model_value):
                            if str(gt_value).strip() == str(model_value).strip():
                                field_stats[field_path][0] += 1  # matched count

            # Process unmatched GT items (contribute to total but not matches)
            matched_gt_items = {id(pair[0]) for pair in matched_pairs}
            for gt_item in gt_section:
                if id(gt_item) not in matched_gt_items:
                    for field_name, gt_value in gt_item.items():
                        if not is_missing_value(gt_value):
                            field_path = get_field_path(section_name, field_name)
                            field_stats[field_path][1] += 1  # total_gt count only

    # Convert to tuple format
    return {field_path: (stats[0], stats[1]) for field_path, stats in field_stats.items()}


def calculate_field_recall_for_model(model_dir: str, gt_dir: str) -> Dict[str, Tuple[int, int]]:
    """
    Calculate field recall for all cell lines of a specific model.

    Returns:
        Dict mapping field_path -> (total_matched_count, total_gt_count)
    """
    model_path = Path(model_dir)
    gt_path = Path(gt_dir)

    # Aggregate field statistics across all cell lines
    aggregated_stats = defaultdict(lambda: [0, 0])  # [matched, total_gt]

    # Get all model output files
    model_files = list(model_path.glob("*_m.json"))

    for model_file in model_files:
        # Get corresponding GT file
        cell_line_name = model_file.stem.replace("_m", "")
        gt_file = gt_path / f"{cell_line_name}_gt.json"

        if not gt_file.exists():
            print(f"Warning: GT file not found for {cell_line_name}")
            continue

        try:
            # Load data
            gt_data = load_json_file(str(gt_file))
            model_data = load_json_file(str(model_file))

            # Calculate field recall for this cell line
            cell_line_stats = calculate_field_recall_for_cell_line(gt_data, model_data)

            # Aggregate into model statistics
            for field_path, (matched, total_gt) in cell_line_stats.items():
                aggregated_stats[field_path][0] += matched
                aggregated_stats[field_path][1] += total_gt

        except Exception as e:
            print(f"Error processing {cell_line_name}: {e}")
            continue

    # Convert to tuple format
    return {field_path: (stats[0], stats[1]) for field_path, stats in aggregated_stats.items()}


def calculate_all_models_field_recall(results_dir: str) -> Dict[str, Dict[str, float]]:
    """
    Calculate field recall for all models.

    Returns:
        Dict mapping model_name -> field_path -> recall_score
    """
    results_path = Path(results_dir)
    model_output_dir = results_path / "model_output"
    gt_dir = results_path / "ground_truth"

    if not model_output_dir.exists() or not gt_dir.exists():
        raise ValueError(f"Required directories not found in {results_dir}")

    all_results = {}

    # Get all model directories
    model_dirs = [d for d in model_output_dir.iterdir() if d.is_dir()]

    for model_dir in model_dirs:
        model_name = model_dir.name
        print(f"Processing model: {model_name}")

        try:
            # Calculate field recall for this model
            model_stats = calculate_field_recall_for_model(str(model_dir), str(gt_dir))

            # Convert to recall scores
            model_recall = {}
            for field_path, (matched, total_gt) in model_stats.items():
                recall = matched / total_gt if total_gt > 0 else 0.0
                model_recall[field_path] = recall

            all_results[model_name] = model_recall
            print(f"  Processed {len(model_recall)} fields")

        except Exception as e:
            print(f"Error processing model {model_name}: {e}")
            continue

    return all_results


def save_field_recall_results(results: Dict[str, Dict[str, float]], output_file: str):
    """Save field recall results to JSON file."""
    # Also include summary statistics
    output_data = {
        "field_recall_by_model": results,
        "summary": {
            "total_models": len(results),
            "total_unique_fields": len(set().union(*[fields.keys() for fields in results.values()])) if results else 0
        }
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Default paths
    results_dir = "/home/stefanmirandadev/projects/stefan-masters-research-package/results/cleaned_results"
    output_file = "/home/stefanmirandadev/projects/stefan-masters-research-package/scoring/field_recall_scoring/field_recall_results.json"

    print("Calculating field recall for all models...")

    try:
        results = calculate_all_models_field_recall(results_dir)
        save_field_recall_results(results, output_file)

        print(f"\nField recall calculation completed!")
        print(f"Results saved to: {output_file}")
        print(f"Processed {len(results)} models")

        # Print some summary stats
        if results:
            all_fields = set().union(*[fields.keys() for fields in results.values()])
            print(f"Total unique fields analyzed: {len(all_fields)}")

            for model_name, field_recalls in results.items():
                avg_recall = sum(field_recalls.values()) / len(field_recalls) if field_recalls else 0
                print(f"  {model_name}: {len(field_recalls)} fields, avg recall: {avg_recall:.3f}")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)