import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any


def load_config() -> Dict:
    """Load configuration from config.json"""
    config_path = Path(__file__).parent / "config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Config file not found at {config_path}")
        return {"field_types": {"scalar_fields": [], "object_fields": []}}
    except json.JSONDecodeError as e:
        print(f"Warning: Invalid JSON in config file: {e}")
        return {"field_types": {"scalar_fields": [], "object_fields": []}}


def flatten_object_field(field_name: str, field_value: Dict) -> Dict[str, Any]:
    """
    Flatten an object field into scalar fields with underscore naming.
    
    Args:
        field_name: The parent field name
        field_value: The object containing nested fields
        
    Returns:
        Dictionary of flattened field_name_subfield: value pairs
    """
    flattened = {}
    if isinstance(field_value, dict):
        for sub_field, sub_value in field_value.items():
            flattened_key = f"{field_name}_{sub_field}"
            flattened[flattened_key] = sub_value
    return flattened


def get_per_field_results(path_to_results: str) -> Dict[str, List[Tuple[str, Any]]]:
    """
    Process JSON result files and organize metadata by field.
    
    Args:
        path_to_results: Path to directory containing JSON result files
        
    Returns:
        Dictionary where keys are field names and values are lists of tuples
        containing (stem_cell_line_name, field_value). Object fields are flattened
        into separate scalar fields using underscore naming.
    """
    config = load_config()
    object_fields = set(config.get("field_types", {}).get("object_fields", []))
    
    results_dict = {}
    results_path = Path(path_to_results)
    
    if not results_path.exists():
        raise FileNotFoundError(f"Results path does not exist: {path_to_results}")
    
    # Process all JSON files in the directory
    for json_file in results_path.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract stem cell line name from filename or data
            stem_cell_line_name = json_file.stem  # Use filename without extension
            
            # If there's a specific field for the line name in the JSON, use that instead
            if 'line_name' in data:
                stem_cell_line_name = data['line_name']
            elif 'stem_cell_line' in data:
                stem_cell_line_name = data['stem_cell_line']
            elif 'name' in data:
                stem_cell_line_name = data['name']
            
            # Process each field in the JSON object
            for field_name, field_value in data.items():
                if field_name in object_fields and isinstance(field_value, dict):
                    # Flatten object fields
                    flattened_fields = flatten_object_field(field_name, field_value)
                    for flattened_key, flattened_value in flattened_fields.items():
                        if flattened_key not in results_dict:
                            results_dict[flattened_key] = []
                        results_dict[flattened_key].append((stem_cell_line_name, flattened_value))
                else:
                    # Handle scalar fields normally
                    if field_name not in results_dict:
                        results_dict[field_name] = []
                    results_dict[field_name].append((stem_cell_line_name, field_value))
                
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse JSON file {json_file}: {e}")
            continue
        except Exception as e:
            print(f"Warning: Error processing file {json_file}: {e}")
            continue
    
    return results_dict