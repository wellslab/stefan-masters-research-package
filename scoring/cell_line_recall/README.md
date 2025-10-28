# Cell Line Recall Calculation

## Overview

This scoring system calculates recall performance for AI models curating stem cell registry data. Models process scientific publications to extract structured cell line information, which is compared against manually curated ground truth data.

## What We're Measuring

**Cell Line Recall**: The proportion of ground truth data fields that the model correctly extracted and matched exactly.

**Formula**: `Recall = (matched non-Missing GT fields) / (total non-Missing GT fields)`

## Data Structure

Each cell line is represented as a JSON object with 13 sections (arrays):

```json
{
  "basic_data": [{"cell_line_name": "...", "source_organism": "..."}],
  "publications": [{"doi": "...", "pmid": "...", "title": "..."}],
  "contact": [{"first_name": "...", "last_name": "...", "email": "..."}],
  "genomic_modifications": [{"loci_name": "...", "type": "..."}],
  // ... 9 more sections
}
```

## Array Classification

### Single-Item Arrays (Expected: 1 item per array)
`publications`, `donor`, `genomic_characterisation`, `induced_derivation`, `culture_medium`, `embryonic_derivation`, `basic_data`, `generator`, `undifferentiated_characterisation`

**Scoring Rules**:
- GT=1, Model=1 → Compare all fields
- GT=1, Model≠1 → Model failed, recall=0 but GT fields count toward denominator
- GT≠1 → Skip (not model's fault)

### Multi-Item Arrays (Expected: 0+ items per array)
`contact`, `genomic_modifications`, `differentiation_results`, `ethics`

**Scoring Rules**:
- Match GT and model items using key fields
- Compare matched pairs field-by-field
- Unmatched GT items contribute 0 matches but count fields toward denominator

## Multi-Item Matching Logic

Items are matched using these key fields:
- `contact` → `last_name`
- `differentiation_results` → `cell_type`
- `ethics` → `ethics_number`
- `genomic_modifications` → `loci_name`

## Field Comparison

- Only non-Missing GT fields are scored (`None`, `""`, `"Missing"` are excluded)
- Exact string match required after `.strip()`
- Conservative scoring: ambiguous cases (multiple matches) are skipped

## Usage

```bash
# Single cell line analysis
poetry run python scoring/cell_line_recall/single_item_recall.py gt_file.json model_file.json
poetry run python scoring/cell_line_recall/multi_item_recall.py gt_file.json model_file.json

# Detailed field-by-field analysis for debugging
poetry run python scoring/cell_line_recall/detailed_analysis.py gt_file.json model_file.json

# Automated workflow (reconstruction + analysis)
poetry run python scripts/update_and_analyze_workflow.py
```

## File Structure

```
results/cleaned_results/
├── ground_truth/
│   └── {cell_line}_gt.json     # Manual curation ground truth
└── model_output/
    └── {model}/
        └── {cell_line}_m.json  # AI model output
```

Example files: `AIBNi017-A_gt.json`, `gpt-4.1/AIBNi017-A_m.json`