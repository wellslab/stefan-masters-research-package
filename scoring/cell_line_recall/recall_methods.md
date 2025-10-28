# Cell Line Recall Calculation Methods

## Overview

Cell line recall is defined as the proportion of non-Missing ground truth values that have an exact match in the corresponding model output cell line. This measures what proportion of the ground truth data the model successfully recovered in its curation.

## General Recall Calculation Logic

### Single-Item Arrays
For arrays containing only one item:
- Take the first (and only) item from both ground truth and model output arrays
- Perform direct field-wise string comparisons between the items
- Calculate recall as: `matching_fields / total_non_missing_gt_fields`

### Multi-Item Arrays
For arrays containing multiple items:
- Match array items between ground truth and model output based on a specified matching field
- For each matched pair of items, perform field-wise string comparisons
- Calculate recall across all matched item pairs
- Unmatched items in either array contribute to missed recall

## Array Field Analysis

Based on analysis of 1,126+ cell line JSON files, the following arrays can contain multiple items:

### Arrays Requiring Matching Logic (Multi-Item Capable)

| Array Field | Frequency | Max Items | Matching Field Needed |
|-------------|-----------|-----------|----------------------|
| **differentiation_results** | Very Common (770 files) | 9 items | **TBD** |
| **publications** | Common (111 files) | 23 items | **TBD** |
| **ethics** | Common (210 files) | 4 items | **TBD** |
| **donor** | Moderate (30 files) | 7 items | **TBD** |
| **contact** | Moderate (56 files) | 2 items | **TBD** |
| **genomic_characterisation** | Occasional (6 files) | 3 items | **TBD** |
| **genomic_modifications** | Occasional (10 files) | 2 items | **TBD** |
| **generator** | Rare (4 files) | 2 items | **TBD** |
| **basic_data** | Rare (3 files) | 2 items | **TBD** |
| **culture_medium** | Very Rare (1 file) | 2 items | **TBD** |
| **induced_derivation** | Very Rare (2 files) | 2 items | **TBD** |

### Arrays Using Direct Comparison (Single-Item)

| Array Field | Always Single Item |
|-------------|-------------------|
| **embryonic_derivation** | ✅ (117 files) |
| **undifferentiated_characterisation** | ✅ (5 files) |

## Array Item Structures

### differentiation_results
Most common multi-item array. Items contain:
- `cell_type` - Type of differentiated cell (e.g., "EN", "ME", "EC")
- `description` - Differentiation method description
- `marker_list` - Gene markers used for validation
- `method_used` - Detection method (e.g., "RT-qPCR")
- `show_potency` - Whether potency was demonstrated

**Example multi-item array:**
```json
"differentiation_results": [
  {
    "cell_type": "EC",
    "marker_list": "OTX2; PAX6",
    "description": "In vitro directed differentiation",
    "method_used": "RT-qPCR",
    "show_potency": "True"
  },
  {
    "cell_type": "ME",
    "marker_list": "TBXT; BMP4",
    "description": "In vitro directed differentiation",
    "method_used": "RT-qPCR",
    "show_potency": "True"
  },
  {
    "cell_type": "EN",
    "marker_list": "SOX17; GATA4",
    "description": "In vitro directed differentiation",
    "method_used": "RT-qPCR",
    "show_potency": "True"
  }
]
```

### publications
Can contain extensive publication lists. Items contain:
- `doi` - Digital Object Identifier
- `first_author` - First author name
- `journal` - Journal name
- `last_author` - Last author name
- `pmid` - PubMed ID
- `title` - Publication title
- `year` - Publication year

### ethics
Multiple ethics approvals. Items contain:
- `approval_date` - Date of approval
- `ethics_number` - Ethics approval number
- `institutional_HREC` - Human Research Ethics Committee name

### donor
Multiple donors for same cell line. Items contain:
- `age` - Donor age category (e.g., "A30_34")
- `disease_description` - Disease description
- `disease_name` - Disease name
- `sex` - Donor sex

### genomic_modifications
Multiple genetic variants/modifications. Items contain:
- `cytoband` - Chromosomal location
- `delivery_method` - Method of modification
- `description` - Modification description
- `genotype` - Genetic notation
- `loci_name` - Gene/locus name
- `mutation_type` - Type of mutation

### genomic_characterisation
Multiple karyotype analyses. Items contain:
- `karyotype` - Karyotype result
- `karyotype_method` - Analysis method
- `passage_number` - Cell passage number
- `summary` - Analysis summary

### contact
Multiple contact persons. Items contain:
- `e_mail` - Email address
- `first_name` - First name
- `group` - Research group/institution
- `last_name` - Last name
- `name_initials` - Name initials
- `phone_number` - Phone number

### Other Arrays
- **generator**: Institution information (`group`)
- **basic_data**: Cell line basics (`cell_line_alt_name`, `cell_type`, `frozen`, `hpscreg_name`)
- **culture_medium**: Culture conditions (`co2_concentration`, `o2_concentration`, `passage_method`)
- **induced_derivation**: iPSC derivation details (7 possible fields)

## Implementation Notes

1. **Matching Field Selection**: For each multi-item array, a specific field must be chosen to match items between ground truth and model output
2. **Missing Value Handling**: Only non-Missing ground truth values are considered in recall calculation
3. **Exact String Matching**: Field comparisons use exact string matching
4. **Unmatched Items**: Items that cannot be matched between arrays contribute to lower recall scores

## TODO: Define Matching Fields

The following arrays need matching field definitions:
- [ ] differentiation_results - Likely `cell_type`
- [ ] publications - Likely `doi` or `pmid`
- [ ] ethics - Likely `ethics_number`
- [ ] donor - Likely combination of `age` + `sex`
- [ ] contact - Likely `e_mail` or `last_name`
- [ ] genomic_characterisation - Likely `passage_number`
- [ ] genomic_modifications - Likely `loci_name` + `genotype`
- [ ] generator - Likely `group`
- [ ] basic_data - Likely `hpscreg_name`
- [ ] culture_medium - Likely combination of conditions
- [ ] induced_derivation - Likely method-related fields