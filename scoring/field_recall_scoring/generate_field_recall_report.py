"""
Generate markdown report for field recall results.
"""

import json
from typing import Dict, List, Tuple
from pathlib import Path


def load_field_recall_results(json_file: str) -> Dict:
    """Load field recall results from JSON file."""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_all_fields(results: Dict[str, Dict[str, float]]) -> List[str]:
    """Get all unique fields across all models, sorted by section then field name."""
    all_fields = set()
    for model_results in results.values():
        all_fields.update(model_results.keys())

    # Sort fields by section name first, then field name
    sorted_fields = sorted(all_fields, key=lambda x: (x.split('.')[0], x.split('.')[1]))
    return sorted_fields


def group_fields_by_section(fields: List[str]) -> Dict[str, List[str]]:
    """Group fields by their section name."""
    sections = {}
    for field in fields:
        section, field_name = field.split('.', 1)
        if section not in sections:
            sections[section] = []
        sections[section].append(field)
    return sections


def generate_markdown_report(results: Dict, output_file: str):
    """Generate comprehensive markdown report."""

    field_recall_data = results["field_recall_by_model"]
    summary = results["summary"]

    # Get all models and fields
    models = sorted(field_recall_data.keys())
    all_fields = get_all_fields(field_recall_data)
    sections = group_fields_by_section(all_fields)

    report_lines = []

    # Header
    report_lines.extend([
        "# Field Recall Analysis Report",
        "",
        "This report shows per-field recall performance across all AI models for stem cell registry curation.",
        "",
        f"**Summary Statistics:**",
        f"- Total Models Analyzed: {summary['total_models']}",
        f"- Total Unique Fields: {summary['total_unique_fields']}",
        "",
    ])

    # Overall model performance summary
    report_lines.extend([
        "## Model Performance Summary",
        "",
        "| Model | Avg Recall | Fields Analyzed |",
        "|-------|------------|-----------------|"
    ])

    for model in models:
        model_data = field_recall_data[model]
        avg_recall = sum(model_data.values()) / len(model_data) if model_data else 0
        field_count = len(model_data)
        report_lines.append(f"| {model} | {avg_recall:.3f} | {field_count} |")

    report_lines.extend(["", ""])

    # Section-wise analysis
    report_lines.extend([
        "## Field Recall by Section",
        "",
        "Each section shows recall scores for individual fields across all models.",
        ""
    ])

    for section_name in sorted(sections.keys()):
        section_fields = sections[section_name]

        report_lines.extend([
            f"### {section_name.replace('_', ' ').title()}",
            "",
            "| Field | " + " | ".join(models) + " |",
            "|-------|" + "|".join(["--------"] * len(models)) + "|"
        ])

        for field in sorted(section_fields, key=lambda x: x.split('.')[1]):
            field_name = field.split('.')[1]
            row = [f"**{field_name}**"]

            for model in models:
                recall = field_recall_data[model].get(field, 0.0)
                if recall >= 0.8:
                    cell = f"🟢 {recall:.3f}"
                elif recall >= 0.5:
                    cell = f"🟡 {recall:.3f}"
                elif recall >= 0.2:
                    cell = f"🟠 {recall:.3f}"
                else:
                    cell = f"🔴 {recall:.3f}"
                row.append(cell)

            report_lines.append("| " + " | ".join(row) + " |")

        report_lines.extend(["", ""])

    # Performance insights
    report_lines.extend([
        "## Performance Insights",
        "",
        "### Best Performing Fields (Avg Recall ≥ 0.8)",
        ""
    ])

    # Calculate average recall for each field
    field_averages = {}
    for field in all_fields:
        recalls = [field_recall_data[model].get(field, 0.0) for model in models]
        field_averages[field] = sum(recalls) / len(recalls)

    # Best performing fields
    best_fields = [(field, avg) for field, avg in field_averages.items() if avg >= 0.8]
    best_fields.sort(key=lambda x: x[1], reverse=True)

    if best_fields:
        for field, avg_recall in best_fields:
            section, field_name = field.split('.', 1)
            report_lines.append(f"- **{section}.{field_name}**: {avg_recall:.3f}")
    else:
        report_lines.append("No fields achieved average recall ≥ 0.8 across all models.")

    report_lines.extend(["", "### Challenging Fields (Avg Recall < 0.2)", ""])

    # Worst performing fields
    worst_fields = [(field, avg) for field, avg in field_averages.items() if avg < 0.2]
    worst_fields.sort(key=lambda x: x[1])

    if worst_fields:
        for field, avg_recall in worst_fields:
            section, field_name = field.split('.', 1)
            report_lines.append(f"- **{section}.{field_name}**: {avg_recall:.3f}")
    else:
        report_lines.append("All fields achieved average recall ≥ 0.2 across models.")

    report_lines.extend([
        "",
        "### Model Comparison",
        "",
        "**GPT-5 vs GPT-4.1 Series:**"
    ])

    # Compare model families
    gpt5_models = [m for m in models if m.startswith('gpt-5')]
    gpt41_models = [m for m in models if m.startswith('gpt-4.1')]

    if gpt5_models and gpt41_models:
        gpt5_avg = sum(sum(field_recall_data[m].values()) / len(field_recall_data[m]) for m in gpt5_models) / len(gpt5_models)
        gpt41_avg = sum(sum(field_recall_data[m].values()) / len(field_recall_data[m]) for m in gpt41_models) / len(gpt41_models)

        report_lines.append(f"- GPT-5 family average: {gpt5_avg:.3f}")
        report_lines.append(f"- GPT-4.1 family average: {gpt41_avg:.3f}")

        if gpt5_avg > gpt41_avg:
            report_lines.append(f"- GPT-5 models outperform GPT-4.1 by {gpt5_avg - gpt41_avg:.3f} on average")
        else:
            report_lines.append(f"- GPT-4.1 models outperform GPT-5 by {gpt41_avg - gpt5_avg:.3f} on average")

    report_lines.extend([
        "",
        "---",
        "",
        "**Legend:**",
        "- 🟢 High performance (≥0.8)",
        "- 🟡 Good performance (0.5-0.8)",
        "- 🟠 Moderate performance (0.2-0.5)",
        "- 🔴 Low performance (<0.2)",
        "",
        f"*Report generated from field_recall_results.json*"
    ])

    # Write report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))


if __name__ == "__main__":
    # Default paths
    json_file = "/home/stefanmirandadev/projects/stefan-masters-research-package/scoring/field_recall_scoring/field_recall_results.json"
    output_file = "/home/stefanmirandadev/projects/stefan-masters-research-package/scoring/field_recall_scoring/field_recall_report.md"

    print("Generating field recall markdown report...")

    try:
        results = load_field_recall_results(json_file)
        generate_markdown_report(results, output_file)

        print(f"Report generated successfully: {output_file}")

    except Exception as e:
        print(f"Error generating report: {e}")
        exit(1)