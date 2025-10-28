"""
Single-item array recall calculation for cell line JSON data.

This module handles recall calculation for arrays that should contain only one item.
"""

from typing import Dict, Any, Tuple, Optional, List
import json


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


class SingleItemRecallResult:
    """Result of single-item array recall calculation."""

    def __init__(self, section_name: str):
        self.section_name = section_name
        self.total_gt_fields = 0
        self.matched_fields = 0
        self.recall = 0.0
        self.status = "success"  # success, gt_multiple_items, model_multiple_items, missing_sections
        self.message = ""

    def set_recall(self, matched: int, total: int):
        """Set recall values."""
        self.matched_fields = matched
        self.total_gt_fields = total
        self.recall = matched / total if total > 0 else 0.0

    def set_error(self, status: str, message: str):
        """Set error status."""
        self.status = status
        self.message = message


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON file and return parsed data."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ValueError(f"Error loading JSON file {file_path}: {e}")


def calculate_single_item_recall(gt_data: Dict[str, Any],
                                model_data: Dict[str, Any],
                                section_name: str) -> SingleItemRecallResult:
    """
    Calculate recall for a single-item array section.

    Args:
        gt_data: Ground truth JSON data
        model_data: Model output JSON data
        section_name: Name of the array section to compare

    Returns:
        SingleItemRecallResult with recall score and status
    """
    result = SingleItemRecallResult(section_name)

    # Check if sections exist
    gt_section = gt_data.get(section_name, [])
    model_section = model_data.get(section_name, [])

    # Validate ground truth has exactly one item
    if len(gt_section) == 0:
        result.set_error("missing_sections", f"Ground truth missing {section_name} section")
        return result
    elif len(gt_section) > 1:
        result.set_error("gt_multiple_items",
                        f"Ground truth has {len(gt_section)} items in {section_name}, expected 1. Skipping recall.")
        return result

    # Ground truth has exactly 1 item - proceed with validation
    gt_item = gt_section[0]

    # Check model output
    if len(model_section) == 0:
        # Model has no items - all GT fields are missed
        total_gt_fields = count_non_missing_fields(gt_item)
        result.set_recall(matched=0, total=total_gt_fields)
        result.message = f"Model output missing {section_name} section"
        return result
    elif len(model_section) > 1:
        # Model has multiple items when it should have 1 - structure error but fields still count
        total_gt_fields = count_non_missing_fields(gt_item)
        result.set_recall(matched=0, total=total_gt_fields)
        result.status = "success"  # Fields contribute to total, just no matches due to structure error
        result.message = f"Model output has {len(model_section)} items in {section_name}, expected 1. No matches due to structure error."
        return result

    # Both GT and model have exactly 1 item - perform field-wise comparison
    model_item = model_section[0]
    matched_fields, total_gt_fields = compare_items_fieldwise(gt_item, model_item)

    result.set_recall(matched=matched_fields, total=total_gt_fields)
    result.message = f"Compared {total_gt_fields} GT fields, {matched_fields} matched"

    return result


def count_non_missing_fields(item: Dict[str, Any]) -> int:
    """Count non-missing fields in an item."""
    count = 0
    for key, value in item.items():
        if value is not None and str(value).strip() not in ["", "Missing", "None"]:
            count += 1
    return count


def compare_items_fieldwise(gt_item: Dict[str, Any], model_item: Dict[str, Any]) -> Tuple[int, int]:
    """
    Compare two items field by field.

    Args:
        gt_item: Ground truth item
        model_item: Model output item

    Returns:
        Tuple of (matched_fields, total_gt_fields)
    """
    matched_fields = 0
    total_gt_fields = 0

    for field_name, gt_value in gt_item.items():
        # Only count non-missing GT fields
        if gt_value is not None and str(gt_value).strip() not in ["", "Missing", "None"]:
            total_gt_fields += 1

            # Check if model has matching value
            model_value = model_item.get(field_name)
            if model_value is not None:
                # Exact string match comparison
                if str(gt_value).strip() == str(model_value).strip():
                    matched_fields += 1

    return matched_fields, total_gt_fields


def calculate_cell_line_single_item_recall(gt_file_path: str,
                                          model_file_path: str) -> Dict[str, SingleItemRecallResult]:
    """
    Calculate single-item array recall for all relevant sections in a cell line.

    Args:
        gt_file_path: Path to ground truth JSON file
        model_file_path: Path to model output JSON file

    Returns:
        Dictionary mapping section names to recall results
    """
    # Load JSON files
    gt_data = load_json_file(gt_file_path)
    model_data = load_json_file(model_file_path)

    results = {}

    # Calculate recall for each single-item array section
    for section_name in SINGLE_ITEM_ARRAYS:
        result = calculate_single_item_recall(gt_data, model_data, section_name)
        results[section_name] = result

    return results


def print_recall_summary(results: Dict[str, SingleItemRecallResult], cell_line_name: str = ""):
    """Print a summary of recall results."""
    if cell_line_name:
        print(f"\n=== Single-Item Array Recall Results for {cell_line_name} ===")
    else:
        print(f"\n=== Single-Item Array Recall Results ===")

    total_matched = 0
    total_fields = 0

    for section_name, result in results.items():
        status_indicator = "✓" if result.status == "success" else "⚠"
        print(f"{status_indicator} {section_name}: {result.recall:.3f} ({result.matched_fields}/{result.total_gt_fields})")

        if result.message:
            print(f"   {result.message}")

        if result.status == "success":
            total_matched += result.matched_fields
            total_fields += result.total_gt_fields

    if total_fields > 0:
        overall_recall = total_matched / total_fields
        print(f"\nOverall Single-Item Recall: {overall_recall:.3f} ({total_matched}/{total_fields})")
    else:
        print(f"\nNo valid single-item fields found for recall calculation")


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) != 3:
        print("Usage: python single_item_recall.py <gt_file.json> <model_file.json>")
        sys.exit(1)

    gt_file = sys.argv[1]
    model_file = sys.argv[2]

    try:
        results = calculate_cell_line_single_item_recall(gt_file, model_file)
        print_recall_summary(results)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)