#!/usr/bin/env python3
"""
Generate model-based field recall results.

Reads from field_results/ directory and creates model folders with individual field files
containing the raw comparison data for each model.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List
import glob


def load_field_results(field_results_dir: str) -> Dict[str, Any]:
    """Load all field result files from the field_results directory."""
    field_data = {}
    field_files = glob.glob(os.path.join(field_results_dir, "*.json"))
    
    for file_path in field_files:
        filename = Path(file_path).stem
        # Skip non-field files
        if filename in ['README', 'visualisation']:
            continue
            
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
                field_data[filename] = data
            except json.JSONDecodeError:
                print(f"Warning: Could not parse {file_path}")
                continue
    
    return field_data


def get_all_models(field_data: Dict[str, Any]) -> List[str]:
    """Extract all unique model names from the field data."""
    models = set()
    for field_name, data in field_data.items():
        if 'comparisons' in data:
            for comparison in data['comparisons']:
                models.add(comparison['model_name'])
    return sorted(list(models))


def create_model_directories(base_path: str, models: List[str]) -> None:
    """Create directories for each model."""
    for model in models:
        model_dir = Path(base_path) / "model_results" / model
        model_dir.mkdir(parents=True, exist_ok=True)


def generate_model_field_files(field_data: Dict[str, Any], base_path: str) -> None:
    """Generate individual field files for each model with raw comparison data."""
    models = get_all_models(field_data)
    
    # Create model directories
    create_model_directories(base_path, models)
    
    # Process each field and organize by model
    for field_filename, field_info in field_data.items():
        field_path = field_info.get('field_path', field_filename.replace('_', '.'))
        
        # Group comparisons by model
        model_comparisons = {}
        for comparison in field_info.get('comparisons', []):
            model_name = comparison['model_name']
            if model_name not in model_comparisons:
                model_comparisons[model_name] = []
            model_comparisons[model_name].append(comparison)
        
        # Create field file for each model
        for model_name in models:
            model_dir = Path(base_path) / "model_results" / model_name
            file_path = model_dir / f"{field_filename}.json"
            
            # Get comparisons for this model
            comparisons = model_comparisons.get(model_name, [])
            
            # Calculate model-specific metrics
            total_comparisons = len(comparisons)
            total_matches = sum(1 for comp in comparisons 
                              if comp.get('ground_truth') == comp.get('model_output'))
            recall = total_matches / total_comparisons if total_comparisons > 0 else 0.0
            
            # Create model-specific field data
            model_field_data = {
                "model_name": model_name,
                "field_path": field_path,
                "summary": {
                    "total_comparisons": total_comparisons,
                    "total_matches": total_matches,
                    "recall": recall
                },
                "comparisons": comparisons
            }
            
            # Write field file
            with open(file_path, 'w') as f:
                json.dump(model_field_data, f, indent=2)
    
    print(f"Generated model results for {len(models)} models")
    print(f"Each model has {len(field_data)} field files")
    print(f"Total files created: {len(models) * len(field_data)}")
    
    # Create summary file
    summary_path = Path(base_path) / "model_results" / "README.md"
    create_summary_readme(summary_path, models, list(field_data.keys()))


def create_summary_readme(file_path: Path, models: list, fields: list) -> None:
    """Create a README file explaining the model results structure."""
    content = f"""# Model Results

This directory contains field recall scores organized by model.

## Structure

Each model has its own directory containing individual JSON files for each field:

```
model_results/
├── {models[0]}/
│   ├── basic_data_cell_type.json
│   ├── basic_data_frozen.json
│   └── ... (all fields)
├── {models[1]}/
│   ├── basic_data_cell_type.json
│   └── ... (all fields)
└── ... (all models)
```

## Models

- {len(models)} total models evaluated
- Models: {', '.join(models)}

## Fields

- {len(fields)} total unique fields
- Each model directory contains {len(fields)} field files

## File Format

Each field file contains:
```json
{{
  "model_name": "model_name",
  "field_path": "category.field_name", 
  "recall_score": 0.85,
  "metadata": {{
    "total_models_evaluated": {len(models)},
    "total_unique_fields": {len(fields)}
  }}
}}
```

Generated from field_recall_results.json
"""
    
    with open(file_path, 'w') as f:
        f.write(content)


def main():
    """Main function to generate model-based field results."""
    # Set up paths
    script_dir = Path(__file__).parent
    field_results_dir = script_dir / "field_results"
    
    if not field_results_dir.exists():
        print(f"Error: {field_results_dir} not found!")
        return
    
    # Load data from field_results directory
    print(f"Loading field results from {field_results_dir}")
    field_data = load_field_results(str(field_results_dir))
    
    if not field_data:
        print("Error: No field data files found!")
        return
    
    # Generate model results
    print("Generating model-based field results with raw comparison data...")
    generate_model_field_files(field_data, str(script_dir))
    
    print(f"Model results generated in: {script_dir}/model_results/")


if __name__ == "__main__":
    main()