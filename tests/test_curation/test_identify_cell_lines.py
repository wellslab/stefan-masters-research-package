"""
Test script for identifying cell lines from articles using vision/OCR processing.

This script tests the identify_cell_lines function by processing articles and saving
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
package_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(package_root))

from aus_stem_cell_curate.curation.curate import identify_cell_lines

def load_test_config(config_file: str = "config.json") -> dict:
    """Load test configuration from specified config file."""
    config_path = Path(__file__).parent / config_file

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
    Set up logging for the test run and all identification functions.

    Args:
        run_dir: Directory for this test run

    Returns:
        Configured logger
    """
    log_file = run_dir / "test_identify_run.log"

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

    # Formatter - include logger name to distinguish between test and identification logs
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Return a named logger for test-specific messages
    return logging.getLogger('identify_test')

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

def save_identification_results(results: dict, run_dir: Path, article_pmid: str, logger: logging.Logger):
    """
    Save cell line identification results to JSON files organized by PMID folders.

    Args:
        results: Dictionary containing identification results
        run_dir: Path to run directory
        article_pmid: PMID of the source article
        logger: Logger instance
    """
    # Create PMID-specific folder within the run directory
    pmid_dir = run_dir / article_pmid
    pmid_dir.mkdir(parents=True, exist_ok=True)

    # Save identification results
    results_file = pmid_dir / f"{article_pmid}_identification.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    logger.info(f"    Saved identification results for {article_pmid}")

    # Also save just the cell line names for easy review
    if "cell_lines" in results and results["cell_lines"] != -1:
        cell_lines_file = pmid_dir / f"{article_pmid}_cell_lines.txt"
        with open(cell_lines_file, 'w') as f:
            f.write(f"Cell lines identified in {article_pmid}:\n")
            f.write("=" * 40 + "\n\n")
            for i, cell_line in enumerate(results["cell_lines"], 1):
                f.write(f"{i}. {cell_line}\n")
        logger.info(f"    Saved cell line list for {article_pmid}")

