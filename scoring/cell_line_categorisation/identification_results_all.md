# Cell Line Identification Scoring Results

## Unfiltered Results

| Model | Total Cell Lines | Exact | Manual | Discovery | Hallucination | Error | Exact % | Manual % | Scorable % | Hallucinations per 20 Articles | Errors per 20 Articles |
|-------|------------------|-------|--------|-----------|---------------|-------|---------|----------|------------|-------------------------------|------------------------|
| gpt-4.1 | 130 | 83 | 46 | 1 | 0 | 0 | 63.85% | 35.38% | 99.23% | 0.00 | 0.00 |
| gpt-4.1-mini | 135 | 102 | 27 | 6 | 0 | 0 | 75.56% | 20.00% | 95.56% | 0.00 | 0.00 |
| gpt-4.1-nano | 146 | 56 | 81 | 3 | 1 | 5 | 38.36% | 55.48% | 93.84% | 0.43 | 2.13 |
| gpt-5 | 129 | 77 | 51 | 1 | 0 | 0 | 59.69% | 39.53% | 99.22% | 0.00 | 0.00 |
| gpt-5-mini | 137 | 94 | 39 | 1 | 3 | 0 | 68.61% | 28.47% | 97.08% | 1.36 | 0.00 |
| gpt-5-nano | 134 | 67 | 64 | 1 | 2 | 0 | 50.00% | 47.76% | 97.76% | 0.89 | 0.00 |

## Filtered Results

| Model | Total Cell Lines | Exact | Manual | Discovery | Hallucination | Error | Exact % | Manual % | Scorable % | Hallucinations per 20 Articles | Errors per 20 Articles |
|-------|------------------|-------|--------|-----------|---------------|-------|---------|----------|------------|-------------------------------|------------------------|
| gpt-4.1 | 97 | 82 | 15 | 0 | 0 | 0 | 84.54% | 15.46% | 100.00% | 0.00 | 0.00 |
| gpt-4.1-mini | 99 | 95 | 4 | 0 | 0 | 0 | 95.96% | 4.04% | 100.00% | 0.00 | 0.00 |
| gpt-4.1-nano | 107 | 52 | 53 | 0 | 0 | 2 | 48.60% | 49.53% | 98.13% | 0.00 | 1.08 |
| gpt-5 | 99 | 73 | 26 | 0 | 0 | 0 | 73.74% | 26.26% | 100.00% | 0.00 | 0.00 |
| gpt-5-mini | 101 | 93 | 8 | 0 | 0 | 0 | 92.08% | 7.92% | 100.00% | 0.00 | 0.00 |
| gpt-5-nano | 100 | 62 | 36 | 0 | 2 | 0 | 62.00% | 36.00% | 98.00% | 1.14 | 0.00 |

## Category Definitions

- **Exact**: Cell line identifications that exactly match the ground truth
- **Manual**: Cell line identifications that require manual verification
- **Discovery**: New cell lines discovered that weren't in the ground truth
- **Hallucination**: Fabricated or incorrect cell line identifications
- **Error**: Processing errors during identification
- **Scorable %**: Percentage of cell lines that can be automatically scored (Exact + Manual + Discovery)

## Notes

- **Unfiltered Results**: Include all cell line identifications from all articles
- **Filtered Results**: Include only cell lines from articles that meet specific filtering criteria

