"""
Experiment Runner Module for Predator: Badlands
================================================
This module provides automated simulation running for experiments.
Runs multiple simulations per configuration, collects metrics, and manages results.

Author: Predator Badlands Team
Phase: 10 - Experiments & Data Collection
"""

import sys
import os
import time
import random
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from grid import Grid
from predator import Dek, PredatorFather, PredatorBrother
from synthetic import Thia
from creatures import WildlifeAgent, BossAdversary
from actions import ActionType
from event_logger import EventLogger
from metrics import MetricsCollector, SimulationMetrics, AgentMetrics
from data_collector import DataCollector, ExperimentLogger


class DifficultyLevel(Enum):
    """Difficulty levels for experiments."""
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    EXTREME = "extreme"


@dataclass
class ExperimentConfig:
    """
    Configuration for a single experiment setup.
    
    Attributes:
        name: Unique name for this configuration
        difficulty: Difficulty level
        grid_size: Size of the grid (width, height)
        max_turns: Maximum simulation turns
        boss_health_multiplier: Boss health scaling
        wildlife_count: Number of wildlife agents
        resource_count: Number of resources to spawn
        num_runs: Number of simulation runs to perform
        random_seed: Optional seed for reproducibility
    """
    name: str
    difficulty: DifficultyLevel = DifficultyLevel.NORMAL
    grid_size: tuple = (30, 30)
    max_turns: int = 200
    boss_health_multiplier: float = 1.0
    wildlife_count: int = 4
    resource_count: int = 15
    num_runs: int = 20
    random_seed: Optional[int] = None
    
    # Advanced settings
    dek_start_honour: float = 100.0
    boss_damage_multiplier: float = 1.0
    enable_coordination: bool = True
    enable_learning: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'name': self.name,
            'difficulty': self.difficulty.value,
            'grid_size': self.grid_size,
            'max_turns': self.max_turns,
            'boss_health_multiplier': self.boss_health_multiplier,
            'wildlife_count': self.wildlife_count,
            'resource_count': self.resource_count,
            'num_runs': self.num_runs,
            'random_seed': self.random_seed,
            'dek_start_honour': self.dek_start_honour,
            'boss_damage_multiplier': self.boss_damage_multiplier,
            'enable_coordination': self.enable_coordination,
            'enable_learning': self.enable_learning
        }


# Pre-defined experiment configurations
EXPERIMENT_CONFIGS = {
    'easy': ExperimentConfig(
        name='easy',
        difficulty=DifficultyLevel.EASY,
        boss_health_multiplier=0.7,
        wildlife_count=2,
        resource_count=20,
        num_runs=20
    ),
    'normal': ExperimentConfig(
        name='normal',
        difficulty=DifficultyLevel.NORMAL,
        boss_health_multiplier=1.0,
        wildlife_count=4,
        resource_count=15,
        num_runs=20
    ),
    'hard': ExperimentConfig(
        name='hard',
        difficulty=DifficultyLevel.HARD,
        boss_health_multiplier=1.5,
        wildlife_count=6,
        resource_count=10,
        num_runs=20
    ),
    'extreme': ExperimentConfig(
        name='extreme',
        difficulty=DifficultyLevel.EXTREME,
        boss_health_multiplier=2.0,
        wildlife_count=8,
        resource_count=5,
        boss_damage_multiplier=1.5,
        num_runs=20
    ),
    'no_coordination': ExperimentConfig(
        name='no_coordination',
        difficulty=DifficultyLevel.NORMAL,
        enable_coordination=False,
        num_runs=20
    ),
    'no_learning': ExperimentConfig(
        name='no_learning',
        difficulty=DifficultyLevel.NORMAL,
        enable_learning=False,
        num_runs=20
    ),
    'baseline': ExperimentConfig(
        name='baseline',
        difficulty=DifficultyLevel.NORMAL,
        enable_coordination=False,
        enable_learning=False,
        num_runs=20
    )
}


