"""
Phase 10 Tests - Experiments & Data Collection
==============================================
Comprehensive tests for the experiment system including:
- Metrics collection and tracking
- Data persistence (CSV, JSON)
- Experiment runner functionality
- Visualization generation

Author: Predator Badlands Team
"""

import unittest
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from metrics import (
    MetricsCollector, SimulationMetrics, AgentMetrics,
    MetricType, calculate_survival_curve, calculate_honour_progression
)
from data_collector import DataCollector, ExperimentLogger
from experiment_runner import (
    ExperimentRunner, ExperimentConfig, HeadlessSimulation,
    DifficultyLevel, EXPERIMENT_CONFIGS
)


class TestAgentMetrics(unittest.TestCase):
    """Test AgentMetrics dataclass."""
    
    def test_create_agent_metrics(self):
        """Test creating agent metrics."""
        metrics = AgentMetrics(
            agent_id="test_agent",
            agent_type="predator"
        )
        self.assertEqual(metrics.agent_id, "test_agent")
        self.assertEqual(metrics.agent_type, "predator")
        self.assertEqual(metrics.survival_time, 0)
        self.assertEqual(metrics.kills, 0)
        self.assertTrue(metrics.is_alive)
        
    def test_get_win_rate(self):
        """Test win rate calculation."""
        metrics = AgentMetrics(agent_id="test", agent_type="predator")
        
        # No combats
        self.assertEqual(metrics.get_win_rate(), 0.0)
        
        # Some combats
        metrics.combats_initiated = 10
        metrics.combats_won = 7
        self.assertEqual(metrics.get_win_rate(), 0.7)
        
    def test_get_honour_growth(self):
        """Test honour growth calculation."""
        metrics = AgentMetrics(agent_id="test", agent_type="predator")
        
        # No history
        self.assertEqual(metrics.get_honour_growth(), 0.0)
        
        # With history
        metrics.honour_history = [100, 120, 150, 180]
        self.assertEqual(metrics.get_honour_growth(), 80.0)
        
    def test_get_average_honour(self):
        """Test average honour calculation."""
        metrics = AgentMetrics(agent_id="test", agent_type="predator")
        
        # No history
        self.assertEqual(metrics.get_average_honour(), 0.0)
        
        # With history
        metrics.honour_history = [100, 200, 300]
        self.assertEqual(metrics.get_average_honour(), 200.0)
        
    def test_to_dict(self):
        """Test converting metrics to dictionary."""
        metrics = AgentMetrics(
            agent_id="dek",
            agent_type="predator_hero",
            survival_time=150,
            kills=5,
            deaths=0
        )
        
        d = metrics.to_dict()
        self.assertEqual(d['agent_id'], "dek")
        self.assertEqual(d['survival_time'], 150)
        self.assertEqual(d['kills'], 5)
        self.assertIn('win_rate', d)
        

class TestSimulationMetrics(unittest.TestCase):
    """Test SimulationMetrics dataclass."""
    
    def test_create_simulation_metrics(self):
        """Test creating simulation metrics."""
        metrics = SimulationMetrics(
            run_id=1,
            config_name="test_config"
        )
        self.assertEqual(metrics.run_id, 1)
        self.assertEqual(metrics.config_name, "test_config")
        self.assertEqual(metrics.total_steps, 0)
        self.assertFalse(metrics.boss_defeated)
        
    def test_get_average_survival_time(self):
        """Test average survival time calculation."""
        metrics = SimulationMetrics(run_id=1, config_name="test")
        
        # No agents
        self.assertEqual(metrics.get_average_survival_time(), 0.0)
        
        # Add agents
        metrics.agent_metrics["a1"] = AgentMetrics("a1", "p", survival_time=100)
        metrics.agent_metrics["a2"] = AgentMetrics("a2", "p", survival_time=200)
        
        self.assertEqual(metrics.get_average_survival_time(), 150.0)
        
    def test_get_total_kills(self):
        """Test total kills calculation."""
        metrics = SimulationMetrics(run_id=1, config_name="test")
        
        metrics.agent_metrics["a1"] = AgentMetrics("a1", "p", kills=5)
        metrics.agent_metrics["a2"] = AgentMetrics("a2", "p", kills=3)
        
        self.assertEqual(metrics.get_total_kills(), 8)
        
    def test_get_resource_efficiency(self):
        """Test resource efficiency calculation."""
        metrics = SimulationMetrics(run_id=1, config_name="test")
        
        # No resources
        self.assertEqual(metrics.get_resource_efficiency(), 0.0)
        
        # With resources
        metrics.total_resources_spawned = 100
        metrics.total_resources_collected = 75
        self.assertEqual(metrics.get_resource_efficiency(), 0.75)
        
    def test_to_dict(self):
        """Test converting simulation metrics to dictionary."""
        metrics = SimulationMetrics(
            run_id=1,
            config_name="test",
            total_steps=150,
            boss_defeated=True
        )
        
        d = metrics.to_dict()
        self.assertEqual(d['run_id'], 1)
        self.assertEqual(d['config_name'], "test")
        self.assertEqual(d['total_steps'], 150)
        self.assertTrue(d['boss_defeated'])


