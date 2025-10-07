"""
Test script for curating articles using vision/OCR processing.

This script tests the curate_article function by processing articles and saving
results organized by PMID folders within timestamped run folders.
"""

import json
import logging
import os
from pathlib import Path
import sys
import time
from datetime import datetime

# Add the package root to Python path for imports
package_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(package_root))

from aus_stem_cell_curate.curation.curate import curate_article

def load_test_config() -> dict:
    """Load test configuration from local config.json file."""
    config_path = Path(__file__).parent / "config.json"

    with open(config_path, "r") as f:
        config = json.load(f)

    return config

def load_usage_costs() -> dict:
    """Load usage costs from local usage_costs.json file."""
    costs_path = Path(__file__).parent / "usage_costs.json"

    with open(costs_path, "r") as f:
        costs = json.load(f)

    return costs

def calculate_cost(usage_data: dict, model: str, costs: dict) -> float:
    """
    Calculate estimated cost for API usage.

    Args:
        usage_data: Dictionary containing token usage (prompt_tokens, completion_tokens)
        model: Model name used for the request
        costs: Cost data loaded from usage_costs.json

    Returns:
        Estimated cost in USD
    """
    if model not in costs:
        return 0.0

    model_costs = costs[model]
    prompt_tokens = usage_data.get("prompt_tokens", 0)
    completion_tokens = usage_data.get("completion_tokens", 0)

    # Costs are per 1 million tokens, so divide by 1,000,000
    input_cost = (prompt_tokens / 1_000_000) * model_costs["input"]
    output_cost = (completion_tokens / 1_000_000) * model_costs["output"]

    return input_cost + output_cost

def setup_run_logging(run_dir: Path) -> logging.Logger:
    """
    Set up logging for the test run and all curation functions.

    Args:
        run_dir: Directory for this test run

    Returns:
        Configured logger
    """
    log_file = run_dir / "test_run.log"

    # Configure root logger to capture all logging from curate.py functions
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Clear any existing handlers
    root_logger.handlers.clear()

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter - include logger name to distinguish between test and curation logs
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Return a named logger for test-specific messages
    return logging.getLogger('curate_test')

