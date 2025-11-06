# Model Results

This directory contains field recall scores organized by model.

## Structure

Each model has its own directory containing individual JSON files for each field:

```
model_results/
├── gpt-4.1/
│   ├── basic_data_cell_type.json
│   ├── basic_data_frozen.json
│   └── ... (all fields)
├── gpt-4.1-mini/
│   ├── basic_data_cell_type.json
│   └── ... (all fields)
└── ... (all models)
```

## Models

- 6 total models evaluated
- Models: gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, gpt-5, gpt-5-mini, gpt-5-nano

## Fields

- 49 total unique fields
- Each model directory contains 49 field files

## File Format

Each field file contains:
```json
{
  "model_name": "model_name",
  "field_path": "category.field_name", 
  "recall_score": 0.85,
  "metadata": {
    "total_models_evaluated": 6,
    "total_unique_fields": 49
  }
}
```

Generated from field_recall_results.json
