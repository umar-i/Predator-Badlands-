#!/usr/bin/env python3
"""
====================================================
    Predator: Badlands Simulation
=====================================================

Single script to:
1. Run ALL test cases (Phase 2-10)
2. Run the main project simulation
3. Run quick experiment test

Usage: python umer.py
"""

import sys
import os
import unittest
import time
from datetime import datetime

# Set up paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(SCRIPT_DIR, 'src')
TESTS_DIR = os.path.join(SCRIPT_DIR, 'tests')

sys.path.insert(0, SRC_DIR)
sys.path.insert(0, SCRIPT_DIR)
os.chdir(SCRIPT_DIR)


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_section(title):
    """Print a section divider."""
    print("\n" + "-" * 50)
    print(f"  {title}")
    print("-" * 50)


def run_all_tests():
    """
    Run all test cases from the tests directory.
    Returns: (success_count, failure_count, error_count)
    """
    print_header("PHASE 1: RUNNING ALL TEST CASES")
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # List of test modules to run
    test_modules = [
        'test_p2',
        'test_p3', 
        'test_p4',
        'test_p5',
        'test_p6',
        'test_p7',
        'test_p8',
        'test_p9',
        'test_p10'
    ]
    
    tests_loaded = 0
    
    for test_module in test_modules:
        try:
            test_path = os.path.join(TESTS_DIR, f'{test_module}.py')
            if os.path.exists(test_path):
                # Import and add tests
                tests = loader.discover(TESTS_DIR, pattern=f'{test_module}.py')
                suite.addTests(tests)
                tests_loaded += 1
                print(f"  ✓ Loaded: {test_module}")
            else:
                print(f"  ✗ Not found: {test_module}")
        except Exception as e:
            print(f"  ✗ Error loading {test_module}: {e}")
    
    print(f"\n  Total test modules loaded: {tests_loaded}")
    print("\n  Running tests...\n")
    
    # Run the tests with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print_section("TEST SUMMARY")
    print(f"  Tests Run: {result.testsRun}")
    print(f"  Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    
    return result.testsRun, len(result.failures), len(result.errors)


def run_quick_experiment():
    """Run a quick experiment test."""
    print_header("PHASE 2: RUNNING QUICK EXPERIMENT")
    
    try:
        from experiment_runner import ExperimentRunner, ExperimentConfig, DifficultyLevel
        from experiment_visualizer import ExperimentVisualizer, MATPLOTLIB_AVAILABLE
        
        output_dir = "data/experiments"
        runner = ExperimentRunner(output_dir)
        
        # Quick config - just 3 runs for speed
        configs = [
            ExperimentConfig(
                name="umer_test_easy",
                difficulty=DifficultyLevel.EASY,
                num_runs=3,
                max_turns=30
            ),
            ExperimentConfig(
                name="umer_test_normal", 
                difficulty=DifficultyLevel.NORMAL,
                num_runs=3,
                max_turns=30
            )
        ]
        
        for config in configs:
            runner.add_config(config)
        
        print("  Running experiments...")
        results = runner.run_all_experiments()
        
        # Save results (CSV and JSON)
        saved_files = runner.save_results()
        
        print(f"\n  ✓ Experiments completed!")
        for file_type, file_path in saved_files.items():
            print(f"  ✓ {file_type}: {file_path}")
        
        # Print summary
        runner.print_summary()
        
        # Generate plots if matplotlib available
        if MATPLOTLIB_AVAILABLE:
            print("\n  Generating visualizations...")
            visualizer = ExperimentVisualizer(results)
            plot_dir = os.path.join(output_dir, 'plots')
            os.makedirs(plot_dir, exist_ok=True)
            visualizer.create_all_plots(plot_dir)
            print(f"  ✓ Plots saved to: {plot_dir}")
        else:
            print("  ℹ Matplotlib not available - skipping plots")
            
        return True
        
    except Exception as e:
        print(f"  ✗ Experiment error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_main_simulation():
    """Run the main project simulation."""
    print_header("PHASE 3: RUNNING MAIN SIMULATION")
    
    try:
        from grid import Grid
        from renderer import GridRenderer
        from predator import Dek, PredatorFather, PredatorBrother, PredatorClan
        from synthetic import Thia
        from creatures import WildlifeAgent, BossAdversary
        from event_logger import EventLogger
        from clan_code import (
            YautjaClanCode, ClanTrialManager, HonourTracker,
            ClanRelationship, HonourableAction, ClanCodeViolation
        )
        
        print("  Initializing simulation...")
        
        # Create grid
        grid = Grid(30, 30)
        grid.generate_terrain()
        renderer = GridRenderer(grid)
        logger = EventLogger()
        trial_manager = ClanTrialManager()
        
        # Create agents
        dek = Dek(10, 10)
        thia = Thia(11, 10)
        father = PredatorFather("Elder Kaail", 5, 5)
        brother = PredatorBrother("Cetanu", 15, 10)
        clan_warrior = PredatorClan("Warrior Thar", 8, 8, "warrior")
        wildlife1 = WildlifeAgent("Canyon Beast", "predator", 12, 12)
        wildlife2 = WildlifeAgent("Desert Stalker", "predator", 14, 14)
        boss = BossAdversary("Ultimate Adversary", 25, 25)
        
        honour_tracker = HonourTracker(dek)
        
        father.set_trial_manager(trial_manager)
        father.set_dek_reference(dek)
        brother.set_dek_reference(dek)
        
        agents = [dek, thia, father, brother, clan_warrior, wildlife1, wildlife2, boss]
        
        for agent in agents:
            agent.set_grid(grid)
            
        print("  ✓ Grid created (30x30)")
        print("  ✓ Agents initialized:")
        print(f"    - Dek (Predator protagonist)")
        print(f"    - Thia (Synthetic ally)")
        print(f"    - Elder Kaail (Father)")
        print(f"    - Cetanu (Brother)")
        print(f"    - Warrior Thar (Clan member)")
        print(f"    - Canyon Beast (Wildlife)")
        print(f"    - Desert Stalker (Wildlife)")
        print(f"    - Ultimate Adversary (Boss)")
        
        # Run a few simulation turns
        print("\n  Running 10 simulation turns...\n")
        
        for turn in range(1, 11):
            print(f"  Turn {turn}:", end=" ")
            
            # Simple agent updates
            for agent in agents:
                if hasattr(agent, 'is_alive') and agent.is_alive:
                    if hasattr(agent, 'update'):
                        try:
                            agent.update()
                        except:
                            pass
            
            # Show Dek's status
            print(f"Dek HP: {dek.health}/{dek.max_health}, " +
                  f"Honour: {getattr(dek, 'honour', 'N/A')}, " +
                  f"Pos: ({dek.x}, {dek.y})")
        
        print("\n  ✓ Simulation completed successfully!")
        
        # Show final grid
        print_section("FINAL GRID STATE")
        print(renderer.render())
        
        return True
        
    except Exception as e:
        print(f"  ✗ Simulation error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point - runs everything."""
    start_time = time.time()
    
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  UMER - UNIFIED MAIN EXECUTION RUNNER".center(68) + "║")
    print("║" + "  Predator: Badlands Simulation".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("║" + f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    
    print("\n  Select Mode:")
    print("  1. Run ALL Tests + Experiments + Simulation Demo")
    print("  2. Run Visual GUI (Tkinter Visualizer)")
    print("  3. Run Tests Only")
    print("  4. Run Experiments Only")
    print("  5. Run CLI Simulation Only")
    print()
    
    try:
        choice = input("  Enter choice (1-5) [default=2 for GUI]: ").strip()
        if choice == "" or choice == "2":
            # Run Visual GUI
            run_visual_gui()
            return 0
        elif choice == "1":
            # Run everything
            return run_all_phases()
        elif choice == "3":
            # Tests only
            run_all_tests()
            return 0
        elif choice == "4":
            # Experiments only
            run_quick_experiment()
            return 0
        elif choice == "5":
            # CLI simulation
            run_main_simulation()
            return 0
        else:
            print("  Invalid choice. Running GUI...")
            run_visual_gui()
            return 0
    except KeyboardInterrupt:
        print("\n  Cancelled by user.")
        return 0


def run_visual_gui():
    """Run the visual GUI simulation."""
    print_header("LAUNCHING VISUAL GUI")
    
    try:
        from config import GameConfig
        from visualizer import PredatorVisualizer
        from main import SimulationEngine
        
        print("  Initializing visual simulation...")
        
        config = GameConfig()
        engine = SimulationEngine(config)
        visualizer = PredatorVisualizer(config)
        engine.set_visualizer(visualizer)
        visualizer.set_agents(engine.agents)
        
        visualizer.update_turn(0)
        visualizer.update_weather("Calm")
        engine._update_all_agent_status()
        visualizer.update_alive_count(len([a for a in engine.agents if a.is_alive]))
        if hasattr(engine.dek, 'honour'):
            visualizer.update_honour(engine.dek.honour)
        visualizer.render_grid()
        
        visualizer.log_event("PREDATOR: BADLANDS initialized", "system")
        visualizer.log_event("Press START or SPACE to begin", "system")
        visualizer.log_event("Hover on agents for details", "system")
        
        print("  ✓ GUI Ready! Opening window...")
        print("  ℹ Press SPACE or click START to begin simulation")
        print("  ℹ Close the window to exit\n")
        
        visualizer.run()
        
        print("\n  ✓ GUI closed successfully!")
        return True
        
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        print("  ℹ Make sure tkinter is installed: sudo apt-get install python3-tk")
        return False
    except Exception as e:
        print(f"  ✗ GUI error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_phases():
    """Run all phases - tests, experiments, simulation."""
    start_time = time.time()
    
    results = {
        'tests': {'run': 0, 'failures': 0, 'errors': 0},
        'experiment': False,
        'simulation': False
    }
    
    # Phase 1: Run all tests
    try:
        run, failures, errors = run_all_tests()
        results['tests'] = {'run': run, 'failures': failures, 'errors': errors}
    except Exception as e:
        print(f"\n  ✗ Test phase error: {e}")
    
    # Phase 2: Run quick experiment
    try:
        results['experiment'] = run_quick_experiment()
    except Exception as e:
        print(f"\n  ✗ Experiment phase error: {e}")
    
    # Phase 3: Run main simulation
    try:
        results['simulation'] = run_main_simulation()
    except Exception as e:
        print(f"\n  ✗ Simulation phase error: {e}")
    
    # Final Summary
    elapsed = time.time() - start_time
    
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + "  EXECUTION COMPLETE - FINAL SUMMARY".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    
    print(f"""
  ┌─────────────────────────────────────────────────────────────────┐
  │  TESTS                                                          │
  │    Total Run: {results['tests']['run']:>5}                                           │
  │    Passed:    {results['tests']['run'] - results['tests']['failures'] - results['tests']['errors']:>5}                                           │
  │    Failed:    {results['tests']['failures']:>5}                                           │
  │    Errors:    {results['tests']['errors']:>5}                                           │
  ├─────────────────────────────────────────────────────────────────┤
  │  EXPERIMENT: {'✓ SUCCESS' if results['experiment'] else '✗ FAILED':>10}                                     │
  │  SIMULATION: {'✓ SUCCESS' if results['simulation'] else '✗ FAILED':>10}                                     │
  ├─────────────────────────────────────────────────────────────────┤
  │  Total Time:  {elapsed:.2f} seconds                                      │
  │  Completed:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                             │
  └─────────────────────────────────────────────────────────────────┘
""")
    
    # Return exit code based on results
    if results['tests']['failures'] > 0 or results['tests']['errors'] > 0:
        return 1
    if not results['experiment'] or not results['simulation']:
        return 1
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
