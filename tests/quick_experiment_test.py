"""
Quick Test Script for Phase 10 Experiments
==========================================
Runs a minimal experiment to verify CSV and plot generation.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
os.chdir(os.path.join(os.path.dirname(__file__), '..'))

from experiment_runner import ExperimentRunner, ExperimentConfig, DifficultyLevel
from experiment_visualizer import ExperimentVisualizer, MATPLOTLIB_AVAILABLE

def run_quick_test():
    """Run a quick test experiment."""
    print("=" * 60)
    print("PHASE 10 - Quick Experiment Test")
    print("=" * 60)
    
    # Create output directory
    output_dir = "data/experiments"
    
    # Initialize runner
    runner = ExperimentRunner(output_dir)
    
    # Add quick configs (5 runs each for testing)
    configs = [
        ExperimentConfig(
            name="test_easy",
            difficulty=DifficultyLevel.EASY,
            num_runs=5,
            max_turns=50
        ),
        ExperimentConfig(
            name="test_normal",
            difficulty=DifficultyLevel.NORMAL,
            num_runs=5,
            max_turns=50
        ),
        ExperimentConfig(
            name="test_hard",
            difficulty=DifficultyLevel.HARD,
            num_runs=5,
            max_turns=50
        )
    ]
    
    for config in configs:
        runner.add_config(config)
    
    print(f"\nRunning {len(configs)} configs x 5 runs = {len(configs) * 5} total simulations")
    print("-" * 40)
    
    # Run experiments
    results = runner.run_all_experiments()
    
    # Save CSV results
    print("\n" + "-" * 40)
    print("Saving CSV results...")
    saved_files = runner.save_results()
    
    for name, path in saved_files.items():
        print(f"  ✓ {name}: {path}")
    
    # Print summary
    runner.print_summary()
    
    # Generate plots
    if MATPLOTLIB_AVAILABLE:
        print("\n" + "-" * 40)
        print("Generating plots...")
        visualizer = ExperimentVisualizer(os.path.join(output_dir, "plots"))
        saved_plots = visualizer.generate_all_plots(results)
        
        print(f"\n✓ Generated {len(saved_plots)} plots:")
        for path in saved_plots:
            print(f"  • {os.path.basename(path)}")
        
        visualizer.close_all()
    else:
        print("\n[INFO] matplotlib not available, skipping plots")
    
    # List generated files
    print("\n" + "=" * 60)
    print("OUTPUT FILES GENERATED:")
    print("=" * 60)
    
    csv_dir = os.path.join(output_dir, "csv")
    plots_dir = os.path.join(output_dir, "plots")
    
    if os.path.exists(csv_dir):
        print(f"\nCSV Files ({csv_dir}):")
        for f in os.listdir(csv_dir):
            filepath = os.path.join(csv_dir, f)
            size = os.path.getsize(filepath)
            print(f"  • {f} ({size} bytes)")
    
    if os.path.exists(plots_dir):
        print(f"\nPlot Files ({plots_dir}):")
        for f in os.listdir(plots_dir):
            filepath = os.path.join(plots_dir, f)
            size = os.path.getsize(filepath)
            print(f"  • {f} ({size/1024:.1f} KB)")
    
    print("\n" + "=" * 60)
    print("Quick test complete!")
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    run_quick_test()