class TestMetricsCollector(unittest.TestCase):
    """Test MetricsCollector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.collector = MetricsCollector()
        
    def test_start_simulation(self):
        """Test starting a simulation."""
        self.collector.start_simulation(1, "test_config")
        
        self.assertIsNotNone(self.collector.current_run)
        self.assertEqual(self.collector.current_run.run_id, 1)
        self.assertEqual(self.collector.current_run.config_name, "test_config")
        
    def test_register_agent(self):
        """Test registering agents."""
        self.collector.start_simulation(1, "test")
        self.collector.register_agent("dek", "predator")
        
        self.assertIn("dek", self.collector.current_run.agent_metrics)
        self.assertEqual(
            self.collector.current_run.agent_metrics["dek"].agent_type,
            "predator"
        )
        
    def test_record_honour(self):
        """Test recording honour values."""
        self.collector.start_simulation(1, "test")
        self.collector.register_agent("dek", "predator")
        
        self.collector.record_honour("dek", 100.0)
        self.collector.record_honour("dek", 120.0)
        self.collector.record_honour("dek", 150.0)
        
        history = self.collector.current_run.agent_metrics["dek"].honour_history
        self.assertEqual(len(history), 3)
        self.assertEqual(history[-1], 150.0)
        
    def test_record_combat(self):
        """Test recording combat events."""
        self.collector.start_simulation(1, "test")
        self.collector.register_agent("dek", "predator")
        self.collector.register_agent("enemy", "wildlife")
        
        self.collector.record_combat("dek", "enemy", won=True)
        
        self.assertEqual(self.collector.current_run.total_combats, 1)
        dek = self.collector.current_run.agent_metrics["dek"]
        self.assertEqual(dek.combats_initiated, 1)
        self.assertEqual(dek.combats_won, 1)
        self.assertEqual(dek.kills, 1)
        
    def test_record_death(self):
        """Test recording death events."""
        self.collector.start_simulation(1, "test")
        self.collector.register_agent("wildlife", "enemy")
        
        self.collector.record_step(50)
        self.collector.record_death("wildlife")
        
        wildlife = self.collector.current_run.agent_metrics["wildlife"]
        self.assertEqual(wildlife.deaths, 1)
        self.assertFalse(wildlife.is_alive)
        self.assertEqual(wildlife.survival_time, 50)
        
    def test_end_simulation(self):
        """Test ending a simulation."""
        self.collector.start_simulation(1, "test")
        self.collector.register_agent("dek", "predator")
        self.collector.record_step(100)
        
        result = self.collector.end_simulation()
        
        self.assertIsNotNone(result)
        self.assertEqual(result.run_id, 1)
        self.assertEqual(result.total_steps, 100)
        self.assertIsNone(self.collector.current_run)
        self.assertEqual(len(self.collector.all_runs), 1)
        
    def test_get_aggregate_stats(self):
        """Test getting aggregate statistics."""
        # Run 1
        self.collector.start_simulation(1, "test")
        self.collector.register_agent("dek", "p")
        self.collector.record_step(100)
        self.collector.set_boss_defeated(True)
        self.collector.end_simulation()
        
        # Run 2
        self.collector.start_simulation(2, "test")
        self.collector.register_agent("dek", "p")
        self.collector.record_step(150)
        self.collector.set_boss_defeated(False)
        self.collector.end_simulation()
        
        stats = self.collector.get_aggregate_stats()
        
        self.assertEqual(stats['total_runs'], 2)
        self.assertEqual(stats['average_steps'], 125.0)
        self.assertEqual(stats['boss_defeat_rate'], 0.5)


class TestExperimentConfig(unittest.TestCase):
    """Test ExperimentConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = ExperimentConfig(name="test")
        
        self.assertEqual(config.name, "test")
        self.assertEqual(config.difficulty, DifficultyLevel.NORMAL)
        self.assertEqual(config.grid_size, (30, 30))
        self.assertEqual(config.max_turns, 200)
        self.assertEqual(config.num_runs, 20)
        
    def test_custom_config(self):
        """Test custom configuration."""
        config = ExperimentConfig(
            name="hard_test",
            difficulty=DifficultyLevel.HARD,
            boss_health_multiplier=1.5,
            wildlife_count=6,
            num_runs=30
        )
        
        self.assertEqual(config.name, "hard_test")
        self.assertEqual(config.difficulty, DifficultyLevel.HARD)
        self.assertEqual(config.boss_health_multiplier, 1.5)
        self.assertEqual(config.wildlife_count, 6)
        self.assertEqual(config.num_runs, 30)
        
    def test_predefined_configs(self):
        """Test predefined configurations exist."""
        self.assertIn('easy', EXPERIMENT_CONFIGS)
        self.assertIn('normal', EXPERIMENT_CONFIGS)
        self.assertIn('hard', EXPERIMENT_CONFIGS)
        self.assertIn('extreme', EXPERIMENT_CONFIGS)
        
    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = ExperimentConfig(name="test", num_runs=10)
        d = config.to_dict()
        
        self.assertEqual(d['name'], "test")
        self.assertEqual(d['num_runs'], 10)
        self.assertIn('difficulty', d)
        self.assertIn('grid_size', d)


