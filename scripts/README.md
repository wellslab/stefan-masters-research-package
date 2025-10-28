# Automated Workflow Scripts

## update_and_analyze_workflow.py

Automates the common sequence of updating CSV data and running recall analysis.

### Usage

```bash
# Full workflow (reconstruction + analysis)
poetry run python scripts/update_and_analyze_workflow.py

# Skip reconstruction if JSON files are already up to date
poetry run python scripts/update_and_analyze_workflow.py --skip-reconstruction

# Analyze specific cell lines
poetry run python scripts/update_and_analyze_workflow.py --sample-cell-lines AIBNi017-A,MCRIi010-A

# Analyze different model
poetry run python scripts/update_and_analyze_workflow.py --model gpt-5
```

### What it does

1. **Reconstruction** (unless skipped):
   - Runs `reconstruct_from_combined.py` with the cleaned CSV data
   - Recreates all JSON files in `results/cleaned_results/`

2. **Recall Analysis**:
   - Tests single-item array recall for each sample cell line (`scoring/cell_line_recall/single_item_recall.py`)
   - Tests multi-item array recall for each sample cell line (`scoring/cell_line_recall/multi_item_recall.py`)
   - Shows detailed field-by-field comparisons

3. **Summary Report**:
   - Displays success/failure status for each cell line
   - Saves detailed results to `workflow_results.json`

### Common Workflow

After updating `results_processing/cleaned_results/combined_dataframe_clean.csv`:

```bash
# Update JSON files and test with default samples
poetry run python scripts/update_and_analyze_workflow.py

# Or just test specific cell lines if JSONs are current
poetry run python scripts/update_and_analyze_workflow.py --skip-reconstruction --sample-cell-lines YOUR_CELL_LINE
```

### Output

- Console output shows detailed recall analysis
- `workflow_results.json` contains structured results
- Both single-item and multi-item array recall scores