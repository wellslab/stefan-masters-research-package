"""
Age range correction analysis for donor.age field.

Compares exact string matching vs semantically correct age range matching.
"""

import json
import re
from typing import Dict, Any, Optional, Tuple
from pathlib import Path


def parse_age_range(age_str: str) -> Optional[Tuple[int, int]]:
    """
    Parse age range string into (min_age, max_age) tuple.

    Handles formats like:
    - "20_30" -> (20, 30)
    - "25_29" -> (25, 29)
    - "35_39" -> (35, 39)

    Returns None if format not recognized.
    """
    if not age_str or str(age_str).strip() in ["", "Missing", "None"]:
        return None

    age_str = str(age_str).strip()

    # Handle range format like "20_30"
    if '_' in age_str:
        try:
            parts = age_str.split('_')
            if len(parts) == 2:
                min_age = int(parts[0])
                max_age = int(parts[1])
                return (min_age, max_age)
        except ValueError:
            pass

    return None


def parse_single_age(age_str: str) -> Optional[int]:
    """
    Parse single age value.

    Returns the age as integer, or None if not parseable.
    """
    if not age_str or str(age_str).strip() in ["", "Missing", "None"]:
        return None

    age_str = str(age_str).strip()

    try:
        return int(float(age_str))  # Handle "25.0" -> 25
    except ValueError:
        return None


def is_age_in_range(age: int, age_range: Tuple[int, int]) -> bool:
    """Check if single age falls within the given range (inclusive)."""
    min_age, max_age = age_range
    return min_age <= age <= max_age


def ages_are_semantically_equivalent(gt_value: str, model_value: str) -> bool:
    """
    Check if two age values are semantically equivalent.

    Handles cases like:
    - GT: "25_29", Model: "27" -> True (27 is in range 25-29)
    - GT: "25_29", Model: "32" -> False (32 is not in range 25-29)
    - GT: "25_29", Model: "25_29" -> True (exact match)
    """
    if not gt_value or not model_value:
        return False

    # Try exact string match first
    if str(gt_value).strip() == str(model_value).strip():
        return True

    # Parse GT as range
    gt_range = parse_age_range(gt_value)
    if gt_range:
        # GT is a range, check if model age falls in range
        model_age = parse_single_age(model_value)
        if model_age is not None:
            return is_age_in_range(model_age, gt_range)

        # Model might also be a range
        model_range = parse_age_range(model_value)
        if model_range:
            # Both are ranges - check if they overlap significantly
            gt_min, gt_max = gt_range
            model_min, model_max = model_range
            # Ranges are equivalent if they're the same
            return gt_min == model_min and gt_max == model_max

    # Parse GT as single age
    gt_age = parse_single_age(gt_value)
    if gt_age is not None:
        # GT is single age, check if model range contains it
        model_range = parse_age_range(model_value)
        if model_range:
            return is_age_in_range(gt_age, model_range)

        # Both are single ages
        model_age = parse_single_age(model_value)
        if model_age is not None:
            return gt_age == model_age

    return False


