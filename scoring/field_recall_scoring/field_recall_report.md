# Field Recall Analysis Report

This report shows per-field recall performance across all AI models for stem cell registry curation.

**Summary Statistics:**
- Total Models Analyzed: 6
- Total Unique Fields: 48

## Model Performance Summary

| Model | Avg Recall | Fields Analyzed |
|-------|------------|-----------------|
| gpt-4.1 | 0.539 | 48 |
| gpt-4.1-mini | 0.516 | 48 |
| gpt-4.1-nano | 0.303 | 46 |
| gpt-5 | 0.556 | 48 |
| gpt-5-mini | 0.529 | 48 |
| gpt-5-nano | 0.423 | 46 |


## Field Recall by Section

Each section shows recall scores for individual fields across all models.

### Basic Data

| Field | gpt-4.1 | gpt-4.1-mini | gpt-4.1-nano | gpt-5 | gpt-5-mini | gpt-5-nano |
|-------|--------|--------|--------|--------|--------|--------|
| **cell_line_alt_name** | 🟠 0.325 | 🟡 0.608 | 🔴 0.157 | 🟡 0.542 | 🟡 0.621 | 🟠 0.433 |
| **cell_type** | 🟢 0.988 | 🟢 1.000 | 🟢 1.000 | 🟢 1.000 | 🟢 0.989 | 🟢 0.985 |
| **frozen** | 🟡 0.554 | 🟡 0.529 | 🟡 0.500 | 🟡 0.597 | 🟡 0.543 | 🟡 0.627 |
| **hpscreg_name** | 🟢 0.988 | 🟢 1.000 | 🟢 0.982 | 🟢 1.000 | 🟢 1.000 | 🟢 1.000 |


### Contact

| Field | gpt-4.1 | gpt-4.1-mini | gpt-4.1-nano | gpt-5 | gpt-5-mini | gpt-5-nano |
|-------|--------|--------|--------|--------|--------|--------|
| **e_mail** | 🟡 0.705 | 🟡 0.730 | 🟠 0.415 | 🟢 0.815 | 🟡 0.696 | 🟡 0.727 |
| **first_name** | 🟡 0.721 | 🟡 0.716 | 🟠 0.390 | 🟢 0.815 | 🟡 0.681 | 🟡 0.727 |
| **group** | 🔴 0.197 | 🔴 0.176 | 🔴 0.000 | 🔴 0.015 | 🔴 0.159 | 🟠 0.236 |
| **last_name** | 🟡 0.721 | 🟡 0.730 | 🟠 0.439 | 🟢 0.815 | 🟡 0.696 | 🟡 0.782 |
| **name_initials** | 🟡 0.744 | 🟡 0.535 | 🔴 0.000 | 🟡 0.778 | 🟠 0.488 | 🟠 0.342 |


### Culture Medium

| Field | gpt-4.1 | gpt-4.1-mini | gpt-4.1-nano | gpt-5 | gpt-5-mini | gpt-5-nano |
|-------|--------|--------|--------|--------|--------|--------|
| **co2_concentration** | 🟢 1.000 | 🟢 0.930 | 🔴 0.000 | 🟢 0.976 | 🟢 0.960 | 🟡 0.550 |
| **o2_concentration** | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🟠 0.250 |
| **passage_method** | 🔴 0.084 | 🔴 0.069 | 🔴 0.000 | 🟠 0.468 | 🟠 0.383 | 🔴 0.075 |


### Differentiation Results

| Field | gpt-4.1 | gpt-4.1-mini | gpt-4.1-nano | gpt-5 | gpt-5-mini | gpt-5-nano |
|-------|--------|--------|--------|--------|--------|--------|
| **cell_type** | 🟢 0.942 | 🟢 0.898 | 🔴 0.107 | 🟢 0.903 | 🟢 0.970 | 🟠 0.495 |
| **marker_list** | 🟡 0.645 | 🟡 0.640 | 🔴 0.031 | 🟡 0.711 | 🟡 0.673 | 🟠 0.322 |
| **method_used** | 🟡 0.623 | 🟠 0.272 | 🔴 0.141 | 🟡 0.776 | 🟠 0.487 | 🟠 0.275 |
| **show_potency** | 🟡 0.535 | 🟡 0.508 | 🔴 0.089 | 🟡 0.559 | 🟡 0.524 | 🟠 0.315 |


### Donor

