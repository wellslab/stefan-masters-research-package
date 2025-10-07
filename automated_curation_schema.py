from typing import List, Literal, Optional
from pydantic import BaseModel


class Publication(BaseModel):
    doi: str
    pmid: str
    title: str
    first_author: str
    last_author: str
    journal: str
    year: int

class Disease(BaseModel):
    name: str
    description: str
    
    
class Donor(BaseModel):
    age: int
    sex: Literal['Male', 'Female']
    disease: Disease | Literal["Healthy"]



class Contact(BaseModel):
    name: str
    email: str
    phone: str


class MediumComponents(BaseModel):
    medium_component_name: str
    company: str
    component_type: str


class CultureMedium(BaseModel):
    co2_concentration: float
    o2_concentration: float
    rho_kinase_sed: float  # New field
    passage_method: Literal['Enzymatically', 'Enzyme-free cell dissociation', 'Mechanically', 'other']
    other_passage_method: Optional[str]  # New field
    methods_io_id: str  # New field
    base_medium: str
    base_coat: str
    
    


class GenomicCharacterisation(BaseModel):
    passage_number: int
    karyotype: str
    karyotype_method: Literal['G-Banding', 'Spectral', 'Comparative Genomic Hybridisation(CGH)', 'Array CGH', 'Molecular Kartotyping by SNP array', 'Karyolite BoBs']
    summary: str



class EmbryonicDerivation(BaseModel):
    embryo_stage: str  
    zp_removal_technique: str  
    cell_seeding: str  
    e_preimplant_genetic_diagnosis: str  


    

class PluripotencyCharacterisation(BaseModel):
    cell_type: Literal['Endoderm', 'Mesoderm', 'Ectoderm', 'Trophectoderm']
    shown_potency: bool
    marker_list: List[str]
    method: str
    differentiation_profile: Literal['in vivo teratoma', 'in vitro spontaneous differentiation', 
                                  'in vitro directed differentiation', 'scorecard', 'other']
                                  
    


class GenomicAlteration(BaseModel):
    performed: bool
    mutation_type: Literal['variant', 'transgene expression', 'knock out', 'knock in', 'isogenic modification']
    cytoband: str
    delivery_method: str
    loci_name: str
    loci_chromosome: str
    loci_start: int
    loci_end: int
    loci_group: str
    loci_disease: str
    description: str
    genotype: str


class ReprogrammingMethod(BaseModel):
    vector_type: Literal['non-integrated', 'integrated', 'vector-free', 'none']
    vector_name: str
    kit: str
    detected: bool # What is this
    
    
class Ethics(BaseModel):
    ethics_number: str
    institute: str
    approval_date: str
    
    
    
class HLA_Results(BaseModel):
    id: int
    additional_genomic_characteristation: int # foreign key to AdditionalGenomicCharacteristation
    loci: int # foreign key to Loci
    group: Literal['HLA-type-1', 'HLA-type-2', 'Non-HLA']
    allele_1: str
    allele_2: str
    
    
    
    
class STR_Results(BaseModel):
    exists: bool
    loci: int # foreign key to Loci
    group: Literal['HLA-type-1', 'HLA-type-2', 'Non-HLA']
    allele_1: str
    allele_2: str
    
    
    
class Loci(BaseModel):
    name: str
    chromosome: str
    start: int
    end: int
    group: str
    disease: Disease

    
    
class InducedDerivation(BaseModel):
    i_source_cell_type: str
    i_cell_origin: str
    derivation_year: str
    vector_type: str
    vector_name: str
    kit_name: str
    
    

class MicrobiologyVirologyScreening(BaseModel):
    performed: bool
    hiv1: bool
    hiv2: bool
    hep_b: bool
    hep_c: bool
    mycoplasma: bool
    other: bool
    other_result: str





class CellLine(BaseModel):
    hpscreg_id: str
    alt_names: List[str]
    cell_line_type: Literal['hESC', 'hiPSC']
    source: Literal['donor', 'external_institution']
    frozen: bool
    publication: Publication
    donor: Donor
    maintainer: str
    producer: str
    contact: Contact
    source_tissue: str
    source_cell_type: str





if __name__ == "__main__":
    import json 
    models = [
        Publication,
        Disease,
        Donor,
        Contact,
        GenomicCharacterisation,
        CultureMedium,
        PluripotencyCharacterisation,
        GenomicAlteration,
        ReprogrammingMethod,
        Ethics,
        HLA_Results,
        STR_Results,
        Loci,
        InducedDerivation,
        CellLine
    ]
    
    schemas = {model.__name__: model.model_json_schema() for model in models}
    
    with open("resources/schemas/curation_schema.json", "w") as f:
        json.dump(schemas, f, indent=4)

    
    
    

    
    