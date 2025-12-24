"""
Metrics Collection Module for Predator: Badlands
=================================================
This module provides comprehensive metrics tracking for multi-agent simulations.
Collects survival time, honour progression, win rate, resource usage, and more.

Author: Predator Badlands Team
Phase: 10 - Experiments & Data Collection
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import time
import statistics


class MetricType(Enum):
    """Types of metrics that can be collected."""
    SURVIVAL_TIME = "survival_time"
    HONOUR_PROGRESSION = "honour_progression"
    WIN_RATE = "win_rate"
    RESOURCE_USAGE = "resource_usage"
    COMBAT_STATS = "combat_stats"
    MOVEMENT_STATS = "movement_stats"
    COORDINATION_STATS = "coordination_stats"


@dataclass
class AgentMetrics:
    """
    Metrics for a single agent during simulation.
    
    Attributes:
        agent_id: Unique identifier for the agent
        agent_type: Type of agent (predator, prey, etc.)
        survival_time: How long the agent survived (in steps)
        honour_history: List of honour values over time
        kills: Number of kills made
        deaths: Number of deaths
        resources_collected: Total resources gathered
        resources_consumed: Total resources consumed
        distance_traveled: Total distance moved
        combats_initiated: Number of combats started
        combats_won: Number of combats won
        coordinated_actions: Number of coordination events
    """
    agent_id: str
    agent_type: str
    survival_time: int = 0
    honour_history: List[float] = field(default_factory=list)
    kills: int = 0
    deaths: int = 0
    resources_collected: int = 0
    resources_consumed: int = 0
    distance_traveled: float = 0.0
    combats_initiated: int = 0
    combats_won: int = 0
    coordinated_actions: int = 0
    final_honour: float = 0.0
    is_alive: bool = True
    
    def get_win_rate(self) -> float:
        """Calculate combat win rate."""
        if self.combats_initiated == 0:
            return 0.0
        return self.combats_won / self.combats_initiated
    
    def get_honour_growth(self) -> float:
        """Calculate total honour growth."""
        if len(self.honour_history) < 2:
            return 0.0
        return self.honour_history[-1] - self.honour_history[0]
    
    def get_average_honour(self) -> float:
        """Calculate average honour over simulation."""
        if not self.honour_history:
            return 0.0
        return statistics.mean(self.honour_history)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for CSV export."""
        return {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type,
            'survival_time': self.survival_time,
            'final_honour': self.final_honour,
            'honour_growth': self.get_honour_growth(),
            'average_honour': self.get_average_honour(),
            'kills': self.kills,
            'deaths': self.deaths,
            'win_rate': self.get_win_rate(),
            'resources_collected': self.resources_collected,
            'resources_consumed': self.resources_consumed,
            'distance_traveled': self.distance_traveled,
            'combats_initiated': self.combats_initiated,
            'combats_won': self.combats_won,
            'coordinated_actions': self.coordinated_actions,
            'is_alive': self.is_alive
        }


