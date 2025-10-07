# Australian Stem Cell Registry - Data Dictionary

This document provides a comprehensive overview of the data models used in the Australian Stem Cell Registry curation system. Each model represents a specific entity or concept within the registry, with detailed field specifications for data validation and processing.

## Table of Contents

- [CellLine](#cellline)
- [Contact](#contact)
- [CultureMedium](#culturemedium)
- [Disease](#disease)
- [Donor](#donor)
- [EmbryonicDerivation](#embryonicderivation)
- [Ethics](#ethics)
- [GenomicAlteration](#genomicalteration)
- [GenomicCharacterisation](#genomiccharacterisation)
- [HLA_Results](#hla_results)
- [InducedDerivation](#inducedderivation)
- [Loci](#loci)
- [MediumComponents](#mediumcomponents)
- [MicrobiologyVirologyScreening](#microbiologyvirologyscreening)
- [PluripotencyCharacterisation](#pluripotencycharacterisation)
- [Publication](#publication)
- [ReprogrammingMethod](#reprogrammingmethod)
- [STR_Results](#str_results)

## Overview

The data dictionary below describes the structure and requirements for each data model. The models are interconnected through relationships indicated in the "Nested Model" column.

**Field Types:**
- **Required**: Field must be provided
- **Optional**: Field is not required
- **Literal Values**: Field must be one of the specified values
- **List**: Field accepts multiple values of the specified type

---

### CellLine

| Field Name | Type | Required | Accepted Values | Default | Description | Nested Model |
|------------|------|----------|----------------|---------|-------------|-------------|
| hpscreg_id | str | Required |  | PydanticUndefined |  |  |
| alt_names | List | Required |  | PydanticUndefined |  |  |
| cell_line_type | Literal | Required | 'hESC', 'hiPSC' | PydanticUndefined |  |  |
| source | Literal | Required | 'donor', 'external_institution' | PydanticUndefined |  |  |
| frozen | bool | Required |  | PydanticUndefined |  |  |
| publication | Publication | Required |  | PydanticUndefined |  | [Publication](#publication) |
| donor | Donor | Required |  | PydanticUndefined |  | [Donor](#donor) |
| maintainer | str | Required |  | PydanticUndefined |  |  |
| producer | str | Required |  | PydanticUndefined |  |  |
| contact | Contact | Required |  | PydanticUndefined |  | [Contact](#contact) |
| source_tissue | str | Required |  | PydanticUndefined |  |  |
| source_cell_type | str | Required |  | PydanticUndefined |  |  |

### Contact

| Field Name | Type | Required | Accepted Values | Default | Description | Nested Model |
|------------|------|----------|----------------|---------|-------------|-------------|
| name | str | Required |  | PydanticUndefined |  |  |
| email | str | Required |  | PydanticUndefined |  |  |
| phone | str | Required |  | PydanticUndefined |  |  |

### CultureMedium

| Field Name | Type | Required | Accepted Values | Default | Description | Nested Model |
|------------|------|----------|----------------|---------|-------------|-------------|
| co2_concentration | float | Required |  | PydanticUndefined |  |  |
| o2_concentration | float | Required |  | PydanticUndefined |  |  |
| rho_kinase_sed | float | Required |  | PydanticUndefined |  |  |
| passage_method | Literal | Required | 'Enzymatically', 'Enzyme-free cell dissociation', 'Mechanically', 'other' | PydanticUndefined |  |  |
| other_passage_method | Optional | Required |  | PydanticUndefined |  |  |
| methods_io_id | str | Required |  | PydanticUndefined |  |  |
| base_medium | str | Required |  | PydanticUndefined |  |  |
| base_coat | str | Required |  | PydanticUndefined |  |  |

### Disease

| Field Name | Type | Required | Accepted Values | Default | Description | Nested Model |
|------------|------|----------|----------------|---------|-------------|-------------|
| name | str | Required |  | PydanticUndefined |  |  |
| description | str | Required |  | PydanticUndefined |  |  |

### Donor

| Field Name | Type | Required | Accepted Values | Default | Description | Nested Model |
|------------|------|----------|----------------|---------|-------------|-------------|
| age | int | Required |  | PydanticUndefined |  |  |
| sex | Literal | Required | 'Male', 'Female' | PydanticUndefined |  |  |
| disease | Union | Required | 'Healthy' | PydanticUndefined |  |  |

### EmbryonicDerivation

| Field Name | Type | Required | Accepted Values | Default | Description | Nested Model |
|------------|------|----------|----------------|---------|-------------|-------------|
| embryo_stage | str | Required |  | PydanticUndefined |  |  |
| zp_removal_technique | str | Required |  | PydanticUndefined |  |  |
| cell_seeding | str | Required |  | PydanticUndefined |  |  |
| e_preimplant_genetic_diagnosis | str | Required |  | PydanticUndefined |  |  |

### Ethics

| Field Name | Type | Required | Accepted Values | Default | Description | Nested Model |
|------------|------|----------|----------------|---------|-------------|-------------|
| ethics_number | str | Required |  | PydanticUndefined |  |  |
| institute | str | Required |  | PydanticUndefined |  |  |
| approval_date | str | Required |  | PydanticUndefined |  |  |

### GenomicAlteration

| Field Name | Type | Required | Accepted Values | Default | Description | Nested Model |
|------------|------|----------|----------------|---------|-------------|-------------|
| performed | bool | Required |  | PydanticUndefined |  |  |
| mutation_type | Literal | Required | 'variant', 'transgene expression', 'knock out', 'knock in', 'isogenic modification' | PydanticUndefined |  |  |
| cytoband | str | Required |  | PydanticUndefined |  |  |
| delivery_method | str | Required |  | PydanticUndefined |  |  |
| loci_name | str | Required |  | PydanticUndefined |  |  |
| loci_chromosome | str | Required |  | PydanticUndefined |  |  |
| loci_start | int | Required |  | PydanticUndefined |  |  |
| loci_end | int | Required |  | PydanticUndefined |  |  |
| loci_group | str | Required |  | PydanticUndefined |  |  |
| loci_disease | str | Required |  | PydanticUndefined |  |  |
| description | str | Required |  | PydanticUndefined |  |  |
| genotype | str | Required |  | PydanticUndefined |  |  |

### GenomicCharacterisation

| Field Name | Type | Required | Accepted Values | Default | Description | Nested Model |
|------------|------|----------|----------------|---------|-------------|-------------|
| passage_number | int | Required |  | PydanticUndefined |  |  |
| karyotype | str | Required |  | PydanticUndefined |  |  |
| karyotype_method | Literal | Required | 'G-Banding', 'Spectral', 'Comparative Genomic Hybridisation(CGH)', 'Array CGH', 'Molecular Kartotyping by SNP array', 'Karyolite BoBs' | PydanticUndefined |  |  |
| summary | str | Required |  | PydanticUndefined |  |  |

### HLA_Results

| Field Name | Type | Required | Accepted Values | Default | Description | Nested Model |
|------------|------|----------|----------------|---------|-------------|-------------|
| id | int | Required |  | PydanticUndefined |  |  |
| additional_genomic_characteristation | int | Required |  | PydanticUndefined |  |  |
| loci | int | Required |  | PydanticUndefined |  |  |
| group | Literal | Required | 'HLA-type-1', 'HLA-type-2', 'Non-HLA' | PydanticUndefined |  |  |
| allele_1 | str | Required |  | PydanticUndefined |  |  |
| allele_2 | str | Required |  | PydanticUndefined |  |  |

### InducedDerivation

| Field Name | Type | Required | Accepted Values | Default | Description | Nested Model |
|------------|------|----------|----------------|---------|-------------|-------------|
| i_source_cell_type | str | Required |  | PydanticUndefined |  |  |
| i_cell_origin | str | Required |  | PydanticUndefined |  |  |
| derivation_year | str | Required |  | PydanticUndefined |  |  |
| vector_type | str | Required |  | PydanticUndefined |  |  |
| vector_name | str | Required |  | PydanticUndefined |  |  |
| kit_name | str | Required |  | PydanticUndefined |  |  |

### Loci

| Field Name | Type | Required | Accepted Values | Default | Description | Nested Model |
|------------|------|----------|----------------|---------|-------------|-------------|
| name | str | Required |  | PydanticUndefined |  |  |
| chromosome | str | Required |  | PydanticUndefined |  |  |
| start | int | Required |  | PydanticUndefined |  |  |
| end | int | Required |  | PydanticUndefined |  |  |
| group | str | Required |  | PydanticUndefined |  |  |
| disease | Disease | Required |  | PydanticUndefined |  | [Disease](#disease) |

### MediumComponents

| Field Name | Type | Required | Accepted Values | Default | Description | Nested Model |
|------------|------|----------|----------------|---------|-------------|-------------|
| medium_component_name | str | Required |  | PydanticUndefined |  |  |
| company | str | Required |  | PydanticUndefined |  |  |
| component_type | str | Required |  | PydanticUndefined |  |  |

### MicrobiologyVirologyScreening

| Field Name | Type | Required | Accepted Values | Default | Description | Nested Model |
|------------|------|----------|----------------|---------|-------------|-------------|
| performed | bool | Required |  | PydanticUndefined |  |  |
| hiv1 | bool | Required |  | PydanticUndefined |  |  |
| hiv2 | bool | Required |  | PydanticUndefined |  |  |
| hep_b | bool | Required |  | PydanticUndefined |  |  |
| hep_c | bool | Required |  | PydanticUndefined |  |  |
| mycoplasma | bool | Required |  | PydanticUndefined |  |  |
| other | bool | Required |  | PydanticUndefined |  |  |
| other_result | str | Required |  | PydanticUndefined |  |  |

### PluripotencyCharacterisation

| Field Name | Type | Required | Accepted Values | Default | Description | Nested Model |
|------------|------|----------|----------------|---------|-------------|-------------|
| cell_type | Literal | Required | 'Endoderm', 'Mesoderm', 'Ectoderm', 'Trophectoderm' | PydanticUndefined |  |  |
| shown_potency | bool | Required |  | PydanticUndefined |  |  |
| marker_list | List | Required |  | PydanticUndefined |  |  |
| method | str | Required |  | PydanticUndefined |  |  |
| differentiation_profile | Literal | Required | 'in vivo teratoma', 'in vitro spontaneous differentiation', 'in vitro directed differentiation', 'scorecard', 'other' | PydanticUndefined |  |  |

### Publication

| Field Name | Type | Required | Accepted Values | Default | Description | Nested Model |
|------------|------|----------|----------------|---------|-------------|-------------|
| doi | str | Required |  | PydanticUndefined |  |  |
| pmid | str | Required |  | PydanticUndefined |  |  |
| title | str | Required |  | PydanticUndefined |  |  |
| first_author | str | Required |  | PydanticUndefined |  |  |
| last_author | str | Required |  | PydanticUndefined |  |  |
| journal | str | Required |  | PydanticUndefined |  |  |
| year | int | Required |  | PydanticUndefined |  |  |

### ReprogrammingMethod

| Field Name | Type | Required | Accepted Values | Default | Description | Nested Model |
|------------|------|----------|----------------|---------|-------------|-------------|
| vector_type | Literal | Required | 'non-integrated', 'integrated', 'vector-free', 'none' | PydanticUndefined |  |  |
| vector_name | str | Required |  | PydanticUndefined |  |  |
| kit | str | Required |  | PydanticUndefined |  |  |
| detected | bool | Required |  | PydanticUndefined |  |  |

### STR_Results

| Field Name | Type | Required | Accepted Values | Default | Description | Nested Model |
|------------|------|----------|----------------|---------|-------------|-------------|
| exists | bool | Required |  | PydanticUndefined |  |  |
| loci | int | Required |  | PydanticUndefined |  |  |
| group | Literal | Required | 'HLA-type-1', 'HLA-type-2', 'Non-HLA' | PydanticUndefined |  |  |
| allele_1 | str | Required |  | PydanticUndefined |  |  |
| allele_2 | str | Required |  | PydanticUndefined |  |  |

---

## Notes

1. **Nested Models**: Some fields reference other models in this schema. Click the linked model name to navigate to its definition.
2. **Literal Types**: Fields with "One of:" constraints must use exactly one of the specified values.
3. **Optional Fields**: Fields marked as "Optional" can be omitted from the data.
4. **Foreign Keys**: Some fields (like `additional_genomic_characteristation`, `loci`) reference IDs from other models.

Generated from `automated_curation_schema.py`
