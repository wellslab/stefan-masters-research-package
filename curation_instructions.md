
# Instructions
The prompt and context contains a research article, the name of a stem cell line, and a JSON schema.
Your task is to extract information about the stem cell line from the research article.
Format your response as a JSON object, enclosed in a JSON codeblock, according to the schema provided in the context.
The rest of this document provides instructions on how to retrieve information for the cell line.

## How to use this guide
There are several groups of metadata that need to be curated. This documents provide instructions for how to curate each group, these instructions have been divided into sections below. Each section has an **Instruction Table**, that specifies for each metadata field, **retrieval instructions** and an example **passage-value pair.**

- The **retrieval instructions** describe where possible the location of the metadata in the article and the meaning of the metadata so that the right content can be extracted from the article.
- The **passage-value pair** gives a concrete example of a real passage from a real article and the expert extracted metadata value based on this passage.


The example passage-value pair is provided for some fields but may not be for others.


## Reading these insructions

Ignored Fields.
Fields which contain an asterisk at the end of their name should not be retrieved.
These are only recorded here for documentation purposes and will be updated at a later date.


# Cell line information retrieval
Retieve information for the following entities according to the schema:

| Field                    | Metadata retrieval instructions                                                                                                                                                                   |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| hpscreg_id               | Fill this with the stem cell line name given in the prompt.                                                                                                                                       |
| alt_names                | Fill this with alternative names for the cell line if they were used in the article.                                                                                                              |
| stem_cell_type           | Select the most appropriate literal defined in the schema that corresponds to the type of the stem cell line. e.g. hiPSC or ESC                                                                   |
| source_cell_type         | Fill this with the type of cell that the cell line was derived from.                                                                                                                              |
| CellLine.source_tissue   | Fill this with the location in the body from which the cell line was taken. This should be a tissue, or blood. This should not be a type of cell, but rather more a more general biopsy location. |
| CellLine.source          | If the cell line was derived firsthand from a patient, write donor. Otherwise if the cell line was sourced from an external institution, write external institution.                              |
| CellLine.owner_group     | This would be information about which institution is responsible for maintaining the cell line.                                                                                                   |
| CellLine.generator_group | This would be information about which institution produced or manufactured the cell line. It might be same as the maintainer in some cases, but not necessarily so.                               |
| CellLine.frozen          | Set this equal to true if there is a stocked/archived date for the cell line mentioned in the article. Otherwise set it equal to false.                                                           |
|                          |                                                                                                                                                                                                   |
**Example / expected object format**

```json
cell_line: {
	hpscreg_id: "AIBNi001-A",
	alt_names: ["GENIE 1"],
	stem_cell_type: "hiPSC",
	source_cell_type: "Peripheral blood mononuclear cells",
	source_tissue_type: "Blood",
	frozen: "True",
	owner_group: "Australian Institute for Bioengineering and Nanotechnology",
	generator_group: "Australian Institute for Bioengineering and Nanotechnology",
}
```


## Contact metadata retrieval instructions

Retrieve information from the article for the best person to contact regarding the cell line.
**Example 1. Contact information reported.**

```json
contact: {
	name: "Professor Ernst J Wolvetang"
	email: "e.wolvetang@uq.edu.au"
	contact_number: "None"
}
```

In case the article does not contain any contact information write “None” in all the fields while still responding with a contact object.
**Example 2. No contact information reported.**

```json
contact: {
	name: "None"
	email: "None"
	contact_number: "None"
}
```

## Publication metadata retrieval instructions
Retrieve bibliographic publication metadata from the article.

**Example 1. Publication metadata retrieved.**
```json 
publication: {
	title: "Generation of induced pluripotent stem cell lines from peripheral blood mononuclear cells of three drug resistant and three drug responsive epilepsy patients",
	journal: "Stem Cell Research",
	doi: "10.1016/j.scr.2021.102564",
	first_author: "Zoe L. Hunter",
	last_author: "Lata Vadlamudi",
	year: "2021",
	pmid: "34649201"
}
```

All fields must be included. If there is any metadata not reported in the article, write “None” into the respective field.

## Donor metadata retrieval instructions

Retrieve metadata about the donor from which the stem cell line was derived.

| Field               | Description / instructions                                                              | Accepted values                                     |
| ------------------- | --------------------------------------------------------------------------------------- | --------------------------------------------------- |
| age                 | Age of the donor                                                                        | For iPSCs: Integers > 0<br>For ESCs: Write “Embryo” |
| sex                 | Biological sex of the donor                                                             | Male, Female                                        |
| disease_name        | The disease the donor had or otherwise healthy                                          | Disease name OR “ND”                                |
| disease_description | Generate a short description of the disease, or write None if the donor had no disease. |                                                     |

**Example 1. Donor metadata retrieved. Disease present.**