@dataclass
class SimulationMetrics:
    """
    Aggregate metrics for an entire simulation run.
    
    Attributes:
        run_id: Unique identifier for this simulation run
        config_name: Name of the configuration used
        total_steps: Total simulation steps completed
        duration_seconds: Real-time duration of simulation
        agent_metrics: Dictionary of agent metrics by agent_id
        winner: The winning agent/team (if any)
        boss_defeated: Whether the boss was defeated
        team_survival_rate: Percentage of team that survived
    """
    run_id: int
    config_name: str
    total_steps: int = 0
    duration_seconds: float = 0.0
    agent_metrics: Dict[str, AgentMetrics] = field(default_factory=dict)
    winner: Optional[str] = None
    boss_defeated: bool = False
    team_survival_rate: float = 0.0
    total_combats: int = 0
    total_resources_spawned: int = 0
    total_resources_collected: int = 0
    honour_distribution: List[float] = field(default_factory=list)
    
    def get_average_survival_time(self) -> float:
        """Calculate average survival time across all agents."""
        if not self.agent_metrics:
            return 0.0
        times = [m.survival_time for m in self.agent_metrics.values()]
        return statistics.mean(times)
    
    def get_total_kills(self) -> int:
        """Get total kills across all agents."""
        return sum(m.kills for m in self.agent_metrics.values())
    
    def get_resource_efficiency(self) -> float:
        """Calculate resource collection efficiency."""
        if self.total_resources_spawned == 0:
            return 0.0
        return self.total_resources_collected / self.total_resources_spawned
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert simulation metrics to dictionary."""
        return {
            'run_id': self.run_id,
            'config_name': self.config_name,
            'total_steps': self.total_steps,
            'duration_seconds': round(self.duration_seconds, 3),
            'winner': self.winner,
            'boss_defeated': self.boss_defeated,
            'team_survival_rate': round(self.team_survival_rate, 3),
            'average_survival_time': round(self.get_average_survival_time(), 2),
            'total_combats': self.total_combats,
            'total_kills': self.get_total_kills(),
            'resource_efficiency': round(self.get_resource_efficiency(), 3),
            'num_agents': len(self.agent_metrics)
        }


class MetricsCollector:
    """
    Main metrics collection class for tracking simulation data.
    
    This class is responsible for:
    - Recording per-step agent metrics
    - Tracking cumulative statistics
    - Aggregating data for analysis
    - Providing data for visualization
    
    Example:
        collector = MetricsCollector()
        collector.start_simulation(run_id=1, config_name="default")
        collector.register_agent("dek", "predator")
        collector.record_honour("dek", 100.0, step=0)
        collector.record_combat("dek", "wildlife_1", won=True)
        metrics = collector.end_simulation()
    """
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.current_run: Optional[SimulationMetrics] = None
        self.all_runs: List[SimulationMetrics] = []
        self._start_time: float = 0.0
        self._current_step: int = 0
        
    def start_simulation(self, run_id: int, config_name: str) -> None:
        """
        Start tracking a new simulation run.
        
        Args:
            run_id: Unique identifier for this run
            config_name: Name of the configuration being used
        """
        self.current_run = SimulationMetrics(
            run_id=run_id,
            config_name=config_name
        )
        self._start_time = time.time()
        self._current_step = 0
        
    def register_agent(self, agent_id: str, agent_type: str) -> None:
        """
        Register an agent for metrics tracking.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_type: Type of the agent (predator, prey, boss, etc.)
        """
        if self.current_run is None:
            return
            
        self.current_run.agent_metrics[agent_id] = AgentMetrics(
            agent_id=agent_id,
            agent_type=agent_type
        )
        
    def record_step(self, step: int) -> None:
        """
        Record the current simulation step.
        
        Args:
            step: Current step number
        """
        self._current_step = step
        if self.current_run:
            self.current_run.total_steps = step
            
    def record_honour(self, agent_id: str, honour: float, step: int = None) -> None:
        """
        Record an agent's honour value.
        
        Args:
            agent_id: The agent's identifier
            honour: Current honour value
            step: Optional step number (uses current step if not provided)
        """
        if self.current_run is None:
            return
            
        if agent_id not in self.current_run.agent_metrics:
            return
            
        metrics = self.current_run.agent_metrics[agent_id]
        metrics.honour_history.append(honour)
        metrics.final_honour = honour
        
    def record_combat(self, agent_id: str, opponent_id: str, won: bool) -> None:
        """
        Record a combat event.
        
        Args:
            agent_id: The initiating agent
            opponent_id: The opponent agent
            won: Whether the agent won the combat
        """
        if self.current_run is None:
            return
            
        self.current_run.total_combats += 1
        
        if agent_id in self.current_run.agent_metrics:
            metrics = self.current_run.agent_metrics[agent_id]
            metrics.combats_initiated += 1
            if won:
                metrics.combats_won += 1
                metrics.kills += 1
                
        if opponent_id in self.current_run.agent_metrics and not won:
            opponent_metrics = self.current_run.agent_metrics[opponent_id]
            opponent_metrics.combats_won += 1
            opponent_metrics.kills += 1
            
    def record_death(self, agent_id: str) -> None:
        """
        Record an agent's death.
        
        Args:
            agent_id: The agent that died
        """
        if self.current_run is None:
            return
            
        if agent_id in self.current_run.agent_metrics:
            metrics = self.current_run.agent_metrics[agent_id]
            metrics.deaths += 1
            metrics.is_alive = False
            metrics.survival_time = self._current_step
            
    def record_resource_collected(self, agent_id: str, amount: int = 1) -> None:
        """
        Record resource collection.
        
        Args:
            agent_id: The agent collecting resources
            amount: Amount of resources collected
        """
        if self.current_run is None:
            return
            
        self.current_run.total_resources_collected += amount
        
        if agent_id in self.current_run.agent_metrics:
            self.current_run.agent_metrics[agent_id].resources_collected += amount
            
    def record_resource_consumed(self, agent_id: str, amount: int = 1) -> None:
        """
        Record resource consumption.
        
        Args:
            agent_id: The agent consuming resources
            amount: Amount consumed
        """
        if self.current_run is None:
            return
            
        if agent_id in self.current_run.agent_metrics:
            self.current_run.agent_metrics[agent_id].resources_consumed += amount
            
    def record_movement(self, agent_id: str, distance: float) -> None:
        """
        Record agent movement.
        
        Args:
            agent_id: The moving agent
            distance: Distance traveled
        """
        if self.current_run is None:
            return
            
        if agent_id in self.current_run.agent_metrics:
            self.current_run.agent_metrics[agent_id].distance_traveled += distance
            
    def record_coordination(self, agent_id: str) -> None:
        """
        Record a coordination event.
        
        Args:
            agent_id: The coordinating agent
        """
        if self.current_run is None:
            return
            
        if agent_id in self.current_run.agent_metrics:
            self.current_run.agent_metrics[agent_id].coordinated_actions += 1
            
    def record_resource_spawn(self, amount: int = 1) -> None:
        """
        Record resources spawning in the world.
        
        Args:
            amount: Number of resources spawned
        """
        if self.current_run:
            self.current_run.total_resources_spawned += amount
            
    def set_winner(self, winner: str) -> None:
        """
        Set the simulation winner.
        
        Args:
            winner: The winning agent/team
        """
        if self.current_run:
            self.current_run.winner = winner
            
    def set_boss_defeated(self, defeated: bool = True) -> None:
        """
        Set whether the boss was defeated.
        
        Args:
            defeated: True if boss was defeated
        """
        if self.current_run:
            self.current_run.boss_defeated = defeated
            
    def end_simulation(self) -> SimulationMetrics:
        """
        End the current simulation and finalize metrics.
        
        Returns:
            The completed SimulationMetrics for this run
        """
        if self.current_run is None:
            raise ValueError("No simulation is currently running")
            
        # Calculate duration
        self.current_run.duration_seconds = time.time() - self._start_time
        
        # Calculate survival rate
        alive_count = sum(
            1 for m in self.current_run.agent_metrics.values() 
            if m.is_alive
        )
        total_count = len(self.current_run.agent_metrics)
        if total_count > 0:
            self.current_run.team_survival_rate = alive_count / total_count
            
        # Update survival time for surviving agents
        for metrics in self.current_run.agent_metrics.values():
            if metrics.is_alive:
                metrics.survival_time = self._current_step
                
        # Collect honour distribution
        self.current_run.honour_distribution = [
            m.final_honour for m in self.current_run.agent_metrics.values()
        ]
        
        # Store and return
        completed_run = self.current_run
        self.all_runs.append(completed_run)
        self.current_run = None
        
        return completed_run
        
    def get_all_runs(self) -> List[SimulationMetrics]:
        """Get all completed simulation runs."""
        return self.all_runs
        
    def get_aggregate_stats(self) -> Dict[str, Any]:
        """
        Calculate aggregate statistics across all runs.
        
        Returns:
            Dictionary containing aggregate statistics
        """
        if not self.all_runs:
            return {}
            
        win_count = sum(1 for r in self.all_runs if r.boss_defeated)
        
        return {
            'total_runs': len(self.all_runs),
            'average_steps': statistics.mean(r.total_steps for r in self.all_runs),
            'average_duration': statistics.mean(r.duration_seconds for r in self.all_runs),
            'boss_defeat_rate': win_count / len(self.all_runs),
            'average_survival_rate': statistics.mean(r.team_survival_rate for r in self.all_runs),
            'average_combats': statistics.mean(r.total_combats for r in self.all_runs),
            'average_resource_efficiency': statistics.mean(r.get_resource_efficiency() for r in self.all_runs)
        }
        
    def reset(self) -> None:
        """Reset the collector, clearing all data."""
        self.current_run = None
        self.all_runs = []
        self._start_time = 0.0
        self._current_step = 0


# Convenience functions for standalone metrics analysis
def calculate_survival_curve(metrics_list: List[AgentMetrics]) -> List[tuple]:
    """
    Calculate survival curve data from agent metrics.
    
    Args:
        metrics_list: List of AgentMetrics objects
        
    Returns:
        List of (step, survival_count) tuples
    """
    if not metrics_list:
        return []
        
    max_step = max(m.survival_time for m in metrics_list)
    total_agents = len(metrics_list)
    
    curve = []
    for step in range(0, max_step + 1, max(1, max_step // 100)):
        alive = sum(1 for m in metrics_list if m.survival_time > step or m.is_alive)
        curve.append((step, alive / total_agents))
        
    return curve


def calculate_honour_progression(honour_histories: Dict[str, List[float]]) -> Dict[str, List[tuple]]:
    """
    Calculate honour progression curves for multiple agents.
    
    Args:
        honour_histories: Dictionary mapping agent_id to honour history
        
    Returns:
        Dictionary mapping agent_id to (step, honour) tuples
    """
    result = {}
    for agent_id, history in honour_histories.items():
        result[agent_id] = [(i, h) for i, h in enumerate(history)]
    return result
