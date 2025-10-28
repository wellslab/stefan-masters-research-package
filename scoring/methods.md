# Cell Line Curation Scoring Methods

## Overview

This document describes the methods used to analyze and score cell line curation performance across multiple AI models (GPT-4.1, GPT-4.1-mini, GPT-4.1-nano, GPT-5, GPT-5-mini, GPT-5-nano) against ground truth data from the Australian Stem Cell Registry.

## Data Processing Pipeline

### 1. Data Cleaning and Harmonization

**Input**: Raw combined dataframe from model outputs
**Process**:
- Cleaned derivation_year column by extracting year values from full dates (e.g., "2021-01-01" → "2021")
- Verified presence of cell_type_term column
- Applied data harmonization across all model outputs

**Script**: `fix_derivation_year.py`

### 2. JSON Reconstruction

**Input**: Cleaned combined dataframe (2,982 rows, 67 columns)
**Process**:
- Reconstructed individual JSON files organized by PMID
- Created directory structure: `model_output/[model_name]/[pmid]/[cell_line_identification.json]`
- Generated 1,129 files total (315 ground truth, 814 model outputs)

**Script**: `reconstruct_with_pmid_folders.py`

## Scoring Methodology

### 3. Cell Line Identification Analysis

**Objective**: Compare model-identified cell lines with ground truth cell line counts per PMID

**Process**:
- Analyzed actual reconstructed model output directories
- Counted cell lines found by each model per PMID
- Compared counts against ground truth publication dictionary
- Identified PMIDs with count mismatches (model count ≠ ground truth count)

**Script**: `analyze_actual_model_output.py`

**Key Metrics**:
- **Count Accuracy**: Percentage of PMIDs where model count matches ground truth count
- **Cell Line Deficit/Surplus**: Difference between model output and ground truth totals
- **Usable PMIDs**: PMIDs with correct counts suitable for recall calculation

### 4. Unmatched Cell Line Mapping

**Objective**: Identify and map cell lines where model naming didn't match ground truth

**Process**:
1. **Identification**: Generated mapping files for unmatched cell lines per model
2. **Auto-fill**: Used publication dictionary to automatically map obvious matches using:
   - String similarity matching (SequenceMatcher)
   - Single-cell-line PMID matching
   - Pattern recognition for naming variations
3. **Validation**: Ensured all mappings reference actual ground truth cell lines only
4. **Exclusion**: Removed mappings for PMIDs with count mismatches to maintain scoring integrity

**Scripts**:
- `create_unmatched_mapping_files.py`
- `auto_fill_mappings.py`
- `validate_and_fix_mappings.py`
- `clean_mapping_files_exclude_pmids.py`

### 5. Recall Calculation Strategy

**Approach**: Conditional recall calculation based on mapping availability

**Methodology**:
- **Mapped cell lines**: Calculate field-by-field recall scores comparing model output vs ground truth
- **Unmapped cell lines**: Exclude from recall calculation (no penalty for unmappable naming differences)
- **Final scores**: Average recall only across evaluable (mapped) cell lines

**Rationale**: This approach provides meaningful recall metrics while acknowledging practical limitations of mapping every cell line variant.

## Analysis Components

### Count Mismatch Analysis

**Identification of**:
- PMIDs where models found MORE cell lines than ground truth
- PMIDs where models found FEWER cell lines than ground truth
- PMIDs where models found DIFFERENT cell lines than ground truth

### Publication Failure Analysis

**Process**:
- Extracted all PMIDs appearing in unmatched mapping files
- Categorized by number of affected models (1/6 to 6/6)
- Mapped PMIDs to journal names using publication metadata
- Identified systematic naming convention failures

**Output**: List of 26 PMIDs representing publications where models failed to correctly identify cell line names

### Journal Pattern Analysis

**Analysis of**:
- Which journals have most cell line naming issues
- Correlation between journal formatting and model performance
- Impact of publication standards on extraction accuracy

## Quality Assurance Measures

### Data Validation

1. **Ground Truth Integrity**: All mappings validated against publication dictionary as single source of truth
2. **Count Verification**: Manual verification of discrepancies between mapping analysis and actual output directories
3. **Exclusion Logic**: PMIDs with count mismatches excluded from recall calculations to prevent bias

### Error Correction

1. **Fixed Invalid Mappings**: Removed 21 mappings referencing non-existent ground truth cell lines
2. **Corrected Count Analysis**: Updated analysis to use actual model output directories rather than incomplete mapping file data
3. **Consistent Naming**: Standardized file naming and removed temporary analysis files

## Statistical Outputs

### Performance Rankings

**Primary Metrics**:
- Count accuracy percentage
- Cell line deficit/surplus
- Number of usable PMIDs for recall calculation

### Failure Analysis

**Categorization by**:
- Impact level (number of models affected)
- Journal source
- Naming pattern type (prefix variations, institutional differences, etc.)

## File Organization

```
scoring/
├── cell_line_scoring/
│   ├── cell_line_recall_report.md          # Main analysis report
│   ├── corrected_pmids_to_exclude_from_recall.json
│   ├── actual_model_output_analysis.json
│   ├── unmatched_pmids_analysis.json
│   └── unmatched_mapping/
│       ├── gpt-4.1_cell_line_mapping.json
│       ├── gpt-4.1-mini_cell_line_mapping.json
│       ├── gpt-4.1-nano_cell_line_mapping.json
│       ├── gpt-5_cell_line_mapping.json
│       ├── gpt-5-mini_cell_line_mapping.json
│       └── gpt-5-nano_cell_line_mapping.json
└── methods.md                               # This document
```

## Key Findings Summary

1. **Best Performing Model**: GPT-5 (81.4% count accuracy, -5 cell line deficit)
2. **Most Problematic Publication**: PMID 18386991 (all 6 models failed naming)
3. **Total Naming Issues**: 26 PMIDs requiring manual mapping across all models
4. **Journal Impact**: "Stem Cell Research" family journals represent 19/26 problematic PMIDs

## Next Steps

1. **Complete Manual Mappings**: Fill remaining unmapped cell lines in mapping files
2. **Implement Recall Calculation**: Create script using conditional scoring based on mapping availability
3. **Journal Analysis**: Investigate formatting standards across identified problematic journals
4. **Institutional Pattern Study**: Analyze correlation between research institutions and naming conventions