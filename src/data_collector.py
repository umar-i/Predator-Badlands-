"""
Data Collection Module for Predator: Badlands
==============================================
This module handles data persistence, CSV export, and data loading for experiments.
Supports saving simulation results, loading historical data, and managing experiment data.

"""

import csv
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Handle imports for both package and standalone use
try:
    from .metrics import SimulationMetrics, AgentMetrics, MetricsCollector
except ImportError:
    from metrics import SimulationMetrics, AgentMetrics, MetricsCollector


class DataCollector:
    """
    Handles data persistence and CSV export for experiment results.
    
    This class provides:
    - CSV export for simulation metrics
    - JSON export for detailed data
    - Data loading for analysis
    - Timestamped file management
    
    Example:
        collector = DataCollector(output_dir="data/experiments")
        collector.save_simulation_csv(simulation_metrics)
        collector.save_agent_metrics_csv(agent_metrics_list)
    """
    
    def __init__(self, output_dir: str = "data/experiments"):
        """
        Initialize the data collector.
        
        Args:
            output_dir: Directory for saving experiment data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.csv_dir = self.output_dir / "csv"
        self.plots_dir = self.output_dir / "plots"
        self.json_dir = self.output_dir / "json"
        
        self.csv_dir.mkdir(exist_ok=True)
        self.plots_dir.mkdir(exist_ok=True)
        self.json_dir.mkdir(exist_ok=True)
        
        # Track current experiment session
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def get_session_dir(self) -> Path:
        """Get the directory for the current session."""
        session_dir = self.output_dir / f"session_{self.session_id}"
        session_dir.mkdir(exist_ok=True)
        return session_dir
        
    def save_simulation_results_csv(
        self, 
        results: List[SimulationMetrics], 
        filename: str = None
    ) -> str:
        """
        Save multiple simulation results to CSV.
        
        Args:
            results: List of SimulationMetrics objects
            filename: Optional custom filename
            
        Returns:
            Path to the saved CSV file
        """
        if not results:
            return ""
            
        if filename is None:
            filename = f"simulation_results_{self.session_id}.csv"
            
        filepath = self.csv_dir / filename
        
        # Get headers from first result
        headers = list(results[0].to_dict().keys())
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for result in results:
                writer.writerow(result.to_dict())
                
        print(f"[DataCollector] Saved simulation results to: {filepath}")
        return str(filepath)
        
    def save_agent_metrics_csv(
        self, 
        metrics: List[AgentMetrics], 
        run_id: int = 0,
        filename: str = None
    ) -> str:
        """
        Save agent metrics to CSV.
        
        Args:
            metrics: List of AgentMetrics objects
            run_id: The simulation run ID
            filename: Optional custom filename
            
        Returns:
            Path to the saved CSV file
        """
        if not metrics:
            return ""
            
        if filename is None:
            filename = f"agent_metrics_run{run_id}_{self.session_id}.csv"
            
        filepath = self.csv_dir / filename
        
        # Get headers
        headers = ['run_id'] + list(metrics[0].to_dict().keys())
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for m in metrics:
                row = {'run_id': run_id, **m.to_dict()}
                writer.writerow(row)
                
        print(f"[DataCollector] Saved agent metrics to: {filepath}")
        return str(filepath)
        
    def save_all_agent_metrics_csv(
        self,
        all_runs: List[SimulationMetrics],
        filename: str = None
    ) -> str:
        """
        Save agent metrics from all runs to a single CSV.
        
        Args:
            all_runs: List of SimulationMetrics containing agent data
            filename: Optional custom filename
            
        Returns:
            Path to the saved CSV file
        """
        if not all_runs:
            return ""
            
        if filename is None:
            filename = f"all_agent_metrics_{self.session_id}.csv"
            
        filepath = self.csv_dir / filename
        
        # Collect all agent metrics with run info
        all_metrics = []
        for run in all_runs:
            for agent_id, metrics in run.agent_metrics.items():
                row = {
                    'run_id': run.run_id,
                    'config_name': run.config_name,
                    **metrics.to_dict()
                }
                all_metrics.append(row)
                
        if not all_metrics:
            return ""
            
        # Write CSV
        headers = list(all_metrics[0].keys())
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(all_metrics)
            
        print(f"[DataCollector] Saved all agent metrics to: {filepath}")
        return str(filepath)
        
    def save_honour_progression_csv(
        self,
        all_runs: List[SimulationMetrics],
        filename: str = None
    ) -> str:
        """
        Save honour progression data to CSV for plotting.
        
        Args:
            all_runs: List of SimulationMetrics
            filename: Optional custom filename
            
        Returns:
            Path to the saved CSV file
        """
        if not all_runs:
            return ""
            
        if filename is None:
            filename = f"honour_progression_{self.session_id}.csv"
            
        filepath = self.csv_dir / filename
        
        # Find max steps across all runs
        max_steps = max(run.total_steps for run in all_runs) if all_runs else 0
        
        # Collect honour data
        rows = []
        for run in all_runs:
            for agent_id, metrics in run.agent_metrics.items():
                for step, honour in enumerate(metrics.honour_history):
                    rows.append({
                        'run_id': run.run_id,
                        'config_name': run.config_name,
                        'agent_id': agent_id,
                        'agent_type': metrics.agent_type,
                        'step': step,
                        'honour': honour
                    })
                    
        if not rows:
            return ""
            
        # Write CSV
        headers = ['run_id', 'config_name', 'agent_id', 'agent_type', 'step', 'honour']
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
            
        print(f"[DataCollector] Saved honour progression to: {filepath}")
        return str(filepath)
        
    def save_summary_stats_csv(
        self,
        stats_by_config: Dict[str, Dict[str, Any]],
        filename: str = None
    ) -> str:
        """
        Save summary statistics by configuration.
        
        Args:
            stats_by_config: Dictionary mapping config names to stats
            filename: Optional custom filename
            
        Returns:
            Path to the saved CSV file
        """
        if not stats_by_config:
            return ""
            
        if filename is None:
            filename = f"summary_stats_{self.session_id}.csv"
            
        filepath = self.csv_dir / filename
        
        # Prepare rows
        rows = []
        for config_name, stats in stats_by_config.items():
            row = {'config_name': config_name, **stats}
            rows.append(row)
            
        if not rows:
            return ""
            
        # Write CSV
        headers = list(rows[0].keys())
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
            
        print(f"[DataCollector] Saved summary stats to: {filepath}")
        return str(filepath)
        
    def save_experiment_json(
        self,
        all_runs: List[SimulationMetrics],
        experiment_config: Dict[str, Any],
        filename: str = None
    ) -> str:
        """
        Save complete experiment data as JSON.
        
        Args:
            all_runs: List of SimulationMetrics
            experiment_config: Configuration used for experiment
            filename: Optional custom filename
            
        Returns:
            Path to the saved JSON file
        """
        if filename is None:
            filename = f"experiment_{self.session_id}.json"
            
        filepath = self.json_dir / filename
        
        # Build JSON structure
        data = {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'experiment_config': experiment_config,
            'total_runs': len(all_runs),
            'runs': []
        }
        
        for run in all_runs:
            run_data = run.to_dict()
            run_data['agent_details'] = {
                agent_id: metrics.to_dict()
                for agent_id, metrics in run.agent_metrics.items()
            }
            data['runs'].append(run_data)
            
        # Write JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
        print(f"[DataCollector] Saved experiment JSON to: {filepath}")
        return str(filepath)
        
    def load_simulation_results_csv(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Load simulation results from CSV.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            List of dictionaries containing simulation data
        """
        results = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert numeric fields
                for key in ['run_id', 'total_steps', 'total_combats', 'total_kills', 'num_agents']:
                    if key in row:
                        row[key] = int(row[key])
                for key in ['duration_seconds', 'team_survival_rate', 'average_survival_time', 'resource_efficiency']:
                    if key in row:
                        row[key] = float(row[key])
                for key in ['boss_defeated']:
                    if key in row:
                        row[key] = row[key].lower() == 'true'
                results.append(row)
        return results
        
    def load_experiment_json(self, filepath: str) -> Dict[str, Any]:
        """
        Load experiment data from JSON.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            Dictionary containing experiment data
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    def get_plots_dir(self) -> Path:
        """Get the directory for saving plots."""
        return self.plots_dir
        
    def list_csv_files(self) -> List[str]:
        """List all CSV files in the output directory."""
        return [str(f) for f in self.csv_dir.glob("*.csv")]
        
    def list_json_files(self) -> List[str]:
        """List all JSON files in the output directory."""
        return [str(f) for f in self.json_dir.glob("*.json")]


class ExperimentLogger:
    """
    Logger for experiment progress and events.
    
    Provides formatted logging for experiment runs with timestamps
    and severity levels.
    """
    
    def __init__(self, log_file: str = None, verbose: bool = True):
        """
        Initialize the experiment logger.
        
        Args:
            log_file: Optional file path for logging
            verbose: Whether to print to console
        """
        self.verbose = verbose
        self.log_file = log_file
        self.logs: List[str] = []
        
        if log_file:
            # Ensure directory exists
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            
    def _log(self, level: str, message: str) -> None:
        """Internal logging method."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] [{level}] {message}"
        self.logs.append(formatted)
        
        if self.verbose:
            print(formatted)
            
        if self.log_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(formatted + "\n")
                
    def info(self, message: str) -> None:
        """Log an info message."""
        self._log("INFO", message)
        
    def warning(self, message: str) -> None:
        """Log a warning message."""
        self._log("WARN", message)
        
    def error(self, message: str) -> None:
        """Log an error message."""
        self._log("ERROR", message)
        
    def success(self, message: str) -> None:
        """Log a success message."""
        self._log("SUCCESS", message)
        
    def experiment_start(self, config_name: str, num_runs: int) -> None:
        """Log experiment start."""
        self.info(f"Starting experiment: {config_name} ({num_runs} runs)")
        
    def run_start(self, run_id: int, total_runs: int) -> None:
        """Log simulation run start."""
        self.info(f"Run {run_id}/{total_runs} started")
        
    def run_complete(self, run_id: int, steps: int, winner: str) -> None:
        """Log simulation run completion."""
        self.success(f"Run {run_id} complete: {steps} steps, winner: {winner}")
        
    def experiment_complete(self, config_name: str, duration: float) -> None:
        """Log experiment completion."""
        self.success(f"Experiment {config_name} complete in {duration:.2f}s")
        
    def get_logs(self) -> List[str]:
        """Get all logged messages."""
        return self.logs.copy()
        
    def save_logs(self, filepath: str) -> None:
        """Save all logs to a file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.logs))