def test_curate_scr_articles():
    """
    Main test function that curates articles and saves results.
    """
    # Generate timestamp-based run ID (YYMMDD_HHMMSS)
    run_id = datetime.now().strftime("%y%m%d_%H%M%S")
    
    # Load test configuration and usage costs
    config = load_test_config()
    costs = load_usage_costs()

    # Extract test parameters
    model = config['model']

    # Extract curation parameters (to pass to curate_article)
    # Exclude test-specific fields that aren't needed by curate_article
    excluded_fields = ['output_path', 'articles_path']
    curation_config = {k: v for k, v in config.items() if k not in excluded_fields}

    # Set up paths from config
    test_dir = Path(__file__).parent

    # Use articles_path from config (can be relative or absolute)
    articles_path = Path(config['articles_path'])
    if not articles_path.is_absolute():
        articles_dir = test_dir.parent.parent / articles_path  # Relative to project root
    else:
        articles_dir = articles_path

    # Use output_path from config (can be relative or absolute)
    output_path = Path(config['output_path'])
    if not output_path.is_absolute():
        results_base_dir = test_dir.parent.parent / output_path  # Relative to project root
    else:
        results_base_dir = output_path

    run_dir = results_base_dir / run_id
    
    # Create run-specific directory
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # Set up logging
    logger = setup_run_logging(run_dir)
    
    logger.info(f"Starting test run with ID: {run_id}")
    
    # Log full configuration immediately after run ID
    logger.info("Test Configuration (loaded from config.json):")
    for key, value in config.items():
        logger.info(f"  {key}: {value}")
    
    # Get articles to test (filtered by PMIDs)
    pmid_list = config.get('pmid_list', ['*'])
    articles = get_articles(articles_dir, pmid_list)

    logger.info(f"Testing {len(articles)} articles (controlled by pmid_list)")
    
    
    logger.info(f"Found {len(articles)} articles to process:")
    for article in articles:
        logger.info(f"  - {article.name}")
    
    # Track all failed cell lines across all articles
    all_failed_cell_lines = []
    failed_articles = []  # Track articles that completely failed
    no_cell_line_articles = []  # Track articles with no cell lines found
    processed_articles = 0
    total_curated_cell_lines = 0
    total_estimated_cost = 0.0
    total_curation_time = 0.0
    
    # Process each article
    for i, article_path in enumerate(articles, 1):
        logger.info(f"[{i}/{len(articles)}] Processing: {article_path.name}")
        
        try:
            # Read the article
            with open(article_path, 'rb') as f:
                article_content = f.read()
            
            # Curate the article with timing
            logger.info(f"  Curating article...")
            article_start_time = time.time()
            results = curate_article(article_content, curation_config)
            article_end_time = time.time()
            article_total_time = article_end_time - article_start_time
            
            # Handle different result types
            if isinstance(results, str):
                # Error occurred or no cell lines found
                if results == "-1":
                    logger.info(f"  No cell lines found in article")
                    no_cell_line_articles.append(article_path.name)
                else:
                    logger.error(f"  Error occurred: {results}")
                    failed_articles.append({"name": article_path.name, "error": results})
                    # Save error for debugging
                    error_file = run_dir / f"{article_path.stem}_ERROR.txt"
                    with open(error_file, 'w') as f:
                        f.write(f"Error processing {article_path.name}:\n\n{results}")
            
            elif isinstance(results, dict):
                # Successful curation
                processed_articles += 1
                total_cell_lines = results.get('total_cell_lines', 0)
                successful_curations = results.get('successful_curations', 0)
                failed_cell_lines = results.get('failed_cell_lines', [])
                usage_metadata = results.get('usage_metadata', {})

                # Calculate costs and extract timing
                article_cost = 0.0
                identification_time = 0.0
                total_cell_line_time = 0.0

                if usage_metadata:
                    # Cost and timing for cell line identification
                    identification_usage = usage_metadata.get('identification_usage', {})
                    if identification_usage:
                        id_cost = calculate_cost(identification_usage, model, costs)
                        article_cost += id_cost
                        identification_time = identification_usage.get('identification_time_seconds', 0.0)

                    # Cost and timing for individual cell line curations
                    curation_usage_list = usage_metadata.get('curation_usage', [])
                    for curation_usage in curation_usage_list:
                        curation_cost = calculate_cost(curation_usage, model, costs)
                        article_cost += curation_cost
                        cell_line_time = curation_usage.get('curation_time_seconds', 0.0)
                        total_cell_line_time += cell_line_time

                        # Log timing for individual cell line
                        cell_line_name = curation_usage.get('cell_line', 'Unknown')
                        logger.info(f"    Cell line '{cell_line_name}' curation time: {cell_line_time:.2f}s")

                total_estimated_cost += article_cost
                total_curation_time += article_total_time

                logger.info(f"  Found {total_cell_lines} cell lines")
                logger.info(f"  Successfully curated {successful_curations} cell lines")
                logger.info(f"  Identification time: {identification_time:.2f}s")
                logger.info(f"  Total cell line curation time: {total_cell_line_time:.2f}s")
                logger.info(f"  Total article time: {article_total_time:.2f}s")
                logger.info(f"  Estimated cost: ${article_cost:.4f}")

                if failed_cell_lines:
                    logger.warning(f"  Failed cell lines: {failed_cell_lines}")
                    all_failed_cell_lines.extend(failed_cell_lines)

                # Save results (pass run_dir and article PMID)
                article_pmid = article_path.stem  # Assuming filename is PMID.pdf
                save_results(results, run_dir, article_pmid, logger)
                total_curated_cell_lines += successful_curations
            
            logger.info(f"  Completed processing {article_path.name}")
            
        except Exception as e:
            logger.error(f"  Unexpected error processing {article_path.name}: {str(e)}")
            failed_articles.append({"name": article_path.name, "error": f"Exception: {str(e)}"})
            # Save error for debugging
            error_file = run_dir / f"{article_path.stem}_EXCEPTION.txt"
            with open(error_file, 'w') as f:
                f.write(f"Exception processing {article_path.name}:\n\n{str(e)}")
    
    # Save failed cell lines summary
    # Save failed cell lines summary
    if all_failed_cell_lines:
        failed_file = run_dir / "failed_cell_lines.txt"
        with open(failed_file, 'w') as f:
            f.write("Failed Cell Lines\n")
            f.write("=================\n\n")
            for cell_line in all_failed_cell_lines:
                f.write(f"{cell_line}\n")
        logger.info(f"Saved {len(all_failed_cell_lines)} failed cell lines to: failed_cell_lines.txt")

    # Calculate summary statistics
    total_articles = len(articles)
    successful_articles = processed_articles
    failed_article_count = len(failed_articles)
    no_cell_line_count = len(no_cell_line_articles)

    # Save failed articles summary
    if failed_articles:
        failed_articles_file = run_dir / "failed_articles.txt"
        with open(failed_articles_file, 'w') as f:
            f.write(f"Failed Articles Summary\n")
            f.write(f"======================\n\n")
            f.write(f"Total articles attempted: {total_articles}\n")
            f.write(f"Successfully processed: {successful_articles}\n")
            f.write(f"Failed to process: {failed_article_count}\n")
            f.write(f"No cell lines found: {no_cell_line_count}\n\n")

            if failed_articles:
                f.write(f"FAILED ARTICLES ({len(failed_articles)}):\n")
                f.write(f"-" * 40 + "\n")
                for i, failed in enumerate(failed_articles, 1):
                    f.write(f"{i}. {failed['name']}\n")
                    f.write(f"   Error: {failed['error']}\n\n")

            if no_cell_line_articles:
                f.write(f"ARTICLES WITH NO CELL LINES ({len(no_cell_line_articles)}):\n")
                f.write(f"-" * 40 + "\n")
                for i, article in enumerate(no_cell_line_articles, 1):
                    f.write(f"{i}. {article}\n")

        logger.info(f"Saved failed articles summary to: failed_articles.txt")
    
    # Calculate timing statistics
    avg_time_per_article = total_curation_time / processed_articles if processed_articles > 0 else 0.0
    avg_time_per_cell_line = total_curation_time / total_curated_cell_lines if total_curated_cell_lines > 0 else 0.0
    avg_time_per_20_articles = avg_time_per_article * 20 if avg_time_per_article > 0 else 0.0

    # Log detailed summary of failed articles

    logger.info(f"\n" + "="*60)
    logger.info(f"CURATION RUN SUMMARY")
    logger.info(f"="*60)
    logger.info(f"Run ID: {run_id}")
    logger.info(f"Model used: {model}")
    logger.info(f"\nARTICLE PROCESSING:")
    logger.info(f"  Total articles: {total_articles}")
    logger.info(f"  Successfully processed: {successful_articles}")
    logger.info(f"  Failed to process: {failed_article_count}")
    logger.info(f"  No cell lines found: {no_cell_line_count}")

    if failed_articles:
        logger.error(f"\nFAILED ARTICLES ({len(failed_articles)}):")
        for i, failed in enumerate(failed_articles, 1):
            logger.error(f"  {i}. {failed['name']} - {failed['error'][:100]}...")

    if no_cell_line_articles:
        logger.info(f"\nARTICLES WITH NO CELL LINES ({len(no_cell_line_articles)}):")
        for i, article in enumerate(no_cell_line_articles, 1):
            logger.info(f"  {i}. {article}")

    logger.info(f"\nCELL LINE PROCESSING:")
    logger.info(f"  Total curated cell lines: {total_curated_cell_lines}")
    logger.info(f"  Total failed cell lines: {len(all_failed_cell_lines)}")
    logger.info(f"\nPERFORMANCE:")
    logger.info(f"  Total curation time: {total_curation_time:.2f}s")
    logger.info(f"Average time per article: {avg_time_per_article:.2f}s")
    logger.info(f"Average time per 20 articles: {avg_time_per_20_articles:.2f}s ({avg_time_per_20_articles/60:.1f} min)")
    logger.info(f"Average time per cell line: {avg_time_per_cell_line:.2f}s")
    logger.info(f"Total estimated cost: ${total_estimated_cost:.4f}")
    logger.info(f"\nResults saved to: {run_dir}")
    logger.info(f"="*60)

    print(f"\nTest run completed! Run ID: {run_id}")
    print(f"Model: {model}")
    print(f"Total articles: {total_articles}")
    print(f"Successfully processed: {successful_articles}")
    print(f"Failed to process: {failed_article_count}")
    print(f"No cell lines found: {no_cell_line_count}")
    print(f"Total curated cell lines: {total_curated_cell_lines}")
    print(f"Total curation time: {total_curation_time:.2f}s")

    if failed_articles:
        print(f"\nFailed articles: {[f['name'] for f in failed_articles]}")
    print(f"Average time per article: {avg_time_per_article:.2f}s")
    print(f"Average time per 20 articles: {avg_time_per_20_articles:.2f}s ({avg_time_per_20_articles/60:.1f} min)")
    print(f"Average time per cell line: {avg_time_per_cell_line:.2f}s")
    print(f"Total estimated cost: ${total_estimated_cost:.4f}")
    print(f"Results saved to: {run_dir}")

    if failed_articles or no_cell_line_articles:
        print(f"\nCheck failed_articles.txt for detailed failure information.")

