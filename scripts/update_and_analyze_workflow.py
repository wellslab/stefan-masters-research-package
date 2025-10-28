#!/usr/bin/env python3
"""
Automated workflow for updating CSV data and running recall analysis.

This script automates the common sequence of:
1. Reconstructing JSON files from updated CSV data
2. Running recall analysis on sample cell lines
3. Generating summary reports

Usage:
    python scripts/update_and_analyze_workflow.py [--sample-cell-lines CELL1,CELL2,...]
"""

import argparse
import subprocess
import sys
from pathlib import Path
import json
from typing import List, Optional


def run_command(cmd: List[str], description: str, cwd: Optional[Path] = None) -> bool:
    """Run a command and return success status."""
    print(f"\n🔄 {description}")
    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
        print("✅ Success!")
        if result.stdout.strip():
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed with exit code {e.returncode}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def reconstruct_json_files(project_root: Path) -> bool:
    """Reconstruct JSON files from the updated CSV data."""
    results_processing_dir = project_root / "results_processing"
    cmd = [
        "poetry", "run", "python", "reconstruct_from_combined.py",
        "--config", "config_reconstruct_cleaned.json"
    ]
    return run_command(cmd, "Reconstructing JSON files from updated CSV", cwd=results_processing_dir)


def analyze_single_cell_line(project_root: Path, cell_line: str, model: str = "gpt-4.1") -> dict:
    """Analyze recall for a single cell line."""
    gt_file = project_root / f"results/cleaned_results/ground_truth/{cell_line}_gt.json"
    model_file = project_root / f"results/cleaned_results/model_output/{model}/{cell_line}_m.json"

    if not gt_file.exists():
        print(f"⚠️ Ground truth file not found: {gt_file}")
        return {"error": f"GT file not found: {gt_file}"}

    if not model_file.exists():
        print(f"⚠️ Model file not found: {model_file}")
        return {"error": f"Model file not found: {model_file}"}

    print(f"\n📊 Analyzing {cell_line} ({model})")

    # Run single-item recall
    cmd_single = [
        "poetry", "run", "python",
        "scoring/cell_line_recall/single_item_recall.py",
        str(gt_file), str(model_file)
    ]

    # Run multi-item recall
    cmd_multi = [
        "poetry", "run", "python",
        "scoring/cell_line_recall/multi_item_recall.py",
        str(gt_file), str(model_file)
    ]

    print("\n--- Single-Item Array Recall ---")
    single_success = run_command(cmd_single, f"Single-item recall for {cell_line}", cwd=project_root)

    print("\n--- Multi-Item Array Recall ---")
    multi_success = run_command(cmd_multi, f"Multi-item recall for {cell_line}", cwd=project_root)

    return {
        "cell_line": cell_line,
        "model": model,
        "single_item_success": single_success,
        "multi_item_success": multi_success
    }


def main():
    parser = argparse.ArgumentParser(description='Update CSV data and run recall analysis workflow')
    parser.add_argument('--sample-cell-lines',
                       default='AIBNi017-A,MCRIi010-A',
                       help='Comma-separated list of cell lines to analyze (default: AIBNi017-A,MCRIi010-A)')
    parser.add_argument('--model',
                       default='gpt-4.1',
                       help='Model to analyze (default: gpt-4.1)')
    parser.add_argument('--skip-reconstruction',
                       action='store_true',
                       help='Skip JSON reconstruction step')

    args = parser.parse_args()

    # Get project root directory
    project_root = Path(__file__).parent.parent.absolute()
    print(f"🏠 Project root: {project_root}")

    # Parse sample cell lines
    sample_cell_lines = [cl.strip() for cl in args.sample_cell_lines.split(',')]

    print(f"🧬 Sample cell lines: {sample_cell_lines}")
    print(f"🤖 Model: {args.model}")

    # Step 1: Reconstruct JSON files (unless skipped)
    if not args.skip_reconstruction:
        if not reconstruct_json_files(project_root):
            print("❌ JSON reconstruction failed. Exiting.")
            sys.exit(1)
    else:
        print("⏭️ Skipping JSON reconstruction")

    # Step 2: Analyze sample cell lines
    print(f"\n🔬 Analyzing {len(sample_cell_lines)} sample cell lines...")

    results = []
    for cell_line in sample_cell_lines:
        result = analyze_single_cell_line(project_root, cell_line, args.model)
        results.append(result)

    # Step 3: Summary
    print(f"\n📋 WORKFLOW SUMMARY")
    print("=" * 50)

    successful_analyses = 0
    for result in results:
        if "error" in result:
            print(f"❌ {result['cell_line']}: {result['error']}")
        else:
            single_status = "✅" if result["single_item_success"] else "❌"
            multi_status = "✅" if result["multi_item_success"] else "❌"
            print(f"{single_status}{multi_status} {result['cell_line']}: Single={single_status[0]} Multi={multi_status[0]}")
            if result["single_item_success"] and result["multi_item_success"]:
                successful_analyses += 1

    print(f"\n🎯 Successfully analyzed: {successful_analyses}/{len(sample_cell_lines)} cell lines")

    # Save results
    results_file = project_root / "workflow_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": str(Path().cwd()),
            "sample_cell_lines": sample_cell_lines,
            "model": args.model,
            "results": results
        }, f, indent=2)

    print(f"💾 Results saved to: {results_file}")


if __name__ == "__main__":
    main()