class TestDataCollector(unittest.TestCase):
    """Test DataCollector class."""
    
    def setUp(self):
        """Set up test fixtures with temp directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.collector = DataCollector(self.temp_dir)
        
    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_directory_creation(self):
        """Test that directories are created."""
        self.assertTrue(os.path.exists(self.collector.csv_dir))
        self.assertTrue(os.path.exists(self.collector.plots_dir))
        self.assertTrue(os.path.exists(self.collector.json_dir))
        
    def test_save_simulation_results_csv(self):
        """Test saving simulation results to CSV."""
        results = [
            SimulationMetrics(run_id=1, config_name="test", total_steps=100),
            SimulationMetrics(run_id=2, config_name="test", total_steps=150),
        ]
        
        filepath = self.collector.save_simulation_results_csv(results)
        
        self.assertTrue(os.path.exists(filepath))
        
        # Check contents
        with open(filepath, 'r') as f:
            content = f.read()
            self.assertIn("run_id", content)
            self.assertIn("config_name", content)
            self.assertIn("total_steps", content)
            
    def test_save_agent_metrics_csv(self):
        """Test saving agent metrics to CSV."""
        metrics = [
            AgentMetrics(agent_id="dek", agent_type="predator", kills=5),
            AgentMetrics(agent_id="thia", agent_type="synthetic", kills=2),
        ]
        
        filepath = self.collector.save_agent_metrics_csv(metrics, run_id=1)
        
        self.assertTrue(os.path.exists(filepath))
        
    def test_save_experiment_json(self):
        """Test saving experiment data as JSON."""
        runs = [SimulationMetrics(run_id=1, config_name="test")]
        config = {"name": "test", "runs": 1}
        
        filepath = self.collector.save_experiment_json(runs, config)
        
        self.assertTrue(os.path.exists(filepath))
        
        # Load and verify
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.assertIn('session_id', data)
            self.assertIn('runs', data)
            self.assertEqual(len(data['runs']), 1)


class TestExperimentLogger(unittest.TestCase):
    """Test ExperimentLogger class."""
    
    def test_log_messages(self):
        """Test logging messages."""
        logger = ExperimentLogger(verbose=False)
        
        logger.info("Test info")
        logger.warning("Test warning")
        logger.error("Test error")
        logger.success("Test success")
        
        logs = logger.get_logs()
        self.assertEqual(len(logs), 4)
        self.assertIn("INFO", logs[0])
        self.assertIn("WARN", logs[1])
        self.assertIn("ERROR", logs[2])
        self.assertIn("SUCCESS", logs[3])
        
    def test_experiment_logging(self):
        """Test experiment-specific logging."""
        logger = ExperimentLogger(verbose=False)
        
        logger.experiment_start("test_config", 10)
        logger.run_start(1, 10)
        logger.run_complete(1, 100, "victory")
        logger.experiment_complete("test_config", 5.0)
        
        logs = logger.get_logs()
        self.assertTrue(any("test_config" in log for log in logs))
        

class TestHeadlessSimulation(unittest.TestCase):
    """Test HeadlessSimulation class."""
    
    def test_create_simulation(self):
        """Test creating headless simulation."""
        config = ExperimentConfig(name="test", num_runs=1, max_turns=50)
        metrics = MetricsCollector()
        metrics.start_simulation(1, "test")
        
        sim = HeadlessSimulation(config, metrics)
        
        self.assertIsNotNone(sim.dek)
        self.assertIsNotNone(sim.thia)
        self.assertIsNotNone(sim.boss)
        self.assertEqual(len(sim.agents), 5 + config.wildlife_count)
        
    def test_run_simulation(self):
        """Test running a simulation."""
        config = ExperimentConfig(name="test", num_runs=1, max_turns=20)
        metrics = MetricsCollector()
        metrics.start_simulation(1, "test")
        
        sim = HeadlessSimulation(config, metrics)
        outcome = sim.run()
        
        self.assertIn(outcome, ['victory', 'defeat', 'timeout'])
        self.assertGreater(sim.turn, 0)


class TestExperimentRunner(unittest.TestCase):
    """Test ExperimentRunner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.runner = ExperimentRunner(self.temp_dir)
        
    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_add_config(self):
        """Test adding configurations."""
        config = ExperimentConfig(name="test", num_runs=5)
        self.runner.add_config(config)
        
        self.assertEqual(len(self.runner.configs), 1)
        
    def test_run_small_experiment(self):
        """Test running a small experiment."""
        config = ExperimentConfig(
            name="quick_test",
            num_runs=2,
            max_turns=10
        )
        
        self.runner.add_config(config)
        results = self.runner.run_all_experiments()
        
        self.assertIn("quick_test", results)
        self.assertEqual(len(results["quick_test"]), 2)
        
    def test_save_results(self):
        """Test saving experiment results."""
        config = ExperimentConfig(name="test", num_runs=2, max_turns=10)
        self.runner.add_config(config)
        self.runner.run_all_experiments()
        
        saved_files = self.runner.save_results()
        
        self.assertGreater(len(saved_files), 0)
        
    def test_get_summary_stats(self):
        """Test getting summary statistics."""
        config = ExperimentConfig(name="test", num_runs=3, max_turns=10)
        self.runner.add_config(config)
        self.runner.run_all_experiments()
        
        stats = self.runner.get_summary_stats()
        
        self.assertIn("test", stats)
        self.assertEqual(stats["test"]["total_runs"], 3)
        self.assertIn("win_rate", stats["test"])


