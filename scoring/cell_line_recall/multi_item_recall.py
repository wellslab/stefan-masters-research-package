"""
Multi-item array recall calculation for cell line JSON data.

This module handles recall calculation for arrays that can contain multiple items.
"""

from typing import Dict, Any, List, Tuple, Optional
import json
from collections import defaultdict

try:
    from .single_item_recall import (
        load_json_file,
        count_non_missing_fields,
        compare_items_fieldwise,
        MULTI_ITEM_ARRAYS
    )
except ImportError:
    from single_item_recall import (
        load_json_file,
        count_non_missing_fields,
        compare_items_fieldwise,
        MULTI_ITEM_ARRAYS
    )


# Matching fields for multi-item arrays
MULTI_ITEM_MATCHING_FIELDS = {
    'contact': 'last_name',
    'differentiation_results': 'cell_type',
    'ethics': 'ethics_number',
    'genomic_modifications': 'loci_name'
}


class MultiItemRecallResult:
    """Result of multi-item array recall calculation."""

    def __init__(self, section_name: str):
        self.section_name = section_name
        self.total_gt_fields = 0
        self.matched_fields = 0
        self.recall = 0.0
        self.status = "success"  # success, multiple_matches_skipped, no_matches_conservative
        self.message = ""
        self.gt_items_count = 0
        self.model_items_count = 0
        self.matched_pairs = 0
        self.skipped_items = 0

    def set_recall(self, matched: int, total: int):
        """Set recall values."""
        self.matched_fields = matched
        self.total_gt_fields = total
        self.recall = matched / total if total > 0 else 0.0

    def set_conservative_penalty(self, total_gt_fields: int, message: str):
        """Set conservative underestimate due to no matches."""
        self.set_recall(matched=0, total=total_gt_fields)
        self.status = "no_matches_conservative"
        self.message = message


def get_matching_field_value(item: Dict[str, Any], field_name: str) -> Optional[str]:
    """Get the value of the matching field from an item, or None if missing."""
    value = item.get(field_name)
    if value is not None and str(value).strip() not in ["", "Missing", "None"]:
        return str(value).strip()
    return None


def find_item_matches(gt_items: List[Dict[str, Any]],
                     model_items: List[Dict[str, Any]],
                     matching_field: str) -> Dict[int, List[int]]:
    """
    Find matches between GT and model items based on matching field.

    Returns:
        Dict mapping GT item index to list of model item indices that match
    """
    matches = defaultdict(list)

    for gt_idx, gt_item in enumerate(gt_items):
        gt_value = get_matching_field_value(gt_item, matching_field)
        if gt_value is None:
            continue  # Skip GT items with missing matching field

        for model_idx, model_item in enumerate(model_items):
            model_value = get_matching_field_value(model_item, matching_field)
            if model_value is not None and gt_value == model_value:
                matches[gt_idx].append(model_idx)

    return dict(matches)