def analyze_age_field_corrections(field_results_file: str) -> Dict[str, Any]:
    """
    Analyze the donor.age field with and without age range corrections.

    Returns comparison of exact vs semantic matching.
    """
    with open(field_results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    comparisons = data.get('comparisons', [])

    # Calculate exact matches (current system)
    exact_matches = 0
    semantic_matches = 0
    total_comparisons = len(comparisons)

    # Detailed breakdown
    exact_match_cases = []
    semantic_only_cases = []  # Cases that match semantically but not exactly
    no_match_cases = []

    for comp in comparisons:
        gt_value = comp.get('ground_truth')
        model_value = comp.get('model_output')

        # Skip if model didn't provide value
        if model_value is None:
            no_match_cases.append({
                'reason': 'model_missing',
                'comparison': comp
            })
            continue

        # Check exact match
        is_exact_match = str(gt_value).strip() == str(model_value).strip()
        if is_exact_match:
            exact_matches += 1
            exact_match_cases.append(comp)

        # Check semantic match
        is_semantic_match = ages_are_semantically_equivalent(gt_value, model_value)
        if is_semantic_match:
            semantic_matches += 1
            if not is_exact_match:
                semantic_only_cases.append(comp)
        else:
            if model_value is not None:  # Only count as no match if model provided something
                no_match_cases.append({
                    'reason': 'semantic_mismatch',
                    'comparison': comp
                })

    # Calculate recall scores
    exact_recall = exact_matches / total_comparisons if total_comparisons > 0 else 0
    semantic_recall = semantic_matches / total_comparisons if total_comparisons > 0 else 0

    return {
        'field_path': data.get('field_path'),
        'total_comparisons': total_comparisons,
        'exact_matching': {
            'matches': exact_matches,
            'recall': exact_recall,
            'cases': exact_match_cases
        },
        'semantic_matching': {
            'matches': semantic_matches,
            'recall': semantic_recall,
            'improvement': semantic_matches - exact_matches,
            'improvement_rate': (semantic_matches - exact_matches) / total_comparisons if total_comparisons > 0 else 0
        },
        'semantic_only_cases': semantic_only_cases,
        'no_match_cases': no_match_cases,
        'summary': {
            'exact_recall': exact_recall,
            'semantic_recall': semantic_recall,
            'recall_improvement': semantic_recall - exact_recall,
            'cases_corrected': len(semantic_only_cases)
        }
    }


def generate_age_correction_report(analysis: Dict[str, Any], output_file: str):
    """Generate markdown report for age range correction analysis."""

    lines = [
        "# Age Range Correction Analysis",
        "",
        "Analysis of the `donor.age` field comparing exact string matching vs semantically correct age range matching.",
        "",
        "## Summary",
        "",
        f"- **Total Comparisons**: {analysis['total_comparisons']}",
        f"- **Exact String Recall**: {analysis['summary']['exact_recall']:.3f}",
        f"- **Semantic Range Recall**: {analysis['summary']['semantic_recall']:.3f}",
        f"- **Recall Improvement**: +{analysis['summary']['recall_improvement']:.3f} ({analysis['summary']['cases_corrected']} cases corrected)",
        "",
        "## Methodology",
        "",
        "**Exact Matching**: Requires identical strings (e.g., GT: `\"25_29\"` vs Model: `\"25_29\"`)",
        "",
        "**Semantic Matching**: Handles age ranges intelligently:",
        "- GT: `\"25_29\"`, Model: `\"27\"` → ✅ Match (27 is within 25-29 range)",
        "- GT: `\"25_29\"`, Model: `\"32\"` → ❌ No match (32 is outside 25-29 range)",
        "- GT: `\"25_29\"`, Model: `\"25_29\"` → ✅ Match (exact match)",
        "",
    ]

    # Performance comparison table
    lines.extend([
        "## Performance Comparison",
        "",
        "| Matching Type | Matches | Total | Recall | Improvement |",
        "|---------------|---------|-------|--------|-------------|",
        f"| Exact String | {analysis['exact_matching']['matches']} | {analysis['total_comparisons']} | {analysis['exact_matching']['recall']:.3f} | - |",
        f"| Semantic Range | {analysis['semantic_matching']['matches']} | {analysis['total_comparisons']} | {analysis['semantic_matching']['recall']:.3f} | +{analysis['semantic_matching']['improvement']} cases |",
        "",
    ])

    # Show semantic-only corrections
    if analysis['semantic_only_cases']:
        lines.extend([
            "## Cases Corrected by Semantic Matching",
            "",
            "These cases failed exact string matching but succeeded with semantic range matching:",
            "",
            "| Model | PMID | Cell Line | Ground Truth | Model Output | Explanation |",
            "|-------|------|-----------|--------------|--------------|-------------|"
        ])

        for case in analysis['semantic_only_cases'][:10]:  # Show first 10 cases
            gt_val = case['ground_truth']
            model_val = case['model_output']

            # Generate explanation
            gt_range = parse_age_range(gt_val)
            model_age = parse_single_age(model_val)

            if gt_range and model_age:
                explanation = f"Age {model_age} falls within range {gt_range[0]}-{gt_range[1]}"
            else:
                explanation = "Semantic equivalence"

            lines.append(f"| {case['model_name']} | {case['pmid']} | {case['cell_line']} | `{gt_val}` | `{model_val}` | {explanation} |")

        if len(analysis['semantic_only_cases']) > 10:
            lines.append(f"*... and {len(analysis['semantic_only_cases']) - 10} more cases*")

        lines.extend(["", ""])

    # Show remaining mismatches
    semantic_mismatches = [case for case in analysis['no_match_cases'] if case['reason'] == 'semantic_mismatch']
    if semantic_mismatches:
        lines.extend([
            "## Remaining Semantic Mismatches",
            "",
            "Cases where even semantic matching failed:",
            "",
            "| Model | PMID | Cell Line | Ground Truth | Model Output | Issue |",
            "|-------|------|-----------|--------------|--------------|-------|"
        ])

        for case_info in semantic_mismatches[:5]:  # Show first 5 cases
            case = case_info['comparison']
            gt_val = case['ground_truth']
            model_val = case['model_output']

            # Analyze why it failed
            gt_range = parse_age_range(gt_val)
            model_age = parse_single_age(model_val)

            if gt_range and model_age:
                if not is_age_in_range(model_age, gt_range):
                    issue = f"Age {model_age} outside range {gt_range[0]}-{gt_range[1]}"
                else:
                    issue = "Parsing issue"
            else:
                issue = "Unparseable format"

            lines.append(f"| {case['model_name']} | {case['pmid']} | {case['cell_line']} | `{gt_val}` | `{model_val}` | {issue} |")

        if len(semantic_mismatches) > 5:
            lines.append(f"*... and {len(semantic_mismatches) - 5} more cases*")

        lines.extend(["", ""])

    lines.extend([
        "## Implications",
        "",
        f"Semantic age range matching improves recall by **{analysis['summary']['recall_improvement']:.1%}** for the `donor.age` field.",
        "",
        "This demonstrates the importance of domain-aware evaluation metrics that understand:",
        "- Age ranges vs specific ages",
        "- Semantic equivalence beyond exact string matching",
        "- Field-specific validation logic",
        "",
        "**Recommendation**: Implement semantic validation for age fields in production systems."
    ])

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


if __name__ == "__main__":
    # Default paths
    field_results_dir = "/home/stefanmirandadev/projects/stefan-masters-research-package/scoring/field_recall_scoring/field_results"
    age_field_file = f"{field_results_dir}/donor_age.json"
    output_file = "/home/stefanmirandadev/projects/stefan-masters-research-package/scoring/field_recall_scoring/age_range_correction_report.md"

    print("Analyzing age range corrections for donor.age field...")

    try:
        # Analyze age field corrections
        analysis = analyze_age_field_corrections(age_field_file)

        # Generate report
        generate_age_correction_report(analysis, output_file)

        print(f"Age correction analysis completed!")
        print(f"Report saved to: {output_file}")
        print(f"\nSummary:")
        print(f"  Exact recall: {analysis['summary']['exact_recall']:.3f}")
        print(f"  Semantic recall: {analysis['summary']['semantic_recall']:.3f}")
        print(f"  Improvement: +{analysis['summary']['recall_improvement']:.3f} ({analysis['summary']['cases_corrected']} cases)")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)