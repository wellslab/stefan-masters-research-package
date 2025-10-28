# Curation Process Behavior

## Overview

The curation process handles cell line metadata extraction from research articles using a two-phase approach: identification and curation.

## Process Flow

### 1. Article Selection

The script processes articles from two sources:

1. **Primary**: Articles in the `articles_path` directory (default: `to_curate/`)
2. **Filter**: Optional `pmid_list` in config (default: `['*']` = all articles)

**Result**: All articles in `articles_path` are processed unless `pmid_list` specifies otherwise.

### 2. Pre-Identification Check

For each article:

```python
if identification_path provided AND article_pmid in identification_file:
    use_pre_identified_cell_lines = True
else:
    use_pre_identified_cell_lines = False  # Trigger real-time identification
```

### 3. Processing Modes

**Mode A: Pre-Identified Articles**
- Article PMID exists in `identification_path` file
- Uses pre-identified cell line names
- Skips identification phase
- Goes directly to curation phase

**Mode B: Real-Time Identification**
- Article PMID not in `identification_path` file
- Calls `curate_article()` with `pre_identified_for_article = None`
- Performs identification phase first
- If cell lines found, proceeds to curation phase
- If no cell lines found, logs "No cell lines found in the article"

## Expected Behavior

### Normal Operation

1. **Articles in identification file**: Use pre-identified cell lines, curate successfully
2. **Articles not in identification file**: Attempt real-time identification, then curate if successful
3. **Articles with no cell lines**: Log as "No cell lines found" and skip

### Counting Discrepancies

**Curation count > Identification count**: Expected when articles not in identification file successfully undergo real-time identification.

**Curation count < Identification count**: Indicates curation failures after successful identification.

**Curation count = Identification count**: All identified articles were successfully curated.

## Configuration Parameters

### Required
- `articles_path`: Directory containing PDF articles
- `model`: AI model to use
- `processing_method`: "vision" for PDF processing

### Optional
- `identification_path`: Path to pre-identified cell lines JSON file
- `pmid_list`: List of PMIDs to process (default: all articles)
- `output_path`: Where to save results

## Output Structure

```
results/
└── YYMMDD_HHMMSS/          # Timestamp-based run directory
    ├── test_run.log         # Detailed run logs
    ├── failed_articles.txt  # Failed articles (if any)
    ├── failed_cell_lines.txt # Failed cell lines (if any)
    └── {PMID}/             # Per-article results
        ├── {cell_line}_m.json     # Curated metadata
        └── {cell_line}_INVALID.txt # Invalid responses
```

## Error Handling

### Article-Level Failures
- File system errors
- PDF processing failures
- Complete API failures

### Cell Line-Level Failures
- Invalid JSON responses
- Partial curation failures
- Individual API timeouts

## Performance Considerations

- **Batch Processing**: Processes all articles in sequence
- **API Limits**: Includes retry logic for rate limits
- **Memory Usage**: Loads one article at a time
- **Disk Usage**: Saves results incrementally

## Debugging

### Log Levels
- **INFO**: Normal operation, progress updates
- **WARNING**: Invalid responses, missing files
- **ERROR**: Failed articles, exceptions

### Key Log Messages
- `"Using pre-identified cell lines: {list}"`: Mode A operation
- `"No cell lines found in the article"`: Failed identification
- `"Successfully curated metadata for {cell_line}"`: Successful curation
- `"Failed to process: {count}"`: Summary of failures