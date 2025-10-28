# Field Results - Detailed Comparison Data

This directory contains detailed field-by-field comparison data between ground truth and model outputs across all models and cell lines.

## Overview

Each JSON file represents one field and contains all comparisons made for that field across all models and cell lines. This provides complete traceability for understanding field performance patterns.

## File Naming Convention

Files are named using the pattern: `{section}_{field}.json`

Examples:
- `basic_data_cell_type.json` - All comparisons for the `basic_data.cell_type` field
- `culture_medium_o2_concentration.json` - All comparisons for the `culture_medium.o2_concentration` field
- `publications_pmid.json` - All comparisons for the `publications.pmid` field

## JSON File Structure

Each field JSON file contains:

```json
{
  "field_path": "section.field_name",
  "summary": {
    "total_comparisons": 37,
    "total_matches": 1,
    "total_model_missing": 25,
    "recall": 0.027
  },
  "comparisons": [
    {
      "model_name": "gpt-4.1",
      "pmid": "12345678",
      "cell_line": "HPIi005-A",
      "ground_truth": "0.2",
      "model_output": "0.21"
    }
  ]
}
```

## Field Descriptions

### Summary Section
- **total_comparisons**: Number of ground truth instances with non-missing values for this field
- **total_matches**: Number of exact string matches between GT and model output
- **total_model_missing**: Number of cases where model didn't provide the field when GT had it
- **recall**: Exact recall score (total_matches / total_comparisons)

### Comparison Record Fields
- **model_name**: Model name (e.g., "gpt-4.1", "gpt-5-nano")
- **pmid**: PubMed ID from the publication (for traceability back to source paper)
- **cell_line**: Cell line identifier (e.g., "HPIi005-A", "AIBNi001-A")
- **ground_truth**: Ground truth value (always non-missing)
- **model_output**: Model output value (can be null/missing)

## Usage Examples

### Find Exact Matches
Look for successful extractions:
```bash
jq '.comparisons[] | select(.ground_truth == .model_output)' culture_medium_o2_concentration.json
```

### Find Precision Issues
Look for cases where model provided a value but it didn't match exactly:
```bash
jq '.comparisons[] | select(.model_output != null and .ground_truth != .model_output)' culture_medium_o2_concentration.json
```

### Filter by Model
Get comparisons for a specific model:
```bash
jq '.comparisons[] | select(.model_name == "gpt-4.1")' basic_data_cell_type.json
```

### Filter by Cell Line
Get comparisons for a specific cell line:
```bash
jq '.comparisons[] | select(.cell_line == "HPIi005-A")' culture_medium_o2_concentration.json
```

### Find Missing Fields
Look for cases where model didn't provide the field:
```bash
jq '.comparisons[] | select(.model_output == null)' publications_pmid.json
```

### Trace Back to Source Papers
Use PMID to investigate specific cases:
```bash
jq '.comparisons[] | select(.pmid == "12345678")' *.json
```

### Analysis Examples

**Precision vs Missing Analysis:**
```bash
# For o2_concentration, see the pattern of precision issues vs missing values
jq '{
  precision_issues: [.comparisons[] | select(.model_output != null and .ground_truth != .model_output)],
  missing_values: [.comparisons[] | select(.model_output == null)]
}' culture_medium_o2_concentration.json
```

**Model Performance Comparison:**
```bash
# Compare recall across models for a specific field
jq '.comparisons | group_by(.model_name) | map({
  model: .[0].model_name,
  total: length,
  matches: [.[] | select(.ground_truth == .model_output)] | length,
  recall: ([.[] | select(.ground_truth == .model_output)] | length) / length
})' basic_data_cell_type.json
```

**Cell Line Analysis:**
```bash
# See which cell lines are most challenging for a specific field
jq '.comparisons | group_by(.cell_line) | map({
  cell_line: .[0].cell_line,
  total: length,
  matches: [.[] | select(.ground_truth == .model_output)] | length,
  recall: ([.[] | select(.ground_truth == .model_output)] | length) / length
}) | sort_by(.recall)' culture_medium_o2_concentration.json
```

This structure makes it easy to quickly understand what values each model is producing for each field and how they compare to the ground truth, with full traceability back to specific cell lines and publications.