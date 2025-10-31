import json

model_mapping_paths = {
    "gpt-4.1": "scoring/cell_line_categorisation/gpt-4.1_comprehensive_mapping.json",
    "gpt-4.1-mini": "scoring/cell_line_categorisation/gpt-4.1-mini_comprehensive_mapping.json",
    "gpt-4.1-nano": "scoring/cell_line_categorisation/gpt-4.1-nano_comprehensive_mapping.json",
    "gpt-5": "scoring/cell_line_categorisation/gpt-5_comprehensive_mapping.json",
    "gpt-5-mini": "scoring/cell_line_categorisation/gpt-5-mini_comprehensive_mapping.json",
    "gpt-5-nano": "scoring/cell_line_categorisation/gpt-5-nano_comprehensive_mapping.json",
}

# Load scr pmids from experiment configuration file
experiment_config = json.load(open("experiment.json", "r"))
scr_pmids = experiment_config["scr_pmids"]

def run_scoring(identification_results, model):
    results = {}
    exact = 0
    manual = 0
    discovery = 0
    hallucination = 0
    error = 0
    
    pmids = set()   
    for mo_cell_line, result in identification_results.items():
        pmids.add(result["pmid"])
        if result["categorisation"] == "Exact":
            exact += 1
        elif result["categorisation"] == "Manual":
            manual += 1
        elif result["categorisation"] == "Discovery":
            discovery += 1
        elif result["categorisation"] == "Hallucinated Cell Line":
            hallucination += 1
        elif result["categorisation"] == "Error":
            error += 1
    
    # Calculating statistics
    total = exact + manual + discovery + hallucination + error
    articles = len(pmids)
    hallucination_per_twenty_articles = hallucination / (articles / 20)
    error_per_twenty_articles = error / (articles / 20)
    
    model_results = {
        "exact": exact,
        "manual": manual,
        "discovery": discovery,
        "hallucination": hallucination,
        "error": error,
        "total_cell_lines": total,
        "exact_percentage": round((exact / total) * 100, 2),
        "manual_percentage": round((manual / total) * 100, 2),
        "scorable_percentage": round(((exact + manual) / total) * 100, 2),
        "hallucination_per_twenty_articles": round(hallucination_per_twenty_articles, 4),
        "error_per_twenty_articles": round(error_per_twenty_articles, 2),
    }   
    return model_results
        

# Filter the results to score only scr articles
def score_identification_filtered(model_mapping_paths, scr_pmids):
    results = {}
    for model, path in model_mapping_paths.items():
        with open(path, "r") as f:
            identification_results = json.load(f)
            scr_identification_results = {k: v for k, v in identification_results.items() if v["pmid"] in scr_pmids}
            score_results = run_scoring(scr_identification_results, model)
            results[model] = score_results
    
    return results

# Unfiltered scoring results for all models 
def score_identification_unfiltered(model_mapping_paths):
    results = {}
    for model, path in model_mapping_paths.items():
        with open(path, "r") as f:
            identification_results = json.load(f)
            score_results = run_scoring(identification_results, model)
            results[model] = score_results
    return results
            

if __name__ == "__main__":
    
    unfiltered_results = score_identification_unfiltered(model_mapping_paths)
    filtered_results = score_identification_filtered(model_mapping_paths, scr_pmids)
    
    with open("scoring/cell_line_categorisation/identification_scoring_results_unfiltered.json", "w") as f:
        json.dump(unfiltered_results, f, indent=4)
    with open("scoring/cell_line_categorisation/identification_scoring_results_filtered.json", "w") as f:
        json.dump(filtered_results, f, indent=4)
        
    print("Identification scoring results saved to identification_scoring_results_unfiltered.json")
    print("Identification scoring results filtered saved to identification_scoring_results_filtered.json")


        
        
        
        
        