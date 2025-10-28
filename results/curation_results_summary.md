# Automated Curation Process Results Summary

## Overview

This document summarizes the results of automated curation runs across 6 different AI models. The process uses a two-phase pipeline: **identification** (finding cell lines in articles) followed by **curation** (extracting detailed metadata for identified cell lines).

## Pipeline Performance Summary

| Model | Original Articles | Identification Success | Curation Success | Time per 20 Articles | Cost per 20 Articles |
|-------|-------------------|----------------------|------------------|---------------------|---------------------|
| **GPT-4.1** | 54 | 45 (83.3%) | 46 (85.2%) | 49.7 minutes | $1.25 |
| **GPT-4.1-Mini** | 54 | 43 (79.6%) | 44 (81.5%) | 38.0 minutes | $0.50 |
| **GPT-4.1-Nano** | 54 | 48 (88.9%) | 48 (88.9%) | 30.4 minutes | $0.18 |
| **GPT-5** | 54 | 43 (79.6%) | 43 (79.6%) | 144.1 minutes | $4.09 |
| **GPT-5-Mini** | 54 | 44 (81.5%) | 44 (81.5%) | 85.3 minutes | $0.74 |
| **GPT-5-Nano** | 54 | 45 (83.3%) | 45 (83.3%) | 84.3 minutes | $0.23 |

## Detailed Analysis

### Performance Metrics

#### Processing Speed (Time per 20 articles)
1. **GPT-4.1-Nano**: 30.4 minutes (fastest)
2. **GPT-4.1-Mini**: 38.0 minutes
3. **GPT-4.1**: 49.7 minutes
4. **GPT-5-Nano**: 84.3 minutes
5. **GPT-5-Mini**: 85.3 minutes
6. **GPT-5**: 144.1 minutes (slowest)

#### Cost Efficiency (Cost per 20 articles)
1. **GPT-4.1-Nano**: $0.18 (most cost-effective)
2. **GPT-5-Nano**: $0.23
3. **GPT-4.1-Mini**: $0.50
4. **GPT-5-Mini**: $0.74
5. **GPT-4.1**: $1.25
6. **GPT-5**: $4.09 (most expensive)

#### Success Rate
1. **GPT-4.1-Nano**: 88.9% (48/54 articles)
2. **GPT-4.1**: 85.2% (46/54 articles)
3. **GPT-5-Nano**: 83.3% (45/54 articles)
4. **GPT-4.1-Mini**: 81.5% (44/54 articles)
5. **GPT-5-Mini**: 81.5% (44/54 articles)
6. **GPT-5**: 79.6% (43/54 articles)

### Failed Articles Analysis

Only **1 explicit failure** was recorded:
- **GPT-4.1-Mini**: Failed to process article `32887382.pdf` due to a file system error

### Pipeline Analysis

**Identification Phase Results:**
- **GPT-4.1-Nano**: Best identification success (48/54 = 88.9%)
- **GPT-4.1 & GPT-5-Nano**: 45/54 articles (83.3%)
- **GPT-5-Mini**: 44/54 articles (81.5%)
- **GPT-4.1-Mini & GPT-5**: 43/54 articles (79.6%)

**Missing Articles (No Cell Lines Identified):**
- **9-11 articles** per model failed identification phase
- These articles had no identifiable cell lines according to each model's analysis
- **No articles had empty cell line lists** - all identified articles contained at least one cell line

**Curation Phase Results:**
- **Near-perfect success rate** once articles entered curation
- Only **1 explicit failure**: GPT-4.1-Mini failed on article `32887382.pdf` (file system error)
- **Anomaly**: GPT-4.1 and GPT-4.1-Mini show slightly more curation successes than identification successes

### Cell Line Processing Statistics

| Model | Total Cell Lines Curated | Failed Cell Lines |
|-------|---------------------------|-------------------|
| GPT-4.1 | 131 | 0 |
| GPT-4.1-Mini | 126 | 0 |
| GPT-4.1-Nano | 148 | 0 |
| GPT-5 | 129 | 0 |
| GPT-5-Mini | 137 | 0 |
| GPT-5-Nano | 135 | 0 |

## Recommendations

### For Speed-Critical Applications
- **GPT-4.1-Nano**: Fastest processing time (30.4 min/20 articles) with highest success rate (88.9%)

### For Cost-Sensitive Applications
- **GPT-4.1-Nano**: Most cost-effective at $0.18 per 20 articles while maintaining excellent performance

### For Balanced Performance
- **GPT-4.1-Nano**: Offers the best combination of speed, cost, and success rate
- **GPT-4.1**: Good alternative if slightly higher cost is acceptable for established performance

### Models to Avoid
- **GPT-5**: Significantly slower (144.1 min/20 articles) and most expensive ($4.09/20 articles) with lowest success rate
- **GPT-5-Mini/Nano**: Much slower than GPT-4.1 variants with no significant accuracy benefits

## Technical Notes

- **Two-Phase Pipeline**: Identification phase (finding cell lines) followed by curation phase (metadata extraction)
- **Vision-Based Processing**: All models used vision-based PDF analysis
- **Pre-Identification Used**: Curation runs used pre-identified cell lines from each model's identification phase
- **Processing Times**: Include API latency and retry mechanisms for failed requests
- **Cost Estimates**: Based on OpenAI's pricing for input/output tokens
- **100% Identification Quality**: No articles had empty cell line lists - all identified articles contained valid cell lines

## PMIDs That Failed Identification Phase

### Common to All Models (5 PMIDs)
31039485, 32887382, 33316599, 34157503, 37315423

### Missed by 5/6 Models (4 PMIDs)
- 29499499 (all except GPT-4.1-Nano)
- 34619644 (all except GPT-4.1-Nano)
- 38277710 (all except GPT-4.1 and GPT-4.1-Mini)
- 38458031 (all except GPT-4.1-Nano)

### Missed by 3/6 Models (1 PMID)
- 32931148 (GPT-4.1-Mini, GPT-5, GPT-5-Mini)

### Model-Specific Failures (3 PMIDs)
- 18271699 (GPT-4.1-Mini only)
- 32442534 (GPT-4.1 only)
- 38433209 (GPT-5 only)

## Anomalous PMIDs (Curated Without Pre-Identification)

- **GPT-4.1**: 32442534 (successfully curated via real-time identification)
- **GPT-4.1-Mini**: 32887382 (attempted curation, failed with file system error)

## Run Details

- **Test Period**: October 16-17, 2025
- **Total Articles Available**: 54
- **Processing Method**: Vision-based PDF analysis
- **Configuration**: Pre-identified cell lines used for most runs, with real-time identification fallback