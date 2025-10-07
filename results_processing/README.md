# Results Processing Pipeline

This directory contains scripts for processing model output and ground truth data for entity matching and scoring.

## Overview

The pipeline consists of two main scripts:

1. **`generate_combined_dataframe.py`** - Combines model outputs and ground truth into a unified DataFrame
2. **`reconstruct.py`** - Reconstructs JSON files from harmonized DataFrame data

## Workflow

```
Model Output JSONs + Ground Truth JSONs
    ↓ (generate_combined_dataframe.py)
Combined DataFrame with flattened columns
    ↓ (your harmonization work)
Harmonized DataFrame
    ↓ (reconstruct.py)
Cleaned JSON files (ground_truth/ + model_output/)
```

## Scripts

### 1. generate_combined_dataframe.py

**Purpose**: Create a unified DataFrame containing both model outputs and ground truth data.

**Usage**:
```bash
python generate_combined_dataframe.py [--config config_generate.json]
```

**Configuration** (`config_generate.json`):
```json
{
  "results_path": "tests/test_curation/gpt-4/gpt-4o-mini/results/251006_122840",
  "ground_truth_path": "ground_truth",
  "output_filename": "combined_cell_lines_data",
  "save_formats": ["csv"],
  "include_metadata": true,
  "verbose": true
}
```

**What it does**:
- Loads all model output JSONs from the results directory
- Loads all ground truth JSONs
- Analyzes all possible fields across both datasets
- Creates flattened columns for easy editing
- Preserves JSON structure for reconstruction
- Adds proper suffixes: `_m` for model outputs, `_gt` for ground truth
- Saves combined DataFrame and metadata

**Output**:
- `combined_cell_lines_data.csv` - CSV DataFrame
- `combined_cell_lines_data_metadata.json` - Processing metadata

### 2. reconstruct.py

**Purpose**: Reconstruct JSON files from harmonized DataFrame data.

**Usage**:
```bash
python reconstruct.py [--config config_reconstruct.json]
```

**Configuration** (`config_reconstruct.json`):
```json
{
  "dataframe_path": "tests/test_curation/gpt-4/gpt-4o-mini/results/251006_122840/combined_cell_lines_data.csv",
  "output_path": "reconstructed_outputs",
  "ground_truth_folder": "ground_truth",
  "model_output_folder": "model_output",
  "overwrite_existing": true,
  "verbose": true
}
```

**What it does**:
- Loads the harmonized DataFrame
- Separates ground truth and model output rows
- Reconstructs JSON files using **harmonized** flattened columns (not original JSON strings)
- Preserves proper naming conventions
- Creates separate folders for each data type

**Output**:
- `ground_truth/` - Reconstructed ground truth JSONs (with `_gt.json` suffix)
- `model_output/` - Reconstructed model output JSONs (with `_m.json` suffix)
- `reconstruction_metadata.json` - Reconstruction metadata

## Key Features

### Enhanced Field Coverage
- Analyzes **all possible fields** across both datasets
- Ensures no data loss during flattening
- Handles structural differences between model output and ground truth

### Proper Entity Identification
- `hpscreg_name` includes suffixes (`_m` or `_gt`) for clear identification
- `hpscreg_base` provides the base name for matching between datasets
- `data_source` column identifies origin ('model_output' vs 'ground_truth')

### Harmonization-Ready
- Flattened columns for easy bulk editing
- Multiple values separated by " | " for lists
- JSON preservation for perfect reconstruction

### Reconstruction from Harmonized Data
- Uses **edited flattened columns**, not original JSON strings
- Reflects all harmonization changes in output JSONs
- Maintains proper JSON structure and formatting

## Example Workflow

1. **Generate combined DataFrame**:
```bash
python generate_combined_dataframe.py
```

2. **Load and harmonize the data**:
```python
import pandas as pd

# Load the DataFrame
df = pd.read_csv('path/to/combined_cell_lines_data.csv')

# Example harmonization
df.loc[df['generator_group'] == 'AIBN', 'generator_group'] = 'Australian Institute for Bioengineering and Nanotechnology'
df['contact_first_name'] = df['contact_first_name'].str.title()

# Save harmonized version
df.to_csv('path/to/harmonized_data.csv', index=False)
```

3. **Reconstruct cleaned JSONs**:
```bash
# Update config_reconstruct.json to point to harmonized DataFrame
python reconstruct.py
```

## Output Structure

After reconstruction, you'll have:
```
reconstructed_outputs/
├── ground_truth/
│   ├── AIBNi001-A_gt.json
│   ├── AIBNi002-A_gt.json
│   └── ...
├── model_output/
│   ├── AIBNi001-A_m.json
│   ├── AIBNi002-A_m.json
│   └── ...
└── reconstruction_metadata.json
```

## Common Use Cases

### Entity Matching
Compare model outputs vs ground truth for the same cell line:
```python
# Find matching pairs
model_bases = set(df[df['data_source'] == 'model_output']['hpscreg_base'])
gt_bases = set(df[df['data_source'] == 'ground_truth']['hpscreg_base'])
common_bases = model_bases.intersection(gt_bases)

# Compare specific cell line
cell_line = 'AIBNi001-A'
model_row = df[df['hpscreg_name'] == f'{cell_line}_m']
gt_row = df[df['hpscreg_name'] == f'{cell_line}_gt']
```

### Scoring Model Performance
After harmonization, compare values between model and ground truth:
```python
# Compare generator groups for matching cell lines
for base_name in common_bases:
    model_gen = df[df['hpscreg_name'] == f'{base_name}_m']['generator_group'].iloc[0]
    gt_gen = df[df['hpscreg_name'] == f'{base_name}_gt']['generator_group'].iloc[0]
    match = model_gen == gt_gen
    print(f"{base_name}: {match}")
```

## Configuration Notes

- Always use absolute paths in config files
- The `results_path` should point to the specific run directory containing PMID folders
- The `ground_truth_path` should point to the directory containing `*_gt.json` files
- For reconstruction, `dataframe_path` should point to your harmonized DataFrame file

## Troubleshooting

- **Missing files**: Check that paths in config files are correct
- **Permission errors**: Ensure write permissions for output directories
- **Memory issues**: CSV is efficient for large datasets with mostly string data
- **Reconstruction errors**: Check that required columns (`data_source`, `hpscreg_name`) exist in DataFrame