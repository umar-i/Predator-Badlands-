#!/usr/bin/env python3
"""
Run Experiments Script for Predator: Badlands
==============================================
This script runs comprehensive experiments for data collection and analysis.
Executes 20+ simulations per configuration, collects metrics, generates CSV data,
and creates matplotlib visualizations for the report.

Author: Predator Badlands Team
Phase: 10 - Experiments & Data Collection

Usage:
    python run_experiments.py                    # Run all experiments
    python run_experiments.py --quick            # Quick test (5 runs per config)
    python run_experiments.py --config normal    # Run specific config
    python run_experiments.py --configs easy,hard  # Run multiple configs
    python run_experiments.py --runs 30          # Custom number of runs
    python run_experiments.py --no-plots         # Skip plot generation

Output:
    - CSV files with simulation results, agent metrics, honour progression
    - PNG plots with visualizations
    - JSON file with complete experiment data
    - Summary statistics printed to console
"""

import sys
import os
import argparse
import time
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from experiment_runner import (
    ExperimentRunner, ExperimentConfig, EXPERIMENT_CONFIGS,
    DifficultyLevel
)
from experiment_visualizer import ExperimentVisualizer, MATPLOTLIB_AVAILABLE


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Run Predator: Badlands Experiments',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_experiments.py                    # Run all experiments (20 runs each)
    python run_experiments.py --quick            # Quick test (5 runs each)
    python run_experiments.py --config normal    # Run only 'normal' config
    python run_experiments.py --configs easy,hard --runs 25
    python run_experiments.py --all --runs 30   # All configs with 30 runs
        """
    )
    
    parser.add_argument(
        '--quick', '-q',
        action='store_true',
        help='Quick test mode (5 runs per config)'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Single configuration to run (easy, normal, hard, extreme, etc.)'
    )
    
    parser.add_argument(
        '--configs',
        type=str,
        help='Comma-separated list of configurations to run'
    )
    
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Run all available configurations'
    )
    
    parser.add_argument(
        '--runs', '-r',
        type=int,
        default=20,
        help='Number of runs per configuration (default: 20)'
    )
    
    parser.add_argument(
        '--max-turns', '-t',
        type=int,
        default=200,
        help='Maximum turns per simulation (default: 200)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='data/experiments',
        help='Output directory for results (default: data/experiments)'
    )
    
    parser.add_argument(
        '--no-plots',
        action='store_true',
        help='Skip generating matplotlib plots'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        help='Random seed for reproducibility'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    return parser.parse_args()


def print_header():
    """Print experiment header."""
    print("\n" + "=" * 70)
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║         PREDATOR: BADLANDS - EXPERIMENT RUNNER                   ║")
    print("║              Phase 10: Data Collection & Analysis                ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print("=" * 70)
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")


def print_config_info(configs, runs_per_config):
    """Print configuration information."""
    print("\n📋 EXPERIMENT CONFIGURATION:")
    print("-" * 40)
    print(f"  Configurations: {len(configs)}")
    print(f"  Runs per config: {runs_per_config}")
    print(f"  Total runs: {len(configs) * runs_per_config}")
    print("\n  Configs to run:")
    for config in configs:
        print(f"    • {config.name} ({config.difficulty.value})")
    print("-" * 40 + "\n")


def run_experiments(args):
    """Run the experiments based on arguments."""
    
    # Determine configurations to run
    configs_to_run = []
    
    if args.quick:
        # Quick mode: reduced runs
        num_runs = 5
        configs_to_run = [
            ExperimentConfig(name='quick_easy', difficulty=DifficultyLevel.EASY, 
                           num_runs=num_runs, max_turns=100),
            ExperimentConfig(name='quick_normal', difficulty=DifficultyLevel.NORMAL,
                           num_runs=num_runs, max_turns=100),
            ExperimentConfig(name='quick_hard', difficulty=DifficultyLevel.HARD,
                           num_runs=num_runs, max_turns=100),
        ]
    elif args.config:
        # Single config
        if args.config in EXPERIMENT_CONFIGS:
            config = EXPERIMENT_CONFIGS[args.config]
            config.num_runs = args.runs
            config.max_turns = args.max_turns
            if args.seed:
                config.random_seed = args.seed
            configs_to_run = [config]
        else:
            print(f"[ERROR] Unknown config: {args.config}")
            print(f"Available: {', '.join(EXPERIMENT_CONFIGS.keys())}")
            return None
    elif args.configs:
        # Multiple specified configs
        for name in args.configs.split(','):
            name = name.strip()
            if name in EXPERIMENT_CONFIGS:
                config = EXPERIMENT_CONFIGS[name]
                config.num_runs = args.runs
                config.max_turns = args.max_turns
                if args.seed:
                    config.random_seed = args.seed
                configs_to_run.append(config)
            else:
                print(f"[WARNING] Unknown config: {name}, skipping")
    elif args.all:
        # All configurations
        for name, config in EXPERIMENT_CONFIGS.items():
            config.num_runs = args.runs
            config.max_turns = args.max_turns
            if args.seed:
                config.random_seed = args.seed
            configs_to_run.append(config)
    else:
        # Default: core configurations for meaningful comparison
        default_configs = ['easy', 'normal', 'hard', 'extreme']
        for name in default_configs:
            config = EXPERIMENT_CONFIGS[name]
            config.num_runs = args.runs
            config.max_turns = args.max_turns
            if args.seed:
                config.random_seed = args.seed
            configs_to_run.append(config)
            
    if not configs_to_run:
        print("[ERROR] No configurations to run!")
        return None
        
    # Print config info
    print_config_info(configs_to_run, configs_to_run[0].num_runs)
    
    # Initialize runner
    runner = ExperimentRunner(output_dir=args.output)
    
    # Add progress callback
    def progress_callback(current, total, message):
        pct = (current / total) * 100
        bar_len = 30
        filled = int(bar_len * current / total)
        bar = '█' * filled + '░' * (bar_len - filled)
        print(f"\r  Progress: [{bar}] {pct:.1f}% - {message}     ", end='', flush=True)
        
    runner.set_progress_callback(progress_callback)
    
    # Add configs and run
    runner.add_configs(configs_to_run)
    
    print("\n🚀 STARTING EXPERIMENTS...")
    print("-" * 40)
    
    start_time = time.time()
    results = runner.run_all_experiments()
    total_duration = time.time() - start_time
    
    print("\n\n" + "-" * 40)
    print(f"✓ Experiments completed in {total_duration:.1f}s")
    
    # Save results
    print("\n💾 SAVING RESULTS...")
    print("-" * 40)
    saved_files = runner.save_results()
    
    for name, path in saved_files.items():
        print(f"  ✓ {name}: {path}")
        
    # Print summary
    runner.print_summary()
    
    return results


def generate_plots(results, output_dir, skip_plots=False):
    """Generate visualization plots."""
    if skip_plots:
        print("\n[INFO] Skipping plot generation (--no-plots flag)")
        return []
        
    if not MATPLOTLIB_AVAILABLE:
        print("\n[WARNING] matplotlib not installed, skipping plots")
        print("  Install with: pip install matplotlib")
        return []
        
    print("\n📊 GENERATING PLOTS...")
    print("-" * 40)
    
    plots_dir = os.path.join(output_dir, 'plots')
    visualizer = ExperimentVisualizer(plots_dir)
    
    saved_plots = visualizer.generate_all_plots(results)
    
    print(f"\n✓ Generated {len(saved_plots)} plots")
    for path in saved_plots:
        print(f"  • {os.path.basename(path)}")
        
    visualizer.close_all()
    
    return saved_plots


def print_final_summary(results, saved_files, saved_plots, duration):
    """Print final experiment summary."""
    total_runs = sum(len(r) for r in results.values())
    total_wins = sum(
        sum(1 for run in runs if run.boss_defeated)
        for runs in results.values()
    )
    
    print("\n" + "=" * 70)
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                    EXPERIMENT COMPLETE                           ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print("=" * 70)
    print(f"\n📈 FINAL STATISTICS:")
    print(f"  • Total Simulations:    {total_runs}")
    print(f"  • Total Wins (Boss):    {total_wins}")
    print(f"  • Overall Win Rate:     {(total_wins/total_runs*100):.1f}%" if total_runs else "N/A")
    print(f"  • Configurations Run:   {len(results)}")
    print(f"  • Total Duration:       {duration:.1f}s")
    print(f"\n📁 OUTPUT FILES:")
    print(f"  • CSV Files:   {len([f for f in saved_files.values() if f.endswith('.csv')])}")
    print(f"  • JSON Files:  {len([f for f in saved_files.values() if f.endswith('.json')])}")
    print(f"  • Plot Files:  {len(saved_plots)}")
    print("\n" + "=" * 70)
    print("  Results are ready for your report!")
    print("  CSV files can be imported into Excel/Google Sheets")
    print("  Plots are publication-ready PNG images")
    print("=" * 70 + "\n")


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Print header
    print_header()
    
    # Run experiments
    start_time = time.time()
    results = run_experiments(args)
    
    if results is None:
        print("\n[ERROR] Experiment failed!")
        return 1
        
    # Generate plots
    saved_plots = generate_plots(results, args.output, args.no_plots)
    
    # Get saved files from runner
    from data_collector import DataCollector
    dc = DataCollector(args.output)
    saved_files = {
        'csv_files': dc.list_csv_files(),
        'json_files': dc.list_json_files()
    }
    
    # Print final summary
    duration = time.time() - start_time
    print_final_summary(results, saved_files, saved_plots, duration)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