class HeadlessSimulation:
    """
    Headless simulation runner for experiments (no GUI).
    
    This class runs simulations without visualization for fast
    automated data collection.
    """
    
    def __init__(self, config: ExperimentConfig, metrics_collector: MetricsCollector):
        """
        Initialize headless simulation.
        
        Args:
            config: Experiment configuration
            metrics_collector: Metrics collector instance
        """
        self.config = config
        self.metrics = metrics_collector
        
        # Initialize grid
        self.grid = Grid(config.grid_size[0], config.grid_size[1])
        self.grid.generate_terrain()
        
        # Initialize agents
        self.agents: List[Any] = []
        self.dek: Optional[Dek] = None
        self.thia: Optional[Thia] = None
        self.father: Optional[PredatorFather] = None
        self.brother: Optional[PredatorBrother] = None
        self.boss: Optional[BossAdversary] = None
        self.wildlife: List[WildlifeAgent] = []
        
        # Simulation state
        self.turn = 0
        self.outcome = "running"
        self.reason = ""
        self.logger = EventLogger()
        
        self._setup_agents()
        
    def _setup_agents(self) -> None:
        """Initialize and place all agents."""
        # Main agents
        self.dek = Dek(12, 12)
        self.dek.honour = self.config.dek_start_honour
        
        self.thia = Thia(13, 12)
        self.father = PredatorFather("Elder Kaail", 6, 6)
        self.brother = PredatorBrother("Cetanu", 18, 12)
        
        # Boss with health multiplier
        self.boss = BossAdversary("Ultimate Adversary", 22, 22)
        base_health = self.boss.max_health
        self.boss.max_health = int(base_health * self.config.boss_health_multiplier)
        self.boss.health = self.boss.max_health
        
        self.agents = [self.dek, self.thia, self.father, self.brother, self.boss]
        
        # Wildlife agents
        wildlife_positions = [
            (8, 8), (20, 8), (8, 18), (20, 18), (14, 16),
            (10, 20), (20, 10), (5, 15), (25, 15), (15, 5)
        ]
        
        for i in range(min(self.config.wildlife_count, len(wildlife_positions))):
            x, y = wildlife_positions[i]
            wildlife = WildlifeAgent(f"Wildlife_{i+1}", "predator", x, y)
            self.wildlife.append(wildlife)
            self.agents.append(wildlife)
            
        # Place all agents on grid
        for agent in self.agents:
            agent.set_grid(self.grid)
            self.grid.place_agent(agent, agent.x, agent.y)
            
        # Register agents with metrics
        self._register_agents_metrics()
        
    def _register_agents_metrics(self) -> None:
        """Register all agents with the metrics collector."""
        agent_types = {
            'Dek': 'predator_hero',
            'Thia': 'synthetic_ally',
            'PredatorFather': 'predator_elder',
            'PredatorBrother': 'predator_warrior',
            'BossAdversary': 'boss',
            'WildlifeAgent': 'wildlife'
        }
        
        for agent in self.agents:
            agent_id = getattr(agent, 'name', agent.__class__.__name__)
            agent_type = agent_types.get(agent.__class__.__name__, 'unknown')
            self.metrics.register_agent(agent_id, agent_type)
            
    def run(self) -> str:
        """
        Run the simulation to completion.
        
        Returns:
            Outcome string ('victory', 'defeat', 'timeout')
        """
        while self.turn < self.config.max_turns and self.outcome == "running":
            self._run_turn()
            self.turn += 1
            self.metrics.record_step(self.turn)
            
            # Record honour for all predator agents
            self._record_metrics()
            
            # Check win/lose conditions
            self._check_outcome()
            
        # Finalize outcome
        if self.outcome == "running":
            self.outcome = "timeout"
            self.reason = "Maximum turns reached"
            
        # Record final state
        self._record_final_metrics()
        
        return self.outcome
        
    def _run_turn(self) -> None:
        """Execute a single simulation turn."""
        # Process each agent
        for agent in self.agents:
            if not agent.is_alive:
                continue
                
            # Simple AI for agents
            self._process_agent_turn(agent)
            
    def _process_agent_turn(self, agent: Any) -> None:
        """Process a single agent's turn."""
        # Get nearby targets
        targets = self._get_nearby_targets(agent)
        
        if not targets:
            # Random movement
            self._random_move(agent)
            return
            
        # Attack nearest target
        target = min(targets, key=lambda t: self._distance(agent, t))
        
        if self._distance(agent, target) <= 1.5:
            # In range - attack
            self._process_combat(agent, target)
        else:
            # Move towards target
            self._move_towards(agent, target)
            
    def _get_nearby_targets(self, agent: Any) -> List[Any]:
        """Get valid targets for an agent."""
        targets = []
        agent_class = agent.__class__.__name__
        
        for other in self.agents:
            if other == agent or not other.is_alive:
                continue
                
            # Define targeting logic
            if agent_class in ['Dek', 'Thia', 'PredatorFather', 'PredatorBrother']:
                # Team targets boss and wildlife
                if other.__class__.__name__ in ['BossAdversary', 'WildlifeAgent']:
                    targets.append(other)
            elif agent_class == 'BossAdversary':
                # Boss targets heroes
                if other.__class__.__name__ in ['Dek', 'Thia', 'PredatorFather', 'PredatorBrother']:
                    targets.append(other)
            elif agent_class == 'WildlifeAgent':
                # Wildlife targets randomly
                if other.__class__.__name__ in ['Dek', 'Thia']:
                    targets.append(other)
                    
        return targets
        
    def _distance(self, a: Any, b: Any) -> float:
        """Calculate distance between two agents."""
        return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5
        
    def _random_move(self, agent: Any) -> None:
        """Move agent in a random direction."""
        dx = random.choice([-1, 0, 1])
        dy = random.choice([-1, 0, 1])
        
        new_x = max(0, min(self.config.grid_size[0] - 1, agent.x + dx))
        new_y = max(0, min(self.config.grid_size[1] - 1, agent.y + dy))
        
        # Check if cell is walkable (not occupied)
        cell = self.grid.get_cell(new_x, new_y)
        if not cell.is_occupied:
            self.grid.move_agent(agent, new_x, new_y)
            agent.x, agent.y = new_x, new_y
            
            # Record movement
            agent_id = getattr(agent, 'name', agent.__class__.__name__)
            self.metrics.record_movement(agent_id, (dx**2 + dy**2)**0.5)
            
    def _move_towards(self, agent: Any, target: Any) -> None:
        """Move agent towards target."""
        dx = 0 if target.x == agent.x else (1 if target.x > agent.x else -1)
        dy = 0 if target.y == agent.y else (1 if target.y > agent.y else -1)
        
        new_x = max(0, min(self.config.grid_size[0] - 1, agent.x + dx))
        new_y = max(0, min(self.config.grid_size[1] - 1, agent.y + dy))
        
        # Check if cell is walkable (not occupied)
        cell = self.grid.get_cell(new_x, new_y)
        if not cell.is_occupied:
            self.grid.move_agent(agent, new_x, new_y)
            agent.x, agent.y = new_x, new_y
            
            agent_id = getattr(agent, 'name', agent.__class__.__name__)
            self.metrics.record_movement(agent_id, (dx**2 + dy**2)**0.5)
            
    def _process_combat(self, attacker: Any, defender: Any) -> None:
        """Process combat between two agents."""
        attacker_id = getattr(attacker, 'name', attacker.__class__.__name__)
        defender_id = getattr(defender, 'name', defender.__class__.__name__)
        
        # Calculate damage
        base_damage = getattr(attacker, 'damage', 10)
        
        # Apply damage multiplier for boss
        if attacker.__class__.__name__ == 'BossAdversary':
            base_damage = int(base_damage * self.config.boss_damage_multiplier)
            
        # Apply damage
        defender.take_damage(base_damage)
        
        # Determine winner
        won = not defender.is_alive
        
        # Record combat
        self.metrics.record_combat(attacker_id, defender_id, won)
        
        # Update honour for predator kills
        if won and attacker.__class__.__name__ in ['Dek', 'PredatorFather', 'PredatorBrother']:
            if hasattr(attacker, 'honour'):
                honour_gain = 20 if defender.__class__.__name__ == 'BossAdversary' else 5
                attacker.honour += honour_gain
                
        # Record death if defender died
        if not defender.is_alive:
            self.metrics.record_death(defender_id)
            
    def _record_metrics(self) -> None:
        """Record per-turn metrics."""
        # Record honour for all predator agents
        for agent in self.agents:
            if not agent.is_alive:
                continue
                
            agent_id = getattr(agent, 'name', agent.__class__.__name__)
            
            if hasattr(agent, 'honour'):
                self.metrics.record_honour(agent_id, agent.honour)
                
    def _record_final_metrics(self) -> None:
        """Record final simulation metrics."""
        # Set winner
        if self.outcome == 'victory':
            self.metrics.set_winner('team')
            self.metrics.set_boss_defeated(True)
        elif self.outcome == 'defeat':
            self.metrics.set_winner('boss')
            
    def _check_outcome(self) -> None:
        """Check win/lose conditions."""
        # Victory: Boss defeated
        if not self.boss.is_alive:
            self.outcome = 'victory'
            self.reason = 'Boss defeated'
            return
            
        # Defeat: Dek dies
        if not self.dek.is_alive:
            self.outcome = 'defeat'
            self.reason = 'Dek died'
            return
            
        # Defeat: All team dead
        team_alive = any(
            a.is_alive for a in [self.dek, self.thia, self.father, self.brother]
        )
        if not team_alive:
            self.outcome = 'defeat'
            self.reason = 'Team eliminated'


