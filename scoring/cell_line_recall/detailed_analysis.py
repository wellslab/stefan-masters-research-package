#!/usr/bin/env python3
"""
Detailed field-by-field recall analysis for cell line JSON data.

This script provides granular analysis showing exactly which fields match
and which don't for debugging and understanding recall performance.
"""

import sys
import json
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from scoring.cell_line_recall.single_item_recall import load_json_file, compare_items_fieldwise
from scoring.cell_line_recall.multi_item_recall import find_item_matches, MULTI_ITEM_MATCHING_FIELDS


def detailed_field_comparison(gt_item, model_item, section_name):
    """Show detailed field-by-field comparison."""
    print(f"\n--- {section_name} Field-by-Field Comparison ---")
    matched = 0
    total = 0

    for field_name, gt_value in gt_item.items():
        # Only process non-missing GT fields
        if gt_value is not None and str(gt_value).strip() not in ["", "Missing", "None"]:
            total += 1
            model_value = model_item.get(field_name, "MISSING")

            if str(gt_value).strip() == str(model_value).strip():
                print(f"  ✓ {field_name}: '{gt_value}' == '{model_value}'")
                matched += 1
            else:
                print(f"  ✗ {field_name}: GT='{gt_value}' vs Model='{model_value}'")

    print(f"  → Result: {matched}/{total} fields matched")
    return matched, total


def analyze_single_item_arrays(gt_data, model_data):
    """Analyze single-item arrays with detailed field comparisons."""
    print("\n🔍 SINGLE-ITEM ARRAYS:")

    single_item_arrays = [
        'publications', 'donor', 'genomic_characterisation', 'induced_derivation',
        'culture_medium', 'embryonic_derivation', 'basic_data', 'generator',
        'undifferentiated_characterisation'
    ]

    total_matched = 0
    total_fields = 0

    for i, section_name in enumerate(single_item_arrays, 1):
        gt_section = gt_data.get(section_name, [])
        model_section = model_data.get(section_name, [])

        print(f"\n{i}. {section_name.upper()} (single-item):")
        print(f"   GT has {len(gt_section)} items, Model has {len(model_section)} items")

        if len(gt_section) == 1 and len(model_section) == 1:
            matched, total = detailed_field_comparison(gt_section[0], model_section[0], section_name)
            total_matched += matched
            total_fields += total
        elif len(gt_section) == 0:
            print("   → GT section missing")
        elif len(model_section) == 0:
            print("   → Model section missing")
        elif len(gt_section) > 1:
            print(f"   → GT has multiple items ({len(gt_section)}), expected 1")
        elif len(model_section) > 1:
            print(f"   → Model has multiple items ({len(model_section)}), expected 1")

    print(f"\n📊 Single-Item Arrays Summary: {total_matched}/{total_fields} = {total_matched/total_fields:.3f}")
    return total_matched, total_fields


