# Age Range Correction Analysis

Analysis of the `donor.age` field comparing exact string matching vs semantically correct age range matching.

## Summary

- **Total Comparisons**: 325
- **Exact String Recall**: 0.018
- **Semantic Range Recall**: 0.037
- **Recall Improvement**: +0.018 (6 cases corrected)

## Methodology

**Exact Matching**: Requires identical strings (e.g., GT: `"25_29"` vs Model: `"25_29"`)

**Semantic Matching**: Handles age ranges intelligently:
- GT: `"25_29"`, Model: `"27"` → ✅ Match (27 is within 25-29 range)
- GT: `"25_29"`, Model: `"32"` → ❌ No match (32 is outside 25-29 range)
- GT: `"25_29"`, Model: `"25_29"` → ✅ Match (exact match)

## Performance Comparison

| Matching Type | Matches | Total | Recall | Improvement |
|---------------|---------|-------|--------|-------------|
| Exact String | 6 | 325 | 0.018 | - |
| Semantic Range | 12 | 325 | 0.037 | +6 cases |

## Cases Corrected by Semantic Matching

These cases failed exact string matching but succeeded with semantic range matching:

| Model | PMID | Cell Line | Ground Truth | Model Output | Explanation |
|-------|------|-----------|--------------|--------------|-------------|
| gpt-4.1-nano | 31494449 | LEIi011-C | `45_49` | `45` | Age 45 falls within range 45-49 |
| gpt-4.1-nano | 31494449 | LEIi011-B | `45_49` | `45` | Age 45 falls within range 45-49 |
| gpt-4.1-nano | 34198153 | LEIi017-B | `15_19` | `16` | Age 16 falls within range 15-19 |
| gpt-4.1-nano | 34198153 | LEIi017-A | `15_19` | `16` | Age 16 falls within range 15-19 |
| gpt-4.1-nano | 33429167 | LEIi015-B | `5_9` | `9` | Age 9 falls within range 5-9 |
| gpt-4.1-mini | 33429167 | LEIi015-A | `5_9` | `9` | Age 9 falls within range 5-9 |


## Remaining Semantic Mismatches

Cases where even semantic matching failed:

| Model | PMID | Cell Line | Ground Truth | Model Output | Issue |
|-------|------|-----------|--------------|--------------|-------|
| gpt-5-nano | 30634128 | LEIi007-A | `15_19` | `A15_19` | Unparseable format |
| gpt-5-nano | 33091851 | MCRIi020-A | `5_9` | `A5_9` | Unparseable format |
| gpt-5-nano | 30904819 | LEIi010-B | `15_19` | `A15_19` | Unparseable format |
| gpt-5-nano | 33360097 | LEIi014-C | `15_19` | `A15_19` | Unparseable format |
| gpt-5-nano | 32006803 | UOWi007-A | `40_44` | `A40_44` | Unparseable format |
*... and 298 more cases*


## Implications

Semantic age range matching improves recall by **1.8%** for the `donor.age` field.

This demonstrates the importance of domain-aware evaluation metrics that understand:
- Age ranges vs specific ages
- Semantic equivalence beyond exact string matching
- Field-specific validation logic

**Recommendation**: Implement semantic validation for age fields in production systems.