| Field | gpt-4.1 | gpt-4.1-mini | gpt-4.1-nano | gpt-5 | gpt-5-mini | gpt-5-nano |
|-------|--------|--------|--------|--------|--------|--------|
| **age** | 🔴 0.085 | 🔴 0.000 | 🔴 0.026 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 |
| **disease_description** | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 |
| **disease_name** | 🟢 0.864 | 🟢 0.841 | 🟢 0.821 | 🟢 0.882 | 🟢 0.848 | 🟡 0.707 |
| **sex** | 🔴 0.000 | 🔴 0.000 | 🟠 0.205 | 🔴 0.000 | 🔴 0.000 | 🔴 0.024 |


### Ethics

| Field | gpt-4.1 | gpt-4.1-mini | gpt-4.1-nano | gpt-5 | gpt-5-mini | gpt-5-nano |
|-------|--------|--------|--------|--------|--------|--------|
| **approval_date** | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 |
| **ethics_number** | 🟠 0.325 | 🟡 0.578 | 🔴 0.018 | 🟠 0.416 | 🟡 0.543 | 🟠 0.328 |
| **institutional_HREC** | 🟠 0.313 | 🟡 0.559 | 🔴 0.018 | 🟠 0.403 | 🟡 0.543 | 🟠 0.328 |


### Generator

| Field | gpt-4.1 | gpt-4.1-mini | gpt-4.1-nano | gpt-5 | gpt-5-mini | gpt-5-nano |
|-------|--------|--------|--------|--------|--------|--------|
| **group** | 🟢 0.855 | 🟢 0.824 | 🟡 0.536 | 🟢 0.935 | 🟢 0.830 | 🟢 0.851 |


### Genomic Characterisation

| Field | gpt-4.1 | gpt-4.1-mini | gpt-4.1-nano | gpt-5 | gpt-5-mini | gpt-5-nano |
|-------|--------|--------|--------|--------|--------|--------|
| **karyotype** | 🟠 0.476 | 🟡 0.604 | 🟠 0.236 | 🟡 0.513 | 🟡 0.576 | 🔴 0.123 |
| **karyotype_method** | 🔴 0.122 | 🔴 0.158 | 🔴 0.000 | 🟡 0.500 | 🟠 0.467 | 🔴 0.031 |
| **passage_number** | 🟠 0.358 | 🟡 0.650 | 🔴 0.029 | 🟠 0.488 | 🟡 0.625 | 🔴 0.111 |
| **summary** | 🔴 0.024 | 🔴 0.000 | 🔴 0.040 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 |


### Genomic Modifications

| Field | gpt-4.1 | gpt-4.1-mini | gpt-4.1-nano | gpt-5 | gpt-5-mini | gpt-5-nano |
|-------|--------|--------|--------|--------|--------|--------|
| **cytoband** | 🟢 1.000 | 🔴 0.167 | 🔴 0.000 | 🔴 0.167 | 🟠 0.250 | 🔴 0.000 |
| **delivery_method** | 🟢 1.000 | 🟢 1.000 | 🔴 0.000 | 🟢 1.000 | 🟢 1.000 | 🔴 0.000 |
| **description** | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 |
| **genotype** | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 |
| **loci_name** | 🟢 1.000 | 🟢 0.875 | 🟢 1.000 | 🟢 1.000 | 🟡 0.667 | 🟠 0.333 |
| **mutation_type** | 🟢 0.800 | 🟡 0.500 | 🟢 1.000 | 🟢 0.833 | 🟡 0.500 | 🟠 0.333 |


### Induced Derivation

| Field | gpt-4.1 | gpt-4.1-mini | gpt-4.1-nano | gpt-5 | gpt-5-mini | gpt-5-nano |
|-------|--------|--------|--------|--------|--------|--------|
| **derivation_year** | 🔴 0.000 | 🔴 0.115 | 🔴 0.036 | 🔴 0.000 | 🔴 0.021 | 🔴 0.175 |
| **i_source_cell_origin_id** | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 |
| **i_source_cell_origin_term** | 🟢 1.000 | 🟢 1.000 | 🟠 0.217 | 🟢 1.000 | 🟢 1.000 | 🟢 0.897 |
| **i_source_cell_type_id** | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 |
| **i_source_cell_type_term** | 🟢 1.000 | 🟢 1.000 | 🟠 0.217 | 🟢 1.000 | 🟢 1.000 | 🟢 0.897 |
| **non_int_vector** | 🟠 0.354 | 🟠 0.357 | 🔴 0.038 | 🟠 0.338 | 🟠 0.393 | 🟠 0.250 |
| **non_int_vector_name** | 🟡 0.619 | 🟠 0.471 | 🔴 0.185 | 🟡 0.581 | 🟡 0.565 | 🟡 0.513 |


