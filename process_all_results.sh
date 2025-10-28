#!/bin/bash

echo "Processing all remaining results with generate_combined_dataframe.py..."

cd results_processing

echo "Processing gpt-4.1-nano..."
poetry run python generate_combined_dataframe.py --config config_gpt41_nano.json

echo "Processing gpt-5..."
poetry run python generate_combined_dataframe.py --config config_gpt5.json

echo "Processing gpt-5-mini..."
poetry run python generate_combined_dataframe.py --config config_gpt5_mini.json

echo "Processing gpt-5-nano..."
poetry run python generate_combined_dataframe.py --config config_gpt5_nano.json

echo "All processing complete!"