def analyze_multi_item_arrays(gt_data, model_data):
    """Analyze multi-item arrays with detailed matching logic."""
    print("\n🔍 MULTI-ITEM ARRAYS:")

    multi_item_arrays = ['contact', 'genomic_modifications', 'differentiation_results', 'ethics']

    total_matched = 0
    total_fields = 0

    for i, section_name in enumerate(multi_item_arrays, 1):
        gt_section = gt_data.get(section_name, [])
        model_section = model_data.get(section_name, [])

        print(f"\n{i}. {section_name.upper()} (multi-item, match on {MULTI_ITEM_MATCHING_FIELDS.get(section_name, 'N/A')}):")
        print(f"   GT has {len(gt_section)} items, Model has {len(model_section)} items")

        if not gt_section:
            print("   → GT section missing")
            continue

        if not model_section:
            print("   → Model section missing")
            continue

        # Show matching process
        matching_field = MULTI_ITEM_MATCHING_FIELDS.get(section_name)
        if matching_field:
            matches = find_item_matches(gt_section, model_section, matching_field)
            print(f"   Found matches: {dict(matches)}")

            section_matched = 0
            section_total = 0

            for gt_idx, gt_item in enumerate(gt_section):
                gt_match_value = gt_item.get(matching_field, 'MISSING')
                print(f"\n   GT Item {gt_idx} ({matching_field}='{gt_match_value}'):")

                if gt_idx in matches:
                    model_matches = matches[gt_idx]
                    if len(model_matches) == 1:
                        model_idx = model_matches[0]
                        model_item = model_section[model_idx]
                        model_match_value = model_item.get(matching_field, 'MISSING')
                        print(f"   → Matched with Model Item {model_idx} ({matching_field}='{model_match_value}')")
                        matched, total = detailed_field_comparison(gt_item, model_item, f"{section_name}[{gt_idx}→{model_idx}]")
                        section_matched += matched
                        section_total += total
                    else:
                        print(f"   → Multiple matches found: {model_matches} (SKIPPED)")
                        # Still count GT fields for conservative penalty understanding
                        for field_name, gt_value in gt_item.items():
                            if gt_value is not None and str(gt_value).strip() not in ["", "Missing", "None"]:
                                print(f"      - GT field '{field_name}': '{gt_value}' (not scored due to multiple matches)")
                else:
                    print(f"   → No match found (CONSERVATIVE PENALTY)")
                    # Count GT fields that contribute to denominator
                    gt_field_count = 0
                    for field_name, gt_value in gt_item.items():
                        if gt_value is not None and str(gt_value).strip() not in ["", "Missing", "None"]:
                            gt_field_count += 1
                            print(f"      - GT field '{field_name}': '{gt_value}' (penalty)")
                    section_total += gt_field_count

            total_matched += section_matched
            total_fields += section_total
            print(f"   → Section Result: {section_matched}/{section_total} fields matched")

    print(f"\n📊 Multi-Item Arrays Summary: {total_matched}/{total_fields} = {total_matched/total_fields:.3f}")
    return total_matched, total_fields


def analyze_cell_line_detailed(gt_file_path: str, model_file_path: str, cell_line_name: str = ""):
    """Perform detailed analysis of a single cell line."""
    print(f"=== Detailed Cell Line Recall Analysis{' for ' + cell_line_name if cell_line_name else ''} ===")

    # Load data
    gt_data = load_json_file(gt_file_path)
    model_data = load_json_file(model_file_path)

    # Analyze single-item arrays
    single_matched, single_total = analyze_single_item_arrays(gt_data, model_data)

    # Analyze multi-item arrays
    multi_matched, multi_total = analyze_multi_item_arrays(gt_data, model_data)

    # Overall summary
    total_matched = single_matched + multi_matched
    total_fields = single_total + multi_total

    print(f"\n🎯 OVERALL RECALL SUMMARY")
    print("=" * 40)
    print(f"Single-Item Arrays: {single_matched}/{single_total} = {single_matched/single_total:.3f}")
    print(f"Multi-Item Arrays:  {multi_matched}/{multi_total} = {multi_matched/multi_total:.3f}")
    print(f"Combined Recall:    {total_matched}/{total_fields} = {total_matched/total_fields:.3f}")


def main():
    """Main entry point for detailed analysis."""
    if len(sys.argv) != 3:
        print("Usage: python detailed_analysis.py <gt_file.json> <model_file.json>")
        print("\nExample:")
        print("  python detailed_analysis.py ../../results/cleaned_results/ground_truth/AIBNi017-A_gt.json ../../results/cleaned_results/model_output/gpt-4.1/AIBNi017-A_m.json")
        sys.exit(1)

    gt_file = sys.argv[1]
    model_file = sys.argv[2]

    # Extract cell line name from filename
    cell_line_name = Path(gt_file).stem.replace('_gt', '')

    try:
        analyze_cell_line_detailed(gt_file, model_file, cell_line_name)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()