### Publications

| Field | gpt-4.1 | gpt-4.1-mini | gpt-4.1-nano | gpt-5 | gpt-5-mini | gpt-5-nano |
|-------|--------|--------|--------|--------|--------|--------|
| **doi** | 🟢 1.000 | 🟢 1.000 | 🟢 1.000 | 🟢 1.000 | 🟢 1.000 | 🟢 0.909 |
| **first_author** | 🟢 0.912 | 🟢 0.844 | 🟢 1.000 | 🟢 0.893 | 🟢 0.857 | 🟡 0.682 |
| **journal** | 🟢 1.000 | 🟢 0.978 | 🟢 1.000 | 🟢 1.000 | 🟢 1.000 | 🟢 1.000 |
| **last_author** | 🟢 0.971 | 🟢 0.889 | 🔴 0.125 | 🟢 0.964 | 🟢 0.857 | 🟢 0.864 |
| **pmid** | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 | 🔴 0.000 |
| **title** | 🟢 1.000 | 🟢 1.000 | 🟢 1.000 | 🟢 1.000 | 🟢 1.000 | 🟢 0.955 |
| **year** | 🟢 1.000 | 🟢 1.000 | 🟢 0.958 | 🟢 1.000 | 🟢 1.000 | 🟢 1.000 |


## Performance Insights

### Best Performing Fields (Avg Recall ≥ 0.8)

- **publications.journal**: 0.996
- **basic_data.hpscreg_name**: 0.995
- **basic_data.cell_type**: 0.994
- **publications.year**: 0.993
- **publications.title**: 0.992
- **publications.doi**: 0.985
- **publications.first_author**: 0.865
- **induced_derivation.i_source_cell_origin_term**: 0.852
- **induced_derivation.i_source_cell_type_term**: 0.852
- **donor.disease_name**: 0.827
- **genomic_modifications.loci_name**: 0.812
- **generator.group**: 0.805

### Challenging Fields (Avg Recall < 0.2)

- **donor.disease_description**: 0.000
- **ethics.approval_date**: 0.000
- **genomic_modifications.description**: 0.000
- **genomic_modifications.genotype**: 0.000
- **induced_derivation.i_source_cell_origin_id**: 0.000
- **induced_derivation.i_source_cell_type_id**: 0.000
- **publications.pmid**: 0.000
- **genomic_characterisation.summary**: 0.011
- **donor.age**: 0.018
- **donor.sex**: 0.038
- **culture_medium.o2_concentration**: 0.042
- **induced_derivation.derivation_year**: 0.058
- **contact.group**: 0.131
- **culture_medium.passage_method**: 0.180

### Model Comparison

**GPT-5 vs GPT-4.1 Series:**
- GPT-5 family average: 0.503
- GPT-4.1 family average: 0.453
- GPT-5 models outperform GPT-4.1 by 0.050 on average

## Correcting for Age Ranges

The `donor.age` field demonstrates the importance of semantic validation beyond exact string matching. Many models output specific ages (e.g., "27") while ground truth expects age ranges (e.g., "25_29").

**Analysis Results:**
- **Exact String Recall**: 0.018 (6/325 matches)
- **Semantic Range Recall**: 0.037 (12/325 matches)
- **Improvement**: +100% recall improvement (6 additional cases)

**Examples of Corrected Cases:**
- GT: `"25_29"`, Model: `"27"` → ✅ (27 falls within 25-29 range)
- GT: `"45_49"`, Model: `"45"` → ✅ (45 falls within 45-49 range)
- GT: `"5_9"`, Model: `"9"` → ✅ (9 falls within 5-9 range)

This semantic correction **doubles the effective recall** for the age field, demonstrating that domain-aware evaluation metrics can reveal actual model performance beyond strict string matching.

*See `age_range_correction_report.md` for detailed analysis.*

---

**Legend:**
- 🟢 High performance (≥0.8)
- 🟡 Good performance (0.5-0.8)
- 🟠 Moderate performance (0.2-0.5)
- 🔴 Low performance (<0.2)

*Report generated from field_recall_results.json*