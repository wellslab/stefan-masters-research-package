# Scoring Module

This module provides comprehensive scoring and evaluation metrics for AI model performance in stem cell registry curation tasks.

## Components

### 1. Cell Line Recall (`cell_line_recall/`)

Calculates overall recall performance for cell line curation comparing AI model outputs against manually curated ground truth data.

**Key Features:**
- Single-item array recall (for arrays expected to contain exactly one item)
- Multi-item array recall (with intelligent matching based on key fields)
- Conservative scoring approach that handles edge cases appropriately

**Usage:**
```bash
# Single cell line analysis
poetry run python scoring/cell_line_recall/single_item_recall.py gt_file.json model_file.json
poetry run python scoring/cell_line_recall/multi_item_recall.py gt_file.json model_file.json

# Detailed analysis
poetry run python scoring/cell_line_recall/detailed_analysis.py gt_file.json model_file.json
```

### 2. Field Recall Analysis (`field_recall_scoring/`)

**New Component** - Provides per-field recall analysis across all models to identify which specific fields each model can curate accurately.

**Files:**
- `field_recall_calculation.py` - Core calculation logic
- `generate_field_recall_report.py` - Report generation
- `field_recall_results.json` - Raw results data
- `field_recall_report.md` - Human-readable analysis report

**Key Features:**
- Calculates recall for each individual field across all cell lines
- Aggregates results by model
- Handles both single-item and multi-item array fields
- Generates comprehensive markdown reports with performance insights

**Usage:**
```bash
# Calculate field recall for all models
poetry run python scoring/field_recall_scoring/field_recall_calculation.py

# Generate markdown report
poetry run python scoring/field_recall_scoring/generate_field_recall_report.py
```

## Field Recall Methodology

Field recall is calculated as follows:

1. **For each model**: Iterate through all cell line JSON files
2. **For each field**: Compare model output vs ground truth
3. **Single-item arrays**: Direct field-by-field comparison when both GT and model have exactly 1 item
4. **Multi-item arrays**: Match items using key fields (e.g., `last_name` for contacts), then compare matched pairs
5. **Aggregation**: Sum matches and total GT fields across all cell lines for each field

**Formula**: `Field Recall = (Total Matches) / (Total Non-Missing GT Fields)`

## Output Files

### field_recall_results.json
Raw JSON data containing:
- `field_recall_by_model`: Nested dict of model → field → recall score
- `summary`: Metadata about the analysis

### field_recall_report.md
Comprehensive markdown report including:
- Model performance summary table
- Section-wise field analysis with color-coded performance
- Best and worst performing fields identification
- Model family comparisons (GPT-5 vs GPT-4.1)

## Performance Insights

Based on current analysis:

**Best Performing Fields (Avg Recall ≥ 0.8):**
- Basic identifiers: `hpscreg_name`, `cell_type`
- Publication metadata: `title`, `journal`, `year`, `doi`
- Derivation information: source cell types and origins
- Disease names

**Most Challenging Fields (Avg Recall < 0.2):**
- Free text descriptions: `disease_description`, `genomic_modifications.description`
- Structured IDs: ontology IDs, PMIDs
- Technical details: `approval_date`, `passage_method`

**Model Comparison:**
- GPT-5 family outperforms GPT-4.1 family by ~0.05 on average
- All models struggle with free-text fields and structured identifiers
- All models excel at basic metadata and standardized field values

## Dependencies

- Python 3.8+
- Standard library: `json`, `pathlib`, `collections`
- File structure assumes cleaned results in `results/cleaned_results/`

## File Structure Expected

```
results/cleaned_results/
├── ground_truth/
│   └── {cell_line}_gt.json     # Manual curation ground truth
└── model_output/
    └── {model}/
        └── {cell_line}_m.json  # AI model output
```