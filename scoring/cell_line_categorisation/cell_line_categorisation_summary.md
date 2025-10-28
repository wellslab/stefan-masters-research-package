# Cell Line Categorisation Summary

## Overview

This report provides a comprehensive analysis of cell line identification and categorisation across 6 AI models (GPT-4.1, GPT-4.1-mini, GPT-4.1-nano, GPT-5, GPT-5-mini, GPT-5-nano) compared to ground truth data from the Australian Stem Cell Registry.

## Categorisation Definitions

- **Exact**: Cell lines where model output name exactly matches a ground truth file name
- **Manual**: Cell lines requiring manual mapping due to naming differences
- **Error**: Model extraction errors
- **Discovery**: Cell lines found by models but not in ground truth (potential new discoveries)
- **Hallucinated**: Cell lines that don't actually exist in the publications
- **Other**: Unmapped or unclear categories
- **Scorable %**: Percentage of cell lines that can be scored (Exact + Manual)

## Comprehensive Categorisation Results

| Model | Total | Exact | Manual | Error | Discovery | Hallucinated | Other | Exact % | Scorable % |
|-------|-------|-------|--------|-------|-----------|---------------|-------|---------|------------|
| gpt-4.1 | 130 | 83 | 46 | 0 | 1 | 0 | 0 | 63.8% | **99.2%** |
| gpt-4.1-mini | 135 | 102 | 27 | 0 | 6 | 0 | 0 | 75.6% | **95.6%** |
| gpt-4.1-nano | 146 | 56 | 81 | 5 | 3 | 1 | 0 | 38.4% | **93.8%** |
| gpt-5 | 129 | 77 | 51 | 0 | 1 | 0 | 0 | 59.7% | **99.2%** |
| gpt-5-mini | 137 | 94 | 39 | 0 | 1 | 3 | 0 | 68.6% | **97.1%** |
| gpt-5-nano | 134 | 67 | 64 | 0 | 1 | 2 | 0 | 50.0% | **97.8%** |

## Key Findings

### Performance Ranking by Scorable Coverage
1. **GPT-5 & GPT-4.1**: 99.2% - Highest scorable coverage (tied), most reliable for recall calculations
2. **GPT-5-nano**: 97.8% - Strong coverage despite lower exact match rate
3. **GPT-5-mini**: 97.1% - Good performance with hallucination management
4. **GPT-4.1-mini**: 95.6% - Highest exact match rate with strong discovery potential
5. **GPT-4.1-nano**: 93.8% - Lowest coverage due to errors and inconsistencies

### Exact Match Performance
- **Highest**: GPT-4.1-mini (75.6%) - Best at using standard naming conventions
- **Lowest**: GPT-4.1-nano (38.4%) - Requires most manual mapping work

### Error Analysis
- **Only GPT-4.1-nano has extraction errors** (5 errors)
- All other models achieved 0 errors

### Discovery Potential
- **GPT-4.1-mini**: 6 discoveries - Best at identifying potentially novel cell lines
- **GPT-4.1-nano**: 3 discoveries
- **GPT-4.1, GPT-5, GPT-5-mini & GPT-5-nano**: 1 discovery each

### Hallucination Analysis
- **GPT-5-mini**: 3 hallucinated cell lines
- **GPT-5-nano**: 2 hallucinated cell lines
- **GPT-4.1-nano**: 1 hallucinated cell line
- **GPT-4.1, GPT-4.1-mini & GPT-5**: 0 hallucinations

## Overall Statistics

- **Total cell lines across all models**: 811
- **Exact matches**: 479 (59.1%)
- **Manual mappings**: 308 (38.0%)
- **Errors**: 5 (0.6%)
- **Discoveries**: 13 (1.6%)
- **Hallucinated cell lines**: 6 (0.7%)
- **Other/Empty categories**: 0 (0.0%)
- **Overall scorable coverage**: 97.0%

## Recommendations

### For Recall Scoring
1. **GPT-5** and **GPT-4.1** provide the most reliable recall calculations due to highest scorable coverage (99.2%)
2. **GPT-4.1-nano** requires careful validation due to errors and inconsistencies
3. All models achieve >93% scorable coverage, making them suitable for recall analysis

### For Cell Line Discovery
1. **GPT-4.1-mini** shows highest potential for discovering novel cell lines (6 discoveries)
2. Discovery candidates should be manually validated against original publications

### For Production Use
1. **GPT-5** offers the best balance of accuracy, coverage, and minimal errors
2. **GPT-4.1-mini** provides highest exact match rate but may require more manual validation
3. **GPT-4.1-nano** may need additional quality control measures

## Files Generated

All comprehensive mapping files are available in this directory:
- `gpt-4.1_comprehensive_mapping.json`
- `gpt-4.1-mini_comprehensive_mapping.json`
- `gpt-4.1-nano_comprehensive_mapping.json`
- `gpt-5_comprehensive_mapping.json`
- `gpt-5-mini_comprehensive_mapping.json`
- `gpt-5-nano_comprehensive_mapping.json`
- `comprehensive_mapping_summary.json`

Each file contains complete categorisation information for every cell line identified by the respective model.