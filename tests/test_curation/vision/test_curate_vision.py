"""
Test script for curating SCR (Stem Cell Registry) articles using vision/OCR processing.

This script tests the curate_article function by processing the first N articles
from the articles/scr folder and saving valid JSON results in UUID-named run folders.
"""

import json
import logging
import os
from pathlib import Path
import sys
import uuid
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

def setup_run_logging(run_dir: Path) -> logging.Logger:
    """
    Set up logging for the test run.
    
    Args:
        run_dir: Directory for this test run
    
    Returns:
        Configured logger
    """
    log_file = run_dir / "test_run.log"
    
    # Create logger
    logger = logging.getLogger('curate_test')
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def test_curate_scr_articles():
    """
    Main test function that curates SCR articles and saves results.
    """
    # Generate unique run ID
    run_id = str(uuid.uuid4())
    
    # Load test configuration
    config = load_test_config()
    
    # Extract test parameters
    journal = config['journal']
    num_articles = config['num_articles']
    
    # Extract curation parameters (to pass to curate_article)
    curation_config = {k: v for k, v in config.items() if k not in ['journal', 'num_articles']}

    # Set up paths
    test_dir = Path(__file__).parent
    articles_dir = test_dir.parent / "articles" / journal
    results_base_dir = test_dir / "results"
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
    
    logger.info(f"Testing {num_articles} {journal} articles")
    
    # Get articles to test
    articles = get_articles(articles_dir, num_articles)
    
    logger.info(f"Found {len(articles)} articles to process:")
    for article in articles:
        logger.info(f"  - {article.name}")
    
    # Track all failed cell lines across all articles
    all_failed_cell_lines = []
    processed_articles = 0
    total_curated_cell_lines = 0
    
    # Process each article
    for i, article_path in enumerate(articles, 1):
        logger.info(f"[{i}/{len(articles)}] Processing: {article_path.name}")
        
        try:
            # Read the article
            with open(article_path, 'rb') as f:
                article_content = f.read()
            
            # Curate the article
            logger.info(f"  Curating article...")
            results = curate_article(article_content, curation_config)
            
            # Handle different result types
            if isinstance(results, str):
                # Error occurred or no cell lines found
                if results == "-1":
                    logger.info(f"  No cell lines found in article")
                else:
                    logger.error(f"  Error occurred: {results}")
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
                
                logger.info(f"  Found {total_cell_lines} cell lines")
                logger.info(f"  Successfully curated {successful_curations} cell lines")
                
                if failed_cell_lines:
                    logger.warning(f"  Failed cell lines: {failed_cell_lines}")
                    all_failed_cell_lines.extend(failed_cell_lines)
                
                # Save results
                save_results(results, run_dir, article_path.stem, logger)
                total_curated_cell_lines += successful_curations
            
            logger.info(f"  Completed processing {article_path.name}")
            
        except Exception as e:
            logger.error(f"  Unexpected error processing {article_path.name}: {str(e)}")
            # Save error for debugging
            error_file = run_dir / f"{article_path.stem}_EXCEPTION.txt"
            with open(error_file, 'w') as f:
                f.write(f"Exception processing {article_path.name}:\n\n{str(e)}")
    
    # Save failed cell lines summary
    if all_failed_cell_lines:
        failed_file = run_dir / "failed_cell_lines.txt"
        with open(failed_file, 'w') as f:
            f.write("Failed Cell Lines\n")
            f.write("=================\n\n")
            for cell_line in all_failed_cell_lines:
                f.write(f"{cell_line}\n")
        logger.info(f"Saved {len(all_failed_cell_lines)} failed cell lines to: failed_cell_lines.txt")
    
    logger.info(f"Test run completed!")
    logger.info(f"Run ID: {run_id}")
    logger.info(f"Processed articles: {processed_articles}")
    logger.info(f"Total curated cell lines: {total_curated_cell_lines}")
    logger.info(f"Total failed cell lines: {len(all_failed_cell_lines)}")
    logger.info(f"Results saved to: {run_dir}")
    
    print(f"\nTest run completed! Run ID: {run_id}")
    print(f"Results saved to: {run_dir}")

def get_articles(articles_dir: Path, num_articles: int = None) -> list:
    """
    Get the first N articles from the SCR articles directory.
    
    Args:
        articles_dir: Path to the articles directory
        num_articles: Number of articles to select (None for all)
    
    Returns:
        List of article file paths
    """
    article_files = sorted([f for f in articles_dir.iterdir() if f.suffix == '.pdf'])
    
    if num_articles is None:
        return article_files
    else:
        return article_files[:num_articles]

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

def save_results(results: dict, run_dir: Path, article_name: str, logger: logging.Logger):
    """
    Save curation results to JSON files in the run directory.
    
    Args:
        results: Dictionary containing curation results
        run_dir: Path to run directory
        article_name: Name of the source article (without extension)
        logger: Logger instance
    """
    # Save individual cell line metadata
    curated_data = results.get("curated_data", {})
    for cell_line, metadata in curated_data.items():
        is_valid, parsed_json = is_valid_json(metadata)
        
        if is_valid:
            metadata_file = run_dir / f"{article_name}_{cell_line}.json"
            with open(metadata_file, 'w') as f:
                json.dump(parsed_json, f, indent=2)
            logger.info(f"    Saved valid metadata for {cell_line}")
        else:
            # Save invalid responses for debugging
            error_file = run_dir / f"{article_name}_{cell_line}_INVALID.txt"
            with open(error_file, 'w') as f:
                f.write(f"Invalid JSON response for {cell_line}:\n\n{metadata}")
            logger.warning(f"    Saved invalid response for {cell_line} to error file")


if __name__ == "__main__":
    test_curate_scr_articles()