def test_identify_cell_lines(config_file: str = "config.json"):
    """
    Main test function that identifies cell lines from articles and saves results.
    """
    # Generate timestamp-based run ID (YYMMDD_HHMMSS)
    run_id = datetime.now().strftime("%y%m%d_%H%M%S") + "_identify"

    # Load test configuration and usage costs
    config = load_test_config(config_file)
    costs = load_usage_costs()

    # Extract test parameters
    model = config['model']

    # Extract identification parameters (to pass to identify_cell_lines)
    # Exclude test-specific fields that aren't needed by identify_cell_lines
    excluded_fields = ['output_path', 'articles_path']
    identification_config = {k: v for k, v in config.items() if k not in excluded_fields}

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

    logger.info(f"Starting cell line identification test run with ID: {run_id}")

    # Log full configuration immediately after run ID
    logger.info("Test Configuration (loaded from config.json):")
    for key, value in config.items():
        logger.info(f"  {key}: {value}")

    # Get articles to test (filtered by PMIDs)
    pmid_list = config.get('pmid_list', ['*'])
    articles = get_articles(articles_dir, pmid_list)

    logger.info(f"Testing cell line identification on {len(articles)} articles (controlled by pmid_list)")

    logger.info(f"Found {len(articles)} articles to process:")
    for article in articles:
        logger.info(f"  - {article.name}")

    # Track results across all articles
    all_results = {}
    failed_articles = []  # Track articles that completely failed
    no_cell_line_articles = []  # Track articles with no cell lines found
    processed_articles = 0
    total_cell_lines_found = 0
    total_estimated_cost = 0.0
    total_identification_time = 0.0

    # Process each article
    for i, article_path in enumerate(articles, 1):
        logger.info(f"[{i}/{len(articles)}] Processing: {article_path.name}")

        try:
            # Read the article
            with open(article_path, 'rb') as f:
                article_content = f.read()

            # Identify cell lines with timing
            logger.info(f"  Identifying cell lines...")
            article_start_time = time.time()
            results = identify_cell_lines(article_content, identification_config)
            article_end_time = time.time()
            article_total_time = article_end_time - article_start_time

            # Handle different result types
            if "error" in results:
                # Error occurred
                logger.error(f"  Error occurred: {results['error']}")
                failed_articles.append({"name": article_path.name, "error": results["error"]})
                # Save error for debugging
                error_file = run_dir / f"{article_path.stem}_ERROR.txt"
                with open(error_file, 'w') as f:
                    f.write(f"Error processing {article_path.name}:\n\n{results['error']}")

            else:
                # Successful identification
                processed_articles += 1
                cell_lines = results.get('cell_lines', [])
                usage_metadata = results.get('usage_metadata', {})

                # Calculate costs and extract timing
                article_cost = 0.0
                identification_time = 0.0

                if usage_metadata:
                    article_cost = calculate_cost(usage_metadata, model, costs)
                    identification_time = usage_metadata.get('identification_time_seconds', 0.0)

                total_estimated_cost += article_cost
                total_identification_time += article_total_time

                if cell_lines == -1:
                    logger.info(f"  No cell lines found in article")
                    no_cell_line_articles.append(article_path.name)
                    cell_line_count = 0
                else:
                    cell_line_count = len(cell_lines)
                    total_cell_lines_found += cell_line_count
                    logger.info(f"  Found {cell_line_count} cell lines: {cell_lines}")

                logger.info(f"  Identification time: {identification_time:.2f}s")
                logger.info(f"  Total article time: {article_total_time:.2f}s")
                logger.info(f"  Estimated cost: ${article_cost:.4f}")

                # Save results (pass run_dir and article PMID)
                article_pmid = article_path.stem  # Assuming filename is PMID.pdf
                save_identification_results(results, run_dir, article_pmid, logger)

                # Store results for summary
                all_results[article_pmid] = {
                    "cell_lines": cell_lines,
                    "cell_line_count": cell_line_count,
                    "identification_time": identification_time,
                    "cost": article_cost,
                    "usage_metadata": usage_metadata
                }

            logger.info(f"  Completed processing {article_path.name}")

        except Exception as e:
            logger.error(f"  Unexpected error processing {article_path.name}: {str(e)}")
            failed_articles.append({"name": article_path.name, "error": f"Exception: {str(e)}"})
            # Save error for debugging
            error_file = run_dir / f"{article_path.stem}_EXCEPTION.txt"
            with open(error_file, 'w') as f:
                f.write(f"Exception processing {article_path.name}:\n\n{str(e)}")

    # Save overall summary
    summary = {
        "run_id": run_id,
        "model": model,
        "total_articles": len(articles),
        "processed_articles": processed_articles,
        "failed_articles": len(failed_articles),
        "no_cell_line_articles": len(no_cell_line_articles),
        "total_cell_lines_found": total_cell_lines_found,
        "total_identification_time": total_identification_time,
        "total_estimated_cost": total_estimated_cost,
        "results_by_pmid": all_results
    }

    summary_file = run_dir / "identification_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    # Create simplified PMID -> cell_lines dictionary
    pmid_to_cell_lines = {}
    for pmid, result_data in all_results.items():
        cell_lines = result_data["cell_lines"]
        # Only include PMIDs where cell lines were found (not -1)
        if cell_lines != -1:
            pmid_to_cell_lines[pmid] = cell_lines

    # Save simplified dictionary
    simplified_file = run_dir / "pmid_to_cell_lines.json"
    with open(simplified_file, 'w') as f:
        json.dump(pmid_to_cell_lines, f, indent=2)

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
    avg_time_per_article = total_identification_time / processed_articles if processed_articles > 0 else 0.0
    avg_time_per_cell_line = total_identification_time / total_cell_lines_found if total_cell_lines_found > 0 else 0.0
    avg_time_per_20_articles = avg_time_per_article * 20 if avg_time_per_article > 0 else 0.0

    logger.info(f"\n" + "="*60)
    logger.info(f"CELL LINE IDENTIFICATION RUN SUMMARY")
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

    logger.info(f"\nCELL LINE IDENTIFICATION:")
    logger.info(f"  Total cell lines found: {total_cell_lines_found}")
    logger.info(f"\nPERFORMANCE:")
    logger.info(f"  Total identification time: {total_identification_time:.2f}s")
    logger.info(f"  Average time per article: {avg_time_per_article:.2f}s")
    logger.info(f"  Average time per 20 articles: {avg_time_per_20_articles:.2f}s ({avg_time_per_20_articles/60:.1f} min)")
    logger.info(f"  Average time per cell line: {avg_time_per_cell_line:.2f}s")
    logger.info(f"  Total estimated cost: ${total_estimated_cost:.4f}")
    logger.info(f"\nResults saved to: {run_dir}")
    logger.info(f"="*60)

    print(f"\nCell line identification test run completed! Run ID: {run_id}")
    print(f"Model: {model}")
    print(f"Total articles: {total_articles}")
    print(f"Successfully processed: {successful_articles}")
    print(f"Failed to process: {failed_article_count}")
    print(f"No cell lines found: {no_cell_line_count}")
    print(f"Total cell lines found: {total_cell_lines_found}")
    print(f"Total identification time: {total_identification_time:.2f}s")

    if failed_articles:
        print(f"\nFailed articles: {[f['name'] for f in failed_articles]}")
    print(f"Average time per article: {avg_time_per_article:.2f}s")
    print(f"Average time per 20 articles: {avg_time_per_20_articles:.2f}s ({avg_time_per_20_articles/60:.1f} min)")
    print(f"Average time per cell line: {avg_time_per_cell_line:.2f}s")
    print(f"Total estimated cost: ${total_estimated_cost:.4f}")
    print(f"Results saved to: {run_dir}")

    if failed_articles or no_cell_line_articles:
        print(f"\nCheck failed_articles.txt for detailed failure information.")


if __name__ == "__main__":
    import sys
    # Allow config file to be passed as command line argument
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    test_identify_cell_lines(config_file)