def calculate_multi_item_recall(gt_data: Dict[str, Any],
                               model_data: Dict[str, Any],
                               section_name: str) -> MultiItemRecallResult:
    """
    Calculate recall for a multi-item array section.

    Args:
        gt_data: Ground truth JSON data
        model_data: Model output JSON data
        section_name: Name of the array section to compare

    Returns:
        MultiItemRecallResult with recall score and status
    """
    result = MultiItemRecallResult(section_name)

    # Get sections
    gt_section = gt_data.get(section_name, [])
    model_section = model_data.get(section_name, [])

    result.gt_items_count = len(gt_section)
    result.model_items_count = len(model_section)

    # Handle empty sections
    if len(gt_section) == 0:
        result.message = f"Ground truth missing {section_name} section"
        return result

    if len(model_section) == 0:
        # Count all GT fields for conservative penalty
        total_gt_fields = sum(count_non_missing_fields(item) for item in gt_section)
        result.set_conservative_penalty(total_gt_fields, f"Model output missing {section_name} section")
        return result

    # Get matching field
    matching_field = MULTI_ITEM_MATCHING_FIELDS.get(section_name)
    if not matching_field:
        result.message = f"No matching field defined for {section_name}"
        return result

    # Find matches between GT and model items
    matches = find_item_matches(gt_section, model_section, matching_field)

    total_matched_fields = 0
    total_gt_fields = 0
    matched_pairs = 0
    skipped_items = 0

    # Process each GT item
    for gt_idx, gt_item in enumerate(gt_section):
        gt_field_count = count_non_missing_fields(gt_item)

        if gt_idx not in matches:
            # No match found - conservative penalty
            total_gt_fields += gt_field_count
            # No matched fields added (0 matches)
            continue

        model_matches = matches[gt_idx]

        if len(model_matches) > 1:
            # Multiple viable matches - skip scoring but don't penalize
            skipped_items += 1
            continue

        # Exactly one match - perform field-wise comparison
        model_idx = model_matches[0]
        model_item = model_section[model_idx]

        matched_fields, gt_fields = compare_items_fieldwise(gt_item, model_item)
        total_matched_fields += matched_fields
        total_gt_fields += gt_fields
        matched_pairs += 1

    # Set results
    result.set_recall(total_matched_fields, total_gt_fields)
    result.matched_pairs = matched_pairs
    result.skipped_items = skipped_items

    # Determine status and message
    if skipped_items > 0:
        result.status = "multiple_matches_skipped"
        result.message = f"Matched {matched_pairs} pairs, skipped {skipped_items} GT items due to multiple model matches"
    elif total_gt_fields == 0:
        result.message = f"No valid GT items with non-missing {matching_field} field"
    else:
        result.message = f"Matched {matched_pairs} pairs, compared {total_gt_fields} GT fields"

    # Add conservative penalty note if some items had no matches
    unmatched_items = len(gt_section) - matched_pairs - skipped_items
    if unmatched_items > 0:
        if result.status == "success":
            result.status = "no_matches_conservative"
        result.message += f". {unmatched_items} GT items had no matches (conservative penalty)"

    return result


def calculate_cell_line_multi_item_recall(gt_file_path: str,
                                         model_file_path: str) -> Dict[str, MultiItemRecallResult]:
    """
    Calculate multi-item array recall for all relevant sections in a cell line.

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

    # Calculate recall for each multi-item array section
    for section_name in MULTI_ITEM_ARRAYS:
        result = calculate_multi_item_recall(gt_data, model_data, section_name)
        results[section_name] = result

    return results


def print_multi_item_recall_summary(results: Dict[str, MultiItemRecallResult], cell_line_name: str = ""):
    """Print a summary of multi-item recall results."""
    if cell_line_name:
        print(f"\n=== Multi-Item Array Recall Results for {cell_line_name} ===")
    else:
        print(f"\n=== Multi-Item Array Recall Results ===")

    total_matched = 0
    total_fields = 0

    for section_name, result in results.items():
        status_icon = "✓" if result.status == "success" else "⚠" if result.status == "multiple_matches_skipped" else "📉"

        print(f"{status_icon} {section_name}: {result.recall:.3f} ({result.matched_fields}/{result.total_gt_fields}) "
              f"[GT:{result.gt_items_count}, Model:{result.model_items_count}, Pairs:{result.matched_pairs}]")

        if result.message:
            print(f"   {result.message}")

        total_matched += result.matched_fields
        total_fields += result.total_gt_fields

    if total_fields > 0:
        overall_recall = total_matched / total_fields
        print(f"\nOverall Multi-Item Recall: {overall_recall:.3f} ({total_matched}/{total_fields})")
        print("📉 = Conservative underestimate due to no matches")
        print("⚠ = Skipped due to multiple viable matches")
    else:
        print(f"\nNo valid multi-item fields found for recall calculation")


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) != 3:
        print("Usage: python multi_item_recall.py <gt_file.json> <model_file.json>")
        sys.exit(1)

    gt_file = sys.argv[1]
    model_file = sys.argv[2]

    try:
        results = calculate_cell_line_multi_item_recall(gt_file, model_file)
        print_multi_item_recall_summary(results)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)