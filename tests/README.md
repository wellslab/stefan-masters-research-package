# Tests Directory

This directory contains test scripts and configurations for the Australian Stem Cell Curate package.

## Directory Structure

```
tests/
├── test_curation/           # Curation tests and results
├── test_reporting/          # Reporting tests
├── test_scoring/           # Scoring tests
└── test_utils/             # Utility tests
```

## Test Curation (`test_curation/`)

The main testing functionality for the curation system. This directory contains:

### Configuration Files

- **`config_single_test.json`**: Configuration for testing single articles (used for development/debugging)
- **`config_gpt5.json`**: GPT-5 (o1-preview) full curation run configuration
- **`config_gpt5_mini.json`**: GPT-5 Mini (o1-mini) curation configuration
- **`config_gpt5_nano.json`**: GPT-5 Nano (o1-mini) curation configuration
- **`config_gpt41.json`**: GPT-4.1 (gpt-4o) curation configuration
- **`config_gpt41_mini.json`**: GPT-4.1 Mini (gpt-4o-mini) curation configuration
- **`config_gpt41_nano.json`**: GPT-4.1 Nano (gpt-4o-mini) curation configuration

### Test Scripts

- **`test_curate.py`**: Main curation test script that processes articles and generates results
- **`test_identify_cell_lines.py`**: Script for testing cell line identification functionality

### Supporting Files

- **`usage_costs.json`**: API usage cost data for different models
- **`ai_curation_instructions.md`**: Instructions file used by AI models for curation (symlinked from project root)

### Data Directories

- **`articles/`**: Test articles for curation
- **`single_article_test/`**: Single article testing directory with sample article and results
- **`to_curate/`**: Articles to be curated by the main test runs
- **Model-specific result directories**: `gpt-4/`, `gpt-4.1/`, `gpt-5/` containing identification and curation results

## How the Test Process Works

### 1. Two-Phase Process

The curation system uses a two-phase approach:

1. **Identification Phase**: Identifies cell line names from research articles
2. **Curation Phase**: Extracts detailed metadata for each identified cell line

### 2. Configuration Parameters

Each config file contains:

```json
{
    "model": "model-name",              // OpenAI model to use
    "temperature": 0.2,                 // Model temperature setting
    "max_tokens": 16384,               // Maximum tokens per request
    "processing_method": "vision",      // Processing method (vision/transcription)
    "instructions_path": "ai_curation_instructions.md",  // Path to AI instructions
    "output_path": "path/to/results",   // Where to save results
    "articles_path": "path/to/articles", // Where to find articles to process
    "identification_path": "path/to/pmid_to_cell_lines.json"  // Pre-identified cell lines (optional)
}
```

### 3. Pre-identification Feature

If `identification_path` is provided in the config:
- The system loads pre-identified cell line names from the specified JSON file
- Skips the identification phase entirely
- Goes directly to curation using the pre-identified cell lines
- This saves time and API costs for repeated runs

### 4. Output Structure

Results are organized in timestamped directories:
```
results/
└── YYMMDD_HHMMSS/          # Timestamp-based run directory
    ├── test_run.log         # Detailed run logs
    ├── failed_articles.txt  # List of failed articles (if any)
    ├── failed_cell_lines.txt # List of failed cell lines (if any)
    └── {PMID}/             # Per-article results
        ├── {cell_line}_m.json  # Curated metadata for each cell line
        └── {cell_line}_INVALID.txt  # Invalid responses (for debugging)
```

### 5. Running Tests

#### Single Article Test
```bash
poetry run python tests/test_curation/test_curate.py config_single_test.json
```

#### Full Curation Runs
```bash
# Run in background with nohup
nohup poetry run python tests/test_curation/test_curate.py config_gpt5.json > tests/test_curation/gpt5_run.out 2>&1 &
```

#### Check Running Processes
```bash
ps aux | grep "test_curate.py" | grep -v grep
```

#### Monitor Progress
```bash
tail -f tests/test_curation/gpt5_run.out
```

### 6. Identification Results

Previous identification runs have generated `pmid_to_cell_lines.json` files mapping:
```json
{
    "16522163": ["hES3.1", "hES3.2", "hES3.3"],
    "18271699": ["E1", "E1C1", "E1C2"],
    ...
}
```

These files are located in:
- `tests/test_curation/{model_family}/{model_variant}/results/identify/{timestamp}_identify/pmid_to_cell_lines.json`

### 7. Current Configuration

All current configs are set up to use pre-identified cell lines from their respective model identification runs. This means:
- No identification phase is run (saves time/cost)
- Each model uses its own previously identified cell line names
- Curation goes directly to metadata extraction

### 8. Logs and Monitoring

Each run generates:
- **Console output**: Redirected to `{model}_run.out` files
- **Detailed logs**: Saved in timestamped results directories
- **Progress tracking**: Real-time logging of article processing
- **Error handling**: Failed articles and cell lines are tracked separately

### 9. Cost Tracking

The system tracks:
- Token usage per API call
- Estimated costs based on `usage_costs.json`
- Timing for performance analysis
- Success/failure rates

## Development Workflow

1. **Test changes**: Use `config_single_test.json` for quick testing
2. **Full evaluation**: Run all 6 model configurations for complete comparison
3. **Monitor progress**: Check `.out` files and process status
4. **Analyze results**: Compare outputs across different models
5. **Debug issues**: Use detailed logs and invalid response files