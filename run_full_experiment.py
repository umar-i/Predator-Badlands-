"""
Full Experiment Script for Predator: Badlands
=============================================
Runs the complete experiment suite with 20+ runs per configuration.
Generates comprehensive CSV data and matplotlib plots for the report.

Output:
- CSV: simulation_results, agent_metrics, honour_progression, summary_stats
- Plots: win_rates, survival, honour, combat_stats, resource_efficiency
- JSON: Complete experiment data backup

"""

import sys
import os
import time

# Add src to path
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, 'src')
sys.path.insert(0, src_dir)
os.chdir(script_dir)

from experiment_runner import ExperimentRunner, ExperimentConfig, DifficultyLevel
from experiment_visualizer import ExperimentVisualizer, MATPLOTLIB_AVAILABLE


def run_full_experiment():
    """
    Run the complete Phase 10 experiment suite.
    
    Configurations:
    - Easy: 20 runs (low difficulty baseline)
    - Normal: 20 runs (standard gameplay)
    - Hard: 20 runs (challenging difficulty)
    - Extreme: 20 runs (maximum difficulty)
    
    Total: 80 simulations across 4 difficulty levels
    """
    
    print("\n" + "=" * 70)
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║       PREDATOR: BADLANDS - FULL EXPERIMENT SUITE                   ║")
    print("║            Phase 10: Data Collection & Analysis                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print("=" * 70)
    
    output_dir = "data/experiments"
    runner = ExperimentRunner(output_dir)
    
    # Define experiment configurations (20 runs each)
    configs = [
        ExperimentConfig(
            name="easy",
            difficulty=DifficultyLevel.EASY,
            boss_health_multiplier=0.7,
            wildlife_count=2,
            resource_count=20,
            num_runs=20,
            max_turns=200
        ),
        ExperimentConfig(
            name="normal",
            difficulty=DifficultyLevel.NORMAL,
            boss_health_multiplier=1.0,
            wildlife_count=4,
            resource_count=15,
            num_runs=20,
            max_turns=200
        ),
        ExperimentConfig(
            name="hard",
            difficulty=DifficultyLevel.HARD,
            boss_health_multiplier=1.5,
            wildlife_count=6,
            resource_count=10,
            num_runs=20,
            max_turns=200
        ),
        ExperimentConfig(
            name="extreme",
            difficulty=DifficultyLevel.EXTREME,
            boss_health_multiplier=2.0,
            wildlife_count=8,
            resource_count=5,
            boss_damage_multiplier=1.5,
            num_runs=20,
            max_turns=200
        )
    ]
    
    print(f"\n📋 EXPERIMENT CONFIGURATION:")
    print("-" * 50)
    print(f"  Total Configurations: {len(configs)}")
    print(f"  Runs per Config:      20")
    print(f"  Total Simulations:    {len(configs) * 20}")
    print(f"  Max Turns:            200")
    print("\n  Difficulty Levels:")
    for c in configs:
        print(f"    • {c.name}: boss_hp={c.boss_health_multiplier}x, "
              f"wildlife={c.wildlife_count}, resources={c.resource_count}")
    print("-" * 50)
    
    # Add progress bar
    total_runs = len(configs) * 20
    completed = [0]
    
    def progress(current, total, msg):
        completed[0] = current
        pct = (current / total) * 100
        bar_len = 40
        filled = int(bar_len * current / total)
        bar = '█' * filled + '░' * (bar_len - filled)
        print(f"\r  [{bar}] {pct:5.1f}% ({current}/{total}) {msg[:30]:30}", end='', flush=True)
    
    runner.set_progress_callback(progress)
    
    # Add configurations
    for config in configs:
        runner.add_config(config)
    
    # Run experiments
    print("\n\n🚀 RUNNING EXPERIMENTS...")
    print("-" * 50)
    
    start_time = time.time()
    results = runner.run_all_experiments()
    duration = time.time() - start_time
    
    print(f"\n\n✓ Experiments completed in {duration:.1f}s")
    
    # Save results
    print("\n💾 SAVING RESULTS...")
    print("-" * 50)
    saved_files = runner.save_results()
    
    for name, path in saved_files.items():
        print(f"  ✓ {name}")
    
    # Print summary
    runner.print_summary()
    
    # Generate plots
    if MATPLOTLIB_AVAILABLE:
        print("\n📊 GENERATING VISUALIZATION PLOTS...")
        print("-" * 50)
        
        visualizer = ExperimentVisualizer(os.path.join(output_dir, "plots"))
        saved_plots = visualizer.generate_all_plots(results)
        
        print(f"\n✓ Generated {len(saved_plots)} publication-ready plots:")
        for path in saved_plots:
            print(f"  • {os.path.basename(path)}")
        
        visualizer.close_all()
    
    # Final summary
    print("\n" + "=" * 70)
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                 EXPERIMENT SUITE COMPLETE                          ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print("=" * 70)
    
    total_wins = sum(
        sum(1 for r in runs if r.boss_defeated) 
        for runs in results.values()
    )
    total_runs = sum(len(runs) for runs in results.values())
    
    print(f"\n📈 FINAL RESULTS:")
    print(f"  • Total Simulations:  {total_runs}")
    print(f"  • Total Victories:    {total_wins}")
    print(f"  • Overall Win Rate:   {(total_wins/total_runs*100):.1f}%")
    print(f"  • Duration:           {duration:.1f}s")
    print(f"  • Avg per Simulation: {duration/total_runs*1000:.1f}ms")
    
    print(f"\n📁 OUTPUT FILES:")
    print(f"  • CSV Directory:  {os.path.join(output_dir, 'csv')}")
    print(f"  • Plots Directory: {os.path.join(output_dir, 'plots')}")
    print(f"  • JSON Directory:  {os.path.join(output_dir, 'json')}")
    
    print("\n📝 READY FOR REPORT:")
    print("  • Import CSV files into Excel/Google Sheets")
    print("  • Use PNG plots directly in your report")
    print("  • JSON contains complete experiment data backup")
    
    print("\n" + "=" * 70 + "\n")
    
    return results


if __name__ == "__main__":
    run_full_experiment()