def get_articles(articles_dir: Path, pmid_list: list = None) -> list:
    """
    Get articles from the SCR articles directory, filtered by PMIDs.

    Args:
        articles_dir: Path to the articles directory
        pmid_list: List of PMIDs to filter by, or ['*'] for all articles

    Returns:
        List of article file paths
    """
    # Get all PDF files
    all_article_files = sorted([f for f in articles_dir.iterdir() if f.suffix == '.pdf'])

    # Filter by PMIDs if specified and not '*'
    if pmid_list and pmid_list != ['*']:
        filtered_files = []
        for article_file in all_article_files:
            # Article filename stem should be the PMID
            article_pmid = article_file.stem
            if article_pmid in pmid_list:
                filtered_files.append(article_file)
        article_files = sorted(filtered_files)
    else:
        # Use all articles if pmid_list is None, empty, or contains '*'
        article_files = all_article_files

    return article_files

def is_valid_json(response: str) -> tuple[bool, dict]:
    """
    Check if the response contains valid JSON.
    
    Args:
        response: The response string from curate_article
    
    Returns:
        Tuple of (is_valid, parsed_json_or_none)
    """
    try:
        # Look for JSON code blocks first
        if "```json" in response:
            json_start = response.find("```json") + 7
            json_end = response.find("```", json_start)
            if json_end != -1:
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response[json_start:].strip()
        else:
            # Try to parse the entire response as JSON
            json_str = response.strip()
        
        parsed = json.loads(json_str)
        return True, parsed
    except (json.JSONDecodeError, ValueError):
        return False, None