```json
donor: {
	age: "35",
	sex: "Female",
	disease_name: "Epilepsy",
	disease_description: "Epilepsy is a common neurological disorder characterized by seizures."
}

```


**Example 2. Donor metadata retrieved. Disease absent.**

```json
donor: {
	age: "42",
	sex: "Male",
	disease_name: "ND",
	disease_description: "None"
}

```

## Genomic modification metadata retrieval instructions

One or more genomic modifications can be made to a cell line. Retrieve all genomic modifications made to the cell line.
Each genomic modification object must have the following fields.

| Field           | Description / instructions                                                                                 | Accepted values                                                                        |
| --------------- | ---------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| mutation_type   | Select the best matching literal in the schema that describes the mutation type for the genomic alteration | Variant, Knock out, Knock in, CRISPR/Cas9, Transgene expression, Isogenic modification |
| cytoband        | Location of the genomic modification / cytoband                                                            |                                                                                        |
| delivery_method | How the genomic modiciation was delivered                                                                  |                                                                                        |
| loci_name       | Loci name if applicable                                                                                    |                                                                                        |
| loci_start      | Loci start position if present                                                                             |                                                                                        |
| loci_end        | Loci end position if present                                                                               |                                                                                        |
| loci_group      | -                                                                                                          |                                                                                        |
| loci_disease    | Disease associated with the loci, if applicable                                                            |                                                                                        |
| description     | Short description of the genomic modification                                                              |                                                                                        |
| genotype        | Standard nomenclature for the genomic modification                                                         |                                                                                        |

There could be multiple genomic modifications made. Therefore always respond with a list of genomic modification objects.
If there was only one genomic modification made, return a list with one object.
If there were no genomic modifications made, return a list with the string “None”.

**Example / expected response format. A single genomic modification done to the cell line.**
```json

genomic_modifications: [

	{
		mutation_type: "Variant",
		cytoband: "None",
		delivery_method: "CRISPR/Cas9",
		loci_name: "None",
		loci_start: "None",
		loci_end: "None",
		loci_group: "None",
		loci_disease: "Metatropic dysplasia",
		modification_description: "Heterozygous missense mutation p.P799L in TRPV4 gene.",
		modification_genotype: "TRPV4 c.2396C > T"
		
	}
	
]
```

**Example / expected response format. No genomic modifications made.**
```json

genomic_modifications: [
	"None"
]
```

## Differentation characterisation results metadata retrieval instructions

The articles should report on test results for the differentiation potential of the stem cell lines.
Results should be present for all three germ layers of the ectoderm, mesoderm and endoderm.
The output therefore needs to be a list of three test result objects—one object for each germ layer.
The metadata fields in each object are described here:


| Field                   | Information retrieval instructions                                                                                                                                     | Accepted values                                                                |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| cell_type               | The germ layer you are identifying test results for.                                                                                                                   | Endoderm, Mesoderm, Ectoderm                                                   |
| shown_potency           | Boolean for whether results indicate the cell line can differentiate into this germ layer.                                                                             | True, False                                                                    |
| marker_list             | Fill in with the markers reported in the article that indicate differentation into the germ layer under consideration when making this differentiation results object. | The marker lists that are associated with differentiation into each germ layer |
| method                  | The method to test for differentiation into the germ layers                                                                                                            |                                                                                |
| differentiation_profile | Select the best matching literal in the schema for the differentiation profile                                                                                         |                                                                                |

**Example/expected response format**
```json
differentiation_results: [
	{
		germ_layer: "Ectoderm",
		shown_potency:  "True",
		marker_list: ["PAX6", "SOX1", "NESTIN", "TUBB3"],
		method: "Immunocytochemistry",
		differentiation_profile: "in vitro directed differentiation" 
		
	}, 
	{
		germ_layer: "Endoderm",
		shown_potency:  "True",
		marker_list: ["SOX17", "FOXA2", "GATA4/6", "CXCR4"],
		method: "Immunocytochemistry",
		differentiation_profile: "in vitro directed differentiation"
	
	},
	{
		germ_layer: "Mesoderm",
		shown_potency:  "True",
		marker_list: ["Brachyury", "MESP1", "KDR", "α-SMA"],
		method: "Immunocytochemistry",
		differentiation_profile: "in vitro directed differentiation"
	}
	
]
```


## Undifferentation characterisation results
Certain markers that experimenters test for are highly expressed in undifferentiated pluripotent stem cells. 
The article should report on the presence of these markers and scores related to them. Retrieve this information to fill in the following metadata fields.