class TestSurvivalCurve(unittest.TestCase):
    """Test survival curve calculation."""
    
    def test_calculate_survival_curve(self):
        """Test survival curve calculation."""
        metrics = [
            AgentMetrics("a1", "p", survival_time=50, is_alive=False),
            AgentMetrics("a2", "p", survival_time=100, is_alive=False),
            AgentMetrics("a3", "p", survival_time=150, is_alive=True),
        ]
        
        curve = calculate_survival_curve(metrics)
        
        self.assertIsInstance(curve, list)
        self.assertGreater(len(curve), 0)
        
        # First point should have all alive
        self.assertEqual(curve[0][0], 0)  # Step 0
        
    def test_empty_metrics(self):
        """Test with empty metrics list."""
        curve = calculate_survival_curve([])
        self.assertEqual(curve, [])


class TestHonourProgression(unittest.TestCase):
    """Test honour progression calculation."""
    
    def test_calculate_honour_progression(self):
        """Test honour progression calculation."""
        histories = {
            'dek': [100, 120, 150, 180],
            'brother': [80, 90, 100, 110]
        }
        
        result = calculate_honour_progression(histories)
        
        self.assertIn('dek', result)
        self.assertIn('brother', result)
        self.assertEqual(len(result['dek']), 4)
        self.assertEqual(result['dek'][0], (0, 100))
        self.assertEqual(result['dek'][-1], (3, 180))


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete experiment pipeline."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_full_experiment_pipeline(self):
        """Test complete experiment pipeline from config to results."""
        # Create runner
        runner = ExperimentRunner(self.temp_dir)
        
        # Add small configs
        runner.add_config(ExperimentConfig(
            name="pipeline_test",
            num_runs=3,
            max_turns=15
        ))
        
        # Run experiments
        results = runner.run_all_experiments()
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results["pipeline_test"]), 3)
        
        # Save results
        saved = runner.save_results()
        self.assertGreater(len(saved), 0)
        
        # Verify files exist
        csv_files = [f for f in saved.values() if f.endswith('.csv')]
        self.assertGreater(len(csv_files), 0)
        
        for csv_file in csv_files:
            self.assertTrue(os.path.exists(csv_file))
            
    def test_multi_config_experiment(self):
        """Test running multiple configurations."""
        runner = ExperimentRunner(self.temp_dir)
        
        # Add multiple configs
        runner.add_config(ExperimentConfig(name="easy", num_runs=2, max_turns=10))
        runner.add_config(ExperimentConfig(name="hard", num_runs=2, max_turns=10))
        
        results = runner.run_all_experiments()
        
        self.assertEqual(len(results), 2)
        self.assertIn("easy", results)
        self.assertIn("hard", results)
        
        # Summary should have both
        stats = runner.get_summary_stats()
        self.assertIn("easy", stats)
        self.assertIn("hard", stats)


# Run tests
if __name__ == '__main__':
    unittest.main(verbosity=2)