def save_results(results: dict, run_dir: Path, article_pmid: str, logger: logging.Logger):
    """
    Save curation results to JSON files organized by PMID folders.

    Args:
        results: Dictionary containing curation results
        run_dir: Path to run directory
        article_pmid: PMID of the source article
        logger: Logger instance
    """
    # Create PMID-specific folder within the run directory
    pmid_dir = run_dir / article_pmid
    pmid_dir.mkdir(parents=True, exist_ok=True)

    # Save individual cell line metadata
    curated_data = results.get("curated_data", {})
    for cell_line, metadata in curated_data.items():
        is_valid, parsed_json = is_valid_json(metadata)

        if is_valid:
            # Extract hpscregname from the parsed JSON for filename
            hpscregname = parsed_json.get("hpscregname", cell_line)
            metadata_file = pmid_dir / f"{hpscregname}_m.json"
            with open(metadata_file, 'w') as f:
                json.dump(parsed_json, f, indent=2)
            logger.info(f"    Saved valid metadata for {hpscregname}")
        else:
            # Save invalid responses for debugging in PMID folder
            error_file = pmid_dir / f"{cell_line}_INVALID.txt"
            with open(error_file, 'w') as f:
                f.write(f"Invalid JSON response for {cell_line}:\n\n{metadata}")
            logger.warning(f"    Saved invalid response for {cell_line} to error file")


if __name__ == "__main__":
    test_curate_scr_articles()
