# Project TODOs

## Ground Truth Data Updates

### 1. Update ground truth creation script to include hpscreg_name in basic_data section
- **Location**: `database_connection.ipynb`
- **Action**: Modify the basic_data section generation to include the `hpscreg_name` field
- **Current structure**:
  ```json
  "basic_data": [
    {
      "cell_line_alt_name": "GENIE 1",
      "cell_type": "hiPSC",
      "frozen": "True"
    }
  ]
  ```
- **Target structure**:
  ```json
  "basic_data": [
    {
      "hpscreg_name": "AIBNi001-A",
      "cell_line_alt_name": "GENIE 1",
      "cell_type": "hiPSC",
      "frozen": "True"
    }
  ]
  ```

### 2. Add differentiation_profile field to ground truth data
- **Location**: `database_connection.ipynb` - differentiation results section
- **Action**: Add `differentiation_profile` field to the differentiation_results data generation
- **Current structure**:
  ```json
  "differentiation_results": [
    {
      "cell_type": "EN",
      "show_potency": "True",
      "marker_list": "FOXA2; SOX17",
      "method_used": "RT-qPCR",
      "description": ""
    }
  ]
  ```
- **Target structure**:
  ```json
  "differentiation_results": [
    {
      "cell_type": "EN",
      "show_potency": "True",
      "marker_list": "FOXA2; SOX17",
      "method_used": "RT-qPCR",
      "description": "",
      "differentiation_profile": "in vitro directed differentiation"
    }
  ]
  ```

## Status
- ✅ AI curation instructions updated to match ground truth structure
- ⏳ Ground truth data needs updates above