"""
Generate detailed field comparison results for analysis.

Creates one JSON file per field showing all GT vs model comparisons
with model name and pmid for traceability.
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


def get_pmid_from_data(data: Dict[str, Any]) -> str:
    """Extract PMID from cell line data."""
    publications = data.get('publications', [])
    if publications and len(publications) > 0:
        pmid = publications[0].get('pmid')
        if pmid and not is_missing_value(pmid):
            return str(pmid)
    return "unknown"


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


def generate_field_comparisons_for_cell_line(gt_data: Dict[str, Any],
                                           model_data: Dict[str, Any],
                                           model_name: str,
                                           cell_line_name: str) -> Dict[str, List[Dict]]:
    """
    Generate field comparisons for a single cell line.

    Returns:
        Dict mapping field_path -> list of comparison records
    """
    field_comparisons = defaultdict(list)

    # Get PMID for traceability
    pmid = get_pmid_from_data(gt_data)

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
                        model_value = model_item.get(field_name) if model_item else None

                        comparison = {
                            "model_name": model_name,
                            "pmid": pmid,
                            "cell_line": cell_line_name,
                            "ground_truth": gt_value,
                            "model_output": model_value
                        }

                        field_comparisons[field_path].append(comparison)

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
                        model_value = model_item.get(field_name)

                        comparison = {
                            "model_name": model_name,
                            "pmid": pmid,
                            "cell_line": cell_line_name,
                            "ground_truth": gt_value,
                            "model_output": model_value
                        }

                        field_comparisons[field_path].append(comparison)

            # Process unmatched GT items (contribute to total but not matches)
            matched_gt_items = {id(pair[0]) for pair in matched_pairs}
            for gt_item in gt_section:
                if id(gt_item) not in matched_gt_items:
                    matching_key = gt_item.get(matching_field)
                    for field_name, gt_value in gt_item.items():
                        if not is_missing_value(gt_value):
                            field_path = get_field_path(section_name, field_name)

                            comparison = {
                                "model_name": model_name,
                                "pmid": pmid,
                                "cell_line": cell_line_name,
                                "ground_truth": gt_value,
                                "model_output": None
                            }

                            field_comparisons[field_path].append(comparison)

    return field_comparisons


def generate_all_field_results(results_dir: str, output_dir: str):
    """
    Generate detailed field comparison files for all models and fields.
    """
    results_path = Path(results_dir)
    model_output_dir = results_path / "model_output"
    gt_dir = results_path / "ground_truth"
    output_path = Path(output_dir)

    if not model_output_dir.exists() or not gt_dir.exists():
        raise ValueError(f"Required directories not found in {results_dir}")

    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)

    # Aggregate all field comparisons
    all_field_comparisons = defaultdict(list)

    # Get all model directories
    model_dirs = [d for d in model_output_dir.iterdir() if d.is_dir()]

    for model_dir in model_dirs:
        model_name = model_dir.name
        print(f"Processing model: {model_name}")

        # Get all model output files
        model_files = list(model_dir.glob("*_m.json"))

        for model_file in model_files:
            # Get corresponding GT file
            cell_line_name = model_file.stem.replace("_m", "")
            gt_file = gt_dir / f"{cell_line_name}_gt.json"

            if not gt_file.exists():
                continue

            try:
                # Load data
                gt_data = load_json_file(str(gt_file))
                model_data = load_json_file(str(model_file))

                # Generate field comparisons for this cell line
                field_comparisons = generate_field_comparisons_for_cell_line(
                    gt_data, model_data, model_name, cell_line_name
                )

                # Aggregate into global field comparisons
                for field_path, comparisons in field_comparisons.items():
                    all_field_comparisons[field_path].extend(comparisons)

            except Exception as e:
                print(f"Error processing {cell_line_name} for {model_name}: {e}")
                continue

    # Save individual field files
    print(f"\nSaving field comparison files to {output_path}")

    for field_path, comparisons in all_field_comparisons.items():
        # Create safe filename
        safe_field_name = field_path.replace(".", "_")
        output_file = output_path / f"{safe_field_name}.json"

        # Calculate summary statistics
        total_comparisons = len(comparisons)
        total_matches = sum(1 for c in comparisons
                          if c["ground_truth"] is not None and c["model_output"] is not None
                          and str(c["ground_truth"]).strip() == str(c["model_output"]).strip())
        total_missing = sum(1 for c in comparisons if c["model_output"] is None)

        field_data = {
            "field_path": field_path,
            "summary": {
                "total_comparisons": total_comparisons,
                "total_matches": total_matches,
                "total_model_missing": total_missing,
                "recall": total_matches / total_comparisons if total_comparisons > 0 else 0.0
            },
            "comparisons": comparisons
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(field_data, f, indent=2, ensure_ascii=False)

        print(f"  {field_path}: {total_comparisons} comparisons, {total_matches} matches ({total_matches/total_comparisons:.3f})" if total_comparisons > 0 else f"  {field_path}: 0 comparisons")

    print(f"\nGenerated {len(all_field_comparisons)} field comparison files")


if __name__ == "__main__":
    # Default paths
    results_dir = "/home/stefanmirandadev/projects/stefan-masters-research-package/results/cleaned_results"
    output_dir = "/home/stefanmirandadev/projects/stefan-masters-research-package/scoring/field_recall_scoring/field_results"

    print("Generating detailed field comparison files...")

    try:
        generate_all_field_results(results_dir, output_dir)
        print("Field comparison files generated successfully!")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)