class ExperimentRunner:
    """
    Main experiment runner for automated simulations.
    
    Runs multiple configurations with specified number of runs each,
    collecting metrics and generating reports.
    
    Example:
        runner = ExperimentRunner(output_dir="data/experiments")
        runner.add_config(EXPERIMENT_CONFIGS['normal'])
        runner.add_config(EXPERIMENT_CONFIGS['hard'])
        results = runner.run_all_experiments()
    """
    
    def __init__(self, output_dir: str = "data/experiments"):
        """
        Initialize the experiment runner.
        
        Args:
            output_dir: Directory for saving experiment data
        """
        self.output_dir = output_dir
        self.configs: List[ExperimentConfig] = []
        self.results: Dict[str, List[SimulationMetrics]] = {}
        
        self.data_collector = DataCollector(output_dir)
        self.logger = ExperimentLogger(
            log_file=os.path.join(output_dir, "experiment.log"),
            verbose=True
        )
        
        # Progress callback
        self.progress_callback: Optional[Callable[[int, int, str], None]] = None
        
    def add_config(self, config: ExperimentConfig) -> None:
        """
        Add an experiment configuration.
        
        Args:
            config: Configuration to add
        """
        self.configs.append(config)
        self.logger.info(f"Added config: {config.name} ({config.num_runs} runs)")
        
    def add_configs(self, configs: List[ExperimentConfig]) -> None:
        """Add multiple configurations."""
        for config in configs:
            self.add_config(config)
            
    def set_progress_callback(self, callback: Callable[[int, int, str], None]) -> None:
        """Set callback for progress updates: (current, total, message)."""
        self.progress_callback = callback
        
    def run_experiment(self, config: ExperimentConfig) -> List[SimulationMetrics]:
        """
        Run a single experiment configuration.
        
        Args:
            config: Configuration to run
            
        Returns:
            List of SimulationMetrics for all runs
        """
        self.logger.experiment_start(config.name, config.num_runs)
        start_time = time.time()
        
        metrics_collector = MetricsCollector()
        results = []
        
        for run_id in range(1, config.num_runs + 1):
            # Set random seed if specified
            if config.random_seed is not None:
                random.seed(config.random_seed + run_id)
                
            self.logger.run_start(run_id, config.num_runs)
            
            # Start metrics collection
            metrics_collector.start_simulation(run_id, config.name)
            
            # Run headless simulation
            sim = HeadlessSimulation(config, metrics_collector)
            outcome = sim.run()
            
            # End metrics collection
            run_metrics = metrics_collector.end_simulation()
            results.append(run_metrics)
            
            self.logger.run_complete(run_id, run_metrics.total_steps, outcome)
            
            # Progress callback
            if self.progress_callback:
                total_runs = sum(c.num_runs for c in self.configs)
                current = sum(
                    len(self.results.get(c.name, [])) 
                    for c in self.configs 
                    if c.name != config.name
                ) + run_id
                self.progress_callback(current, total_runs, f"{config.name} run {run_id}")
                
        duration = time.time() - start_time
        self.logger.experiment_complete(config.name, duration)
        
        return results
        
    def run_all_experiments(self) -> Dict[str, List[SimulationMetrics]]:
        """
        Run all configured experiments.
        
        Returns:
            Dictionary mapping config names to their results
        """
        if not self.configs:
            self.logger.warning("No configurations to run")
            return {}
            
        self.logger.info(f"Starting {len(self.configs)} experiments...")
        total_start = time.time()
        
        for config in self.configs:
            results = self.run_experiment(config)
            self.results[config.name] = results
            
        total_duration = time.time() - total_start
        total_runs = sum(len(r) for r in self.results.values())
        
        self.logger.success(f"All experiments complete: {total_runs} runs in {total_duration:.1f}s")
        
        return self.results
        
    def save_results(self) -> Dict[str, str]:
        """
        Save all results to CSV and JSON files.
        
        Returns:
            Dictionary of saved file paths
        """
        saved_files = {}
        
        # Flatten all runs
        all_runs = []
        for config_results in self.results.values():
            all_runs.extend(config_results)
            
        if not all_runs:
            self.logger.warning("No results to save")
            return saved_files
            
        # Save simulation results CSV
        sim_csv = self.data_collector.save_simulation_results_csv(all_runs)
        if sim_csv:
            saved_files['simulation_results'] = sim_csv
            
        # Save agent metrics CSV
        agent_csv = self.data_collector.save_all_agent_metrics_csv(all_runs)
        if agent_csv:
            saved_files['agent_metrics'] = agent_csv
            
        # Save honour progression CSV
        honour_csv = self.data_collector.save_honour_progression_csv(all_runs)
        if honour_csv:
            saved_files['honour_progression'] = honour_csv
            
        # Calculate and save summary stats by config
        stats_by_config = {}
        for config_name, results in self.results.items():
            if not results:
                continue
                
            wins = sum(1 for r in results if r.boss_defeated)
            stats_by_config[config_name] = {
                'total_runs': len(results),
                'wins': wins,
                'win_rate': wins / len(results) if results else 0,
                'avg_steps': sum(r.total_steps for r in results) / len(results),
                'avg_survival_rate': sum(r.team_survival_rate for r in results) / len(results),
                'avg_combats': sum(r.total_combats for r in results) / len(results),
                'avg_duration': sum(r.duration_seconds for r in results) / len(results)
            }
            
        summary_csv = self.data_collector.save_summary_stats_csv(stats_by_config)
        if summary_csv:
            saved_files['summary_stats'] = summary_csv
            
        # Save complete experiment JSON
        all_configs = {c.name: c.to_dict() for c in self.configs}
        json_path = self.data_collector.save_experiment_json(all_runs, all_configs)
        if json_path:
            saved_files['experiment_json'] = json_path
            
        self.logger.success(f"Saved {len(saved_files)} result files")
        
        return saved_files
        
    def get_summary_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get summary statistics for all experiments.
        
        Returns:
            Dictionary mapping config names to their summary stats
        """
        summary = {}
        
        for config_name, results in self.results.items():
            if not results:
                continue
                
            wins = sum(1 for r in results if r.boss_defeated)
            total_steps = [r.total_steps for r in results]
            survival_rates = [r.team_survival_rate for r in results]
            
            summary[config_name] = {
                'total_runs': len(results),
                'wins': wins,
                'losses': len(results) - wins,
                'win_rate': round(wins / len(results) * 100, 1),
                'avg_steps': round(sum(total_steps) / len(total_steps), 1),
                'min_steps': min(total_steps),
                'max_steps': max(total_steps),
                'avg_survival_rate': round(sum(survival_rates) / len(survival_rates) * 100, 1),
                'avg_duration_sec': round(
                    sum(r.duration_seconds for r in results) / len(results), 3
                )
            }
            
        return summary
        
    def print_summary(self) -> None:
        """Print a formatted summary of all experiments."""
        stats = self.get_summary_stats()
        
        if not stats:
            print("No experiment results available.")
            return
            
        print("\n" + "=" * 80)
        print("EXPERIMENT SUMMARY")
        print("=" * 80)
        
        for config_name, s in stats.items():
            print(f"\n{config_name.upper()}")
            print("-" * 40)
            print(f"  Total Runs:        {s['total_runs']}")
            print(f"  Wins/Losses:       {s['wins']}/{s['losses']}")
            print(f"  Win Rate:          {s['win_rate']}%")
            print(f"  Avg Steps:         {s['avg_steps']} (min: {s['min_steps']}, max: {s['max_steps']})")
            print(f"  Avg Survival Rate: {s['avg_survival_rate']}%")
            print(f"  Avg Duration:      {s['avg_duration_sec']}s")
            
        print("\n" + "=" * 80)


def run_quick_experiment(num_runs: int = 5) -> Dict[str, List[SimulationMetrics]]:
    """
    Run a quick experiment with default configuration.
    
    Args:
        num_runs: Number of runs to perform
        
    Returns:
        Dictionary of results
    """
    config = ExperimentConfig(
        name='quick_test',
        num_runs=num_runs,
        max_turns=100
    )
    
    runner = ExperimentRunner()
    runner.add_config(config)
    return runner.run_all_experiments()


if __name__ == "__main__":
    # Quick test
    print("Running quick experiment test...")
    results = run_quick_experiment(3)
    
    for name, runs in results.items():
        print(f"\n{name}: {len(runs)} runs")
        for run in runs:
            print(f"  Run {run.run_id}: {run.total_steps} steps, winner={run.winner}")
