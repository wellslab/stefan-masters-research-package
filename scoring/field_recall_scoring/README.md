# Field Recall Scoring

This directory contains tools for calculating per-field recall performance across AI models for stem cell registry curation.

## Overview

Field recall provides granular insights into which specific fields each model can curate accurately versus which fields remain challenging. This helps identify model strengths/weaknesses and guide improvement efforts.

## Files

### Core Scripts

- **`field_recall_calculation.py`** - Main calculation script that processes all models and generates field recall data
- **`generate_field_recall_report.py`** - Report generator that creates human-readable markdown analysis
- **`age_range_correction.py`** - Semantic analysis for age field corrections

### Output Files

- **`field_recall_results.json`** - Raw field recall data in JSON format
- **`field_recall_report.md`** - Comprehensive markdown report with tables and insights
- **`field_results/`** - Directory containing detailed comparison data for each field

## Usage

### Calculate Field Recall for All Models

```bash
# Run from project root directory
poetry run python scoring/field_recall_scoring/field_recall_calculation.py
```

This will:
1. Process all model directories in `results/cleaned_results/model_output/`
2. Compare against ground truth files in `results/cleaned_results/ground_truth/`
3. Calculate recall for each field across all cell lines
4. Save results to `field_recall_results.json`

### Generate Markdown Report

```bash
# Run from project root directory
poetry run python scoring/field_recall_scoring/generate_field_recall_report.py
```

This will:
1. Load data from `field_recall_results.json`
2. Generate comprehensive analysis with tables and insights
3. Save report to `field_recall_report.md`

### Generate Detailed Field Comparison Data

```bash
# Run from project root directory
poetry run python scoring/field_recall_scoring/generate_field_results.py
```

This will:
1. Process all model outputs and ground truth data
2. Generate detailed comparison records for each field
3. Save individual JSON files in `field_results/` directory
4. Include model name, PMID, and traceability information for each comparison


## Methodology

### Field Recall Calculation

For each model and each field:

1. **Iterate through all cell line JSON files** for the model
2. **Extract field values** from both model output and ground truth
3. **Handle array types appropriately**:
   - **Single-item arrays**: Direct comparison when both have exactly 1 item
   - **Multi-item arrays**: Match items using key fields, then compare matched pairs
4. **Count matches and totals** across all cell lines
5. **Calculate recall**: `Matches / Total_GT_Fields`

### Array Handling

**Single-item arrays** (expected to contain exactly 1 item):
- `publications`, `donor`, `genomic_characterisation`, `induced_derivation`, `culture_medium`, `embryonic_derivation`, `basic_data`, `generator`, `undifferentiated_characterisation`

**Multi-item arrays** (can contain 0+ items):
- `contact` (matched by `last_name`)
- `genomic_modifications` (matched by `loci_name`)
- `differentiation_results` (matched by `cell_type`)
- `ethics` (matched by `ethics_number`)

### Conservative Scoring

- Only non-missing ground truth fields are scored (`None`, `""`, `"Missing"` excluded)
- Exact string match required (after `.strip()`)
- Multi-item matching is conservative (skips ambiguous cases with multiple matches)
- Unmatched GT items contribute to denominator but not numerator

## Output Format

### field_recall_results.json Structure

```json
{
  "field_recall_by_model": {
    "gpt-4.1": {
      "basic_data.cell_type": 0.988,
      "publications.title": 0.954,
      "contact.last_name": 0.721,
      ...
    },
    "gpt-5": {
      ...
    }
  },
  "summary": {
    "total_models": 6,
    "total_unique_fields": 48
  }
}
```

### Report Contents

The markdown report includes:

1. **Model Performance Summary** - Average recall and field count per model
2. **Field Recall by Section** - Color-coded tables showing recall for each field
3. **Performance Insights**:
   - Best performing fields (≥0.8 average recall)
   - Most challenging fields (<0.2 average recall)
   - Model family comparisons (GPT-5 vs GPT-4.1)

## Performance Legend

- 🟢 High performance (≥0.8)
- 🟡 Good performance (0.5-0.8)
- 🟠 Moderate performance (0.2-0.5)
- 🔴 Low performance (<0.2)

## Key Insights

Based on current analysis:

**Models excel at**:
- Basic identifiers (`hpscreg_name`, `cell_type`)
- Publication metadata (`title`, `journal`, `year`)
- Standard terminology (`disease_name`, source cell types)

**Models struggle with**:
- Free text descriptions (`disease_description`, `summary`)
- Structured identifiers (PMIDs, ontology IDs)
- Technical details requiring domain knowledge

**Model comparison**:
- GPT-5 family outperforms GPT-4.1 family by ~0.05 on average
- Performance varies significantly by field type rather than just model version