| DB Table Name                   | Field name                                    | Description / instructions                                                                                    | Accepted values                                                                                              |
| ------------------------------- | --------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| UndifferentiatedCharactrisation | undifferentiation_characteristion_marker_list | List of markers reported in the article that were tested for in their undifferentiation characterisation test | Common markers include OCT4, SOX2, NANOG, TRA-1-60, TRA-1-81, SSEA-3, SSEA-4.<br><br>OR<br><br>Empty list [] |
| UndifferentiatedCharactrisation | undifferentiation_characteristion_test_used   | The test reported in the article used to assess the undifferentiation of the cell line                        | Common tests include EpiPluriScore, PluriTest,<br>Morphology, hPSC Scorecard, Other                          |
| UndifferentiatedCharactrisation | epi_pluri_score                               | The epi pluri score for the undifferentation characterisation test                                            | Integers                                                                                                     |
| UndifferentiatedCharactrisation | epi_pluri_mcpg*                               | -                                                                                                             | -                                                                                                            |
| UndifferentiatedCharactrisation | epi_pluri_oct4*                               | -                                                                                                             | -                                                                                                            |
| UndifferentiatedCharactrisation | pluri_test_score                              | The pluri test score for the undifferentiation characterisation test, if one was reported.                    |                                                                                                              |
| UndifferentiatedCharactrisation | pluri_novelty_score                           | The pluri test novelty score for the undifferentiation characterisation test, if one was reported.            |                                                                                                              |
| UndifferentiatedCharactrisation | pluri_test_microarray_url                     | -                                                                                                             | -                                                                                                            |

**Example**
```json
undifferentation_characterisation_results: {
	marker_list: ["OCT4", "SOX2", "NANOG", "TRA-1-60"],
	test_used: "PluriTest",
	epi_pluri_score: "None",
	pluri_test_score: "32.5"
	pluri_novelty_score: "1.6"
	
}
```

Note that if the article does not report on these results or scores write “None” in the respective field.

## Reprogramming method information retrieval

If the cell line is an induced pluropotent stem cell, retrieve the following information about the reprogramming procedure, otherwise, leave empty strings in the fields:

| Field                           | Information retrieval instructions                                                   |
| ------------------------------- | ------------------------------------------------------------------------------------ |
| ReprogrammingMethod.vector_type | Select the best matching literal for the vector type for the reprogramming procedure |
| ReprogrammingMethod.vector_name | Write the name of the vector                                                         |
| ReprogrammingMethod.kit         | Write the name of the reprogramming kit used                                         |
| ReprogrammingMethod.detected    | Write true if there was any reprogramming method detected and false otherwise        |

```json

reprogramming_method: {

	used: true, 
	vector_type: "Viral reprogramming vector"
	vector_name:
	kit_name:
	

}
```




## Genomic characterisation metadata

Retrieve genomic characterisation metadata from the article using the information in the **instructions table** below.

| DB Table Name           | Field name       | Description and instructions                                                                              | Accepted values               |
| ----------------------- | ---------------- | --------------------------------------------------------------------------------------------------------- | ----------------------------- |
| GenomicCharacterisation | passage_number   | FIll with the passage number from the genomic characterisation results.                                   | Integers                      |
| GenomicCharacterisation | karyotype        | The karyotype of the cell line; see accepted values for what kinds of formatting are acceptable.          | See comments below            |
| GenomicCharacterisation | karyotype_method | Find the method used to karyotype the cell line. Select only from the accepted values in the next column. | {GB, S, CGH, ACGH, MKSNP, KB} |
| GenomicCharacterisation | summary          | Generate a clear and concise summary of the genomic characterisation method and results.                  | Free-text                     |

**Comments**
- There are many accepted values for the karyotype, since there are many karyotypes. At minimum, chromosomal karyotype metadata is needed.
	- Example values:
		- 46, XX
		- arr(1-22)x2,(XY)x1

**Example genomic characterisation object**
```json 
genomic_characterisation: {

	passage_number: "5",
	karyotype: "46, XY",
	karyotype_method: "Molecular Karyotyping by SNP Array"
	summary: "No aneuploidies detected; SNP array analysis confirmed >99.9% identity with parental line."

}
```



## STR fingerprinting information retrieval

If short tandem repeat fingerprinting was performed on the cell line retrieve information for the following entities, otherwise, leave empty strings in the fields:

| Field                | Information retrieval instructions                                                |
| -------------------- | --------------------------------------------------------------------------------- |
| STR_results.exists   | Set this to true if STR fingerprinting was done and false otherwise.              |
| STR_results.loci     | Fill this with information about the loci where the str fingerprint was performed |
| STR_results.group    | Select the most appropriate literal stated in the schema for this field.          |
| STR_results.allele_1 | State the first allele for the STR fingerprinting                                 |
| STR_results.allele_2 | State the second allele for the STR fingerprinting results                        |



## Human induced pluropotent stem cells information retrieval

If the cell line is an human induced pluripotent stem cell (hiPSC) then retrieve information for the following entities, otherwise, write empty strings into the fields otherwise:

| Field                                | Information retrieval instructions                                                                                                         |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| InducedDerivation.i_source_cell_type | Get the cell type for the source cell of the cell line.                                                                                    |
| InducedDerivation.i_cell_origin      | Get the “tissue of origin” for the source cell of the cell line. For example: the tissue of origin might be the liver or the blood.        |
| InducedDerivation.derivation_year    | Get the year the stem cell line was first derived.                                                                                         |
| InducedDerivation.vector_type        | State the type of vector that was used to reprogram / induce pluripotency by selecting the best available literal according to the schema. |
| InducedDerivation.vector_name        | State the name of the reprogramming vector.                                                                                                |
| InducedDerivation.kit_name           | State the name of the reprogramming kit that was used.                                                                                     |




## Embryonic stem cells information retrieval

If the cell line is an embryonic stem cell (ESC) then retrieve information for the following entities, otherwise write empty strings into the fields:

| Field                                              | Information retrieval instructions                                |
| -------------------------------------------------- | ----------------------------------------------------------------- |
| EmbryonicDerivation.embryo_stage                   | State what stage the embryo was at when the cell line was derived |
| EmbryonicDerivation.zp_removal_technique           |                                                                   |
| EmbryonicDerivation.cell_seeding                   |                                                                   |
| EmbryonicDerivation.e_preimplant_genetic_diagnosis |                                                                   |





## Ethics information retrieval 

Retrieve the following information regarding the ethics clearance of the cell line. Note that some cell lines might have multiple ethics clearances, in this case, create multiple Ethics entities which contain the individual clearance information and output this list of Ethics entities.

| Field                     | Information retrieval instructions                       |
| ------------------------- | -------------------------------------------------------- |
| Ethics.ethics_number      | Write the ethics number for the cell line                |
| Ethics.approval_date      | Write the date the ethics approval was granted           |
| Ethics.institutional_HREC | Write the institution associated with the ethics number. |

**Example: single ethics object in ethics list**
```json 
ethics: [
	{
		ethics_number: "1872361",
		approval_date: "21/07/10",
		"institutional_HREC": "University of Queensland Ethics Committee"
	}
]
```

**Example: two ethics objects in the ethics list**

```json 
ethics: [
	{
		ethics_number: "1872361",
		approval_date: "21/07/10",
		"institutional_HREC": "University of Queensland Ethics Committee"
	},
	{
		ethics_number: "1123JHAJ1",
		approval_date: "18/10/10",
		"institutional_HREC": "Biocells Ethics Committee"
	}
]
```

If there you could not find any ethics metadata for the prescribed cell line just insert an empty list in the ethics field.

**Example: no ethics metadata found in the article**

```json 
ethics: []
```


## Microbiology / virology screening information retrieval 

If microbiology / virology screening was performed for the cell line, retrieve information for the following entities, otherwise leave the fields as empty strings:

| Field                                      | Information retrieval instructions                                                |
| ------------------------------------------ | --------------------------------------------------------------------------------- |
| MicrobiologyVirologyScreening.performed    | Set to true if microbiology/virology screening was performed and false otherwise. |
| MicrobiologyVirologyScreening.hiv1         |                                                                                   |
| MicrobiologyVirologyScreening.hiv2         |                                                                                   |
| MicrobiologyVirologyScreening.hep_b        |                                                                                   |
| MicrobiologyVirologyScreening.hep_c        |                                                                                   |
| MicrobiologyVirologyScreening.mycoplasma   |                                                                                   |
| MicrobiologyVirologyScreening.other        |                                                                                   |
| MicrobiologyVirologyScreening.other_result |                                                                                   |

## Culture medium information retrieval

Retrieve the following information regarding the culture conditions and medium of the cell line:

| Field                           | Information retrieval instructions                                                                                        | Values accepted                                                     |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| CultureMedium.co2_concentration | Write the carbon dioxide concentration used to culture the cell line                                                      | Concentration values in the closed interval [0,1]                   |
| CultureMedium.o2_concentration  | Write the oxygen concentration used to culture the cell line. If not reported, write atmospheric oxygen concentration.    | Concentration values in the closed interval [0,1]                   |
| CultureMedium.rho_kinase_sed    |                                                                                                                           | -                                                                   |
| CultureMedium.passage_method    | Write the passage method used while culturing the cell line. Select from one of the accepted values listed in this table. | {Enzymatically, Enzyme-free cell dissociation, Mechanically, Other} |
| CultureMedium.base_medium       | Write the base medium used to culture the cell line                                                                       | -                                                                   |
| CultureMedium.base_coat         | Write the base coat used to culture the cell line                                                                         | -                                                                   |

**Example / expected response format**
```json
culture_medium: {
	co2_concentration: "0.05",
	o2_concentration: "0.21",
	rho_kinase_sed: "None",
	passage_method: "Enzymatically",
	other_passage_method: "None",
	base_medium: 
	base_coat
}
```

