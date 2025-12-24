"""
Experiment Visualization Module for Predator: Badlands
=======================================================
This module provides matplotlib-based visualization for experiment results.
Generates publication-ready graphs for survival curves, honour progression,
win rates, resource usage, and more.

Author: Predator Badlands Team
Phase: 10 - Experiments & Data Collection

Requirements: matplotlib (install with: pip install matplotlib)
"""

import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import statistics

# Try to import matplotlib
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend for saving
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.ticker import MaxNLocator
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("[WARNING] matplotlib not installed. Install with: pip install matplotlib")

# Handle imports for both package and standalone use
try:
    from .metrics import SimulationMetrics, AgentMetrics
except ImportError:
    from metrics import SimulationMetrics, AgentMetrics


# Color scheme for consistent visualization
COLORS = {
    'primary': '#FF6B35',      # Orange (Predator theme)
    'secondary': '#00D9FF',    # Cyan (Thermal vision)
    'success': '#00FF88',      # Green
    'danger': '#FF3366',       # Red
    'warning': '#FFD93D',      # Yellow
    'neutral': '#888888',      # Gray
    'boss': '#9B59B6',         # Purple
    'wildlife': '#3498DB',     # Blue
    'team': '#2ECC71',         # Green
    'background': '#1a1a2e',   # Dark background
    'grid': '#333344',         # Grid color
    'text': '#FFFFFF'          # White text
}

# Config name colors
CONFIG_COLORS = {
    'easy': '#00FF88',
    'normal': '#00D9FF',
    'hard': '#FFD93D',
    'extreme': '#FF3366',
    'no_coordination': '#9B59B6',
    'no_learning': '#3498DB',
    'baseline': '#888888'
}


def get_config_color(config_name: str) -> str:
    """Get color for a configuration name."""
    return CONFIG_COLORS.get(config_name, COLORS['primary'])


class ExperimentVisualizer:
    """
    Matplotlib-based visualizer for experiment results.
    
    Generates various plots for analyzing simulation data:
    - Win rate comparison bar charts
    - Survival time distributions
    - Honour progression curves
    - Resource usage analysis
    - Agent performance comparisons
    
    Example:
        visualizer = ExperimentVisualizer(output_dir="data/experiments/plots")
        visualizer.plot_win_rates(results_by_config)
        visualizer.plot_survival_curves(all_runs)
        visualizer.save_all_plots()
    """
    
    def __init__(self, output_dir: str = "data/experiments/plots"):
        """
        Initialize the visualizer.
        
        Args:
            output_dir: Directory for saving plot images
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.figures: Dict[str, plt.Figure] = {}
        self.saved_files: List[str] = []
        
        # Set default style
        if MATPLOTLIB_AVAILABLE:
            plt.style.use('dark_background')
            plt.rcParams['figure.facecolor'] = COLORS['background']
            plt.rcParams['axes.facecolor'] = COLORS['background']
            plt.rcParams['axes.edgecolor'] = COLORS['grid']
            plt.rcParams['axes.labelcolor'] = COLORS['text']
            plt.rcParams['xtick.color'] = COLORS['text']
            plt.rcParams['ytick.color'] = COLORS['text']
            plt.rcParams['text.color'] = COLORS['text']
            plt.rcParams['grid.color'] = COLORS['grid']
            plt.rcParams['font.size'] = 10
            plt.rcParams['axes.titlesize'] = 14
            plt.rcParams['axes.labelsize'] = 12
            
    def _check_matplotlib(self) -> bool:
        """Check if matplotlib is available."""
        if not MATPLOTLIB_AVAILABLE:
            print("[ERROR] matplotlib is not installed. Cannot generate plots.")
            return False
        return True
        
    def plot_win_rates(
        self, 
        results_by_config: Dict[str, List[SimulationMetrics]],
        filename: str = "win_rates.png"
    ) -> Optional[str]:
        """
        Plot win rates comparison across configurations.
        
        Args:
            results_by_config: Dictionary mapping config names to results
            filename: Output filename
            
        Returns:
            Path to saved file or None
        """
        if not self._check_matplotlib():
            return None
            
        fig, ax = plt.subplots(figsize=(12, 6))
        
        configs = list(results_by_config.keys())
        win_rates = []
        colors = []
        
        for config in configs:
            results = results_by_config[config]
            wins = sum(1 for r in results if r.boss_defeated)
            win_rate = (wins / len(results) * 100) if results else 0
            win_rates.append(win_rate)
            colors.append(get_config_color(config))
            
        bars = ax.bar(configs, win_rates, color=colors, edgecolor='white', linewidth=1)
        
        # Add value labels on bars
        for bar, rate in zip(bars, win_rates):
            height = bar.get_height()
            ax.annotate(f'{rate:.1f}%',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom',
                       fontweight='bold', fontsize=11)
                       
        ax.set_xlabel('Configuration', fontweight='bold')
        ax.set_ylabel('Win Rate (%)', fontweight='bold')
        ax.set_title('Win Rate Comparison by Configuration', fontweight='bold', fontsize=16)
        ax.set_ylim(0, 100)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        filepath = self.output_dir / filename
        fig.savefig(filepath, dpi=150, bbox_inches='tight')
        self.figures['win_rates'] = fig
        self.saved_files.append(str(filepath))
        
        print(f"[Visualizer] Saved win rates plot: {filepath}")
        return str(filepath)
        
    def plot_survival_distribution(
        self,
        results_by_config: Dict[str, List[SimulationMetrics]],
        filename: str = "survival_distribution.png"
    ) -> Optional[str]:
        """
        Plot survival time distribution across configurations.
        
        Args:
            results_by_config: Dictionary mapping config names to results
            filename: Output filename
            
        Returns:
            Path to saved file or None
        """
        if not self._check_matplotlib():
            return None
            
        fig, ax = plt.subplots(figsize=(14, 6))
        
        configs = list(results_by_config.keys())
        data = []
        positions = []
        colors = []
        
        for i, config in enumerate(configs):
            results = results_by_config[config]
            steps = [r.total_steps for r in results]
            data.append(steps)
            positions.append(i)
            colors.append(get_config_color(config))
            
        # Box plot
        bp = ax.boxplot(data, positions=positions, patch_artist=True, widths=0.6)
        
        # Color the boxes
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
            
        # Style other elements
        for element in ['whiskers', 'caps', 'medians']:
            plt.setp(bp[element], color='white')
        plt.setp(bp['fliers'], markerfacecolor=COLORS['warning'], marker='o', markersize=5)
        
        ax.set_xticks(positions)
        ax.set_xticklabels(configs, rotation=45, ha='right')
        ax.set_xlabel('Configuration', fontweight='bold')
        ax.set_ylabel('Simulation Steps', fontweight='bold')
        ax.set_title('Survival Time Distribution by Configuration', fontweight='bold', fontsize=16)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        filepath = self.output_dir / filename
        fig.savefig(filepath, dpi=150, bbox_inches='tight')
        self.figures['survival_distribution'] = fig
        self.saved_files.append(str(filepath))
        
        print(f"[Visualizer] Saved survival distribution plot: {filepath}")
        return str(filepath)
        
    def plot_honour_progression(
        self,
        all_runs: List[SimulationMetrics],
        filename: str = "honour_progression.png",
        max_runs: int = 5
    ) -> Optional[str]:
        """
        Plot honour progression over time for sample runs.
        
        Args:
            all_runs: List of all simulation metrics
            filename: Output filename
            max_runs: Maximum number of runs to display per config
            
        Returns:
            Path to saved file or None
        """
        if not self._check_matplotlib():
            return None
            
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Group by config
        by_config: Dict[str, List[SimulationMetrics]] = {}
        for run in all_runs:
            if run.config_name not in by_config:
                by_config[run.config_name] = []
            by_config[run.config_name].append(run)
            
        # Plot sample honour curves
        for config_name, runs in by_config.items():
            color = get_config_color(config_name)
            
            # Get Dek's honour history from sample runs
            for i, run in enumerate(runs[:max_runs]):
                for agent_id, metrics in run.agent_metrics.items():
                    if 'dek' in agent_id.lower() and metrics.honour_history:
                        alpha = 0.3 + (0.5 * (i / max_runs))
                        label = config_name if i == 0 else None
                        ax.plot(
                            range(len(metrics.honour_history)),
                            metrics.honour_history,
                            color=color,
                            alpha=alpha,
                            linewidth=1.5,
                            label=label
                        )
                        break
                        
        ax.set_xlabel('Simulation Step', fontweight='bold')
        ax.set_ylabel('Honour', fontweight='bold')
        ax.set_title("Dek's Honour Progression Over Time", fontweight='bold', fontsize=16)
        ax.legend(loc='upper left', framealpha=0.8)
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        
        filepath = self.output_dir / filename
        fig.savefig(filepath, dpi=150, bbox_inches='tight')
        self.figures['honour_progression'] = fig
        self.saved_files.append(str(filepath))
        
        print(f"[Visualizer] Saved honour progression plot: {filepath}")
        return str(filepath)
        
    def plot_average_honour_by_config(
        self,
        results_by_config: Dict[str, List[SimulationMetrics]],
        filename: str = "average_honour.png"
    ) -> Optional[str]:
        """
        Plot average final honour comparison across configurations.
        
        Args:
            results_by_config: Dictionary mapping config names to results
            filename: Output filename
            
        Returns:
            Path to saved file or None
        """
        if not self._check_matplotlib():
            return None
            
        fig, ax = plt.subplots(figsize=(12, 6))
        
        configs = []
        avg_honours = []
        std_honours = []
        colors = []
        
        for config, results in results_by_config.items():
            # Get Dek's final honour from each run
            honours = []
            for run in results:
                for agent_id, metrics in run.agent_metrics.items():
                    if 'dek' in agent_id.lower():
                        honours.append(metrics.final_honour)
                        break
                        
            if honours:
                configs.append(config)
                avg_honours.append(statistics.mean(honours))
                std_honours.append(statistics.stdev(honours) if len(honours) > 1 else 0)
                colors.append(get_config_color(config))
                
        # Bar chart with error bars
        bars = ax.bar(configs, avg_honours, yerr=std_honours, color=colors,
                     edgecolor='white', linewidth=1, capsize=5, error_kw={'elinewidth': 2})
                     
        # Add value labels
        for bar, avg in zip(bars, avg_honours):
            height = bar.get_height()
            ax.annotate(f'{avg:.1f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom',
                       fontweight='bold')
                       
        ax.set_xlabel('Configuration', fontweight='bold')
        ax.set_ylabel('Average Final Honour', fontweight='bold')
        ax.set_title('Average Final Honour by Configuration', fontweight='bold', fontsize=16)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        filepath = self.output_dir / filename
        fig.savefig(filepath, dpi=150, bbox_inches='tight')
        self.figures['average_honour'] = fig
        self.saved_files.append(str(filepath))
        
        print(f"[Visualizer] Saved average honour plot: {filepath}")
        return str(filepath)
        
    def plot_resource_efficiency(
        self,
        results_by_config: Dict[str, List[SimulationMetrics]],
        filename: str = "resource_efficiency.png"
    ) -> Optional[str]:
        """
        Plot resource collection efficiency comparison.
        
        Args:
            results_by_config: Dictionary mapping config names to results
            filename: Output filename
            
        Returns:
            Path to saved file or None
        """
        if not self._check_matplotlib():
            return None
            
        fig, ax = plt.subplots(figsize=(12, 6))
        
        configs = []
        efficiencies = []
        colors = []
        
        for config, results in results_by_config.items():
            avg_eff = statistics.mean(
                r.get_resource_efficiency() for r in results
            ) if results else 0
            
            configs.append(config)
            efficiencies.append(avg_eff * 100)  # Convert to percentage
            colors.append(get_config_color(config))
            
        bars = ax.bar(configs, efficiencies, color=colors, edgecolor='white', linewidth=1)
        
        # Add value labels
        for bar, eff in zip(bars, efficiencies):
            height = bar.get_height()
            ax.annotate(f'{eff:.1f}%',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom',
                       fontweight='bold')
                       
        ax.set_xlabel('Configuration', fontweight='bold')
        ax.set_ylabel('Resource Efficiency (%)', fontweight='bold')
        ax.set_title('Resource Collection Efficiency by Configuration', fontweight='bold', fontsize=16)
        ax.set_ylim(0, 100)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        filepath = self.output_dir / filename
        fig.savefig(filepath, dpi=150, bbox_inches='tight')
        self.figures['resource_efficiency'] = fig
        self.saved_files.append(str(filepath))
        
        print(f"[Visualizer] Saved resource efficiency plot: {filepath}")
        return str(filepath)
        
    def plot_combat_statistics(
        self,
        results_by_config: Dict[str, List[SimulationMetrics]],
        filename: str = "combat_statistics.png"
    ) -> Optional[str]:
        """
        Plot combat statistics comparison.
        
        Args:
            results_by_config: Dictionary mapping config names to results
            filename: Output filename
            
        Returns:
            Path to saved file or None
        """
        if not self._check_matplotlib():
            return None
            
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        configs = list(results_by_config.keys())
        
        # Average combats per config
        avg_combats = []
        total_kills = []
        colors = [get_config_color(c) for c in configs]
        
        for config in configs:
            results = results_by_config[config]
            avg_combats.append(
                statistics.mean(r.total_combats for r in results) if results else 0
            )
            total_kills.append(
                statistics.mean(r.get_total_kills() for r in results) if results else 0
            )
            
        # Combat count subplot
        axes[0].bar(configs, avg_combats, color=colors, edgecolor='white', linewidth=1)
        axes[0].set_xlabel('Configuration', fontweight='bold')
        axes[0].set_ylabel('Average Combats', fontweight='bold')
        axes[0].set_title('Average Combat Count', fontweight='bold', fontsize=14)
        axes[0].tick_params(axis='x', rotation=45)
        axes[0].grid(axis='y', alpha=0.3)
        
        # Add value labels
        for i, (config, val) in enumerate(zip(configs, avg_combats)):
            axes[0].annotate(f'{val:.1f}',
                           xy=(i, val), xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom', fontweight='bold')
                           
        # Kill count subplot
        axes[1].bar(configs, total_kills, color=colors, edgecolor='white', linewidth=1)
        axes[1].set_xlabel('Configuration', fontweight='bold')
        axes[1].set_ylabel('Average Kills', fontweight='bold')
        axes[1].set_title('Average Kill Count', fontweight='bold', fontsize=14)
        axes[1].tick_params(axis='x', rotation=45)
        axes[1].grid(axis='y', alpha=0.3)
        
        # Add value labels
        for i, (config, val) in enumerate(zip(configs, total_kills)):
            axes[1].annotate(f'{val:.1f}',
                           xy=(i, val), xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom', fontweight='bold')
                           
        plt.suptitle('Combat Statistics by Configuration', fontweight='bold', fontsize=16, y=1.02)
        plt.tight_layout()
        
        filepath = self.output_dir / filename
        fig.savefig(filepath, dpi=150, bbox_inches='tight')
        self.figures['combat_statistics'] = fig
        self.saved_files.append(str(filepath))
        
        print(f"[Visualizer] Saved combat statistics plot: {filepath}")
        return str(filepath)
        
    def plot_team_survival_rates(
        self,
        results_by_config: Dict[str, List[SimulationMetrics]],
        filename: str = "team_survival.png"
    ) -> Optional[str]:
        """
        Plot team survival rate comparison.
        
        Args:
            results_by_config: Dictionary mapping config names to results
            filename: Output filename
            
        Returns:
            Path to saved file or None
        """
        if not self._check_matplotlib():
            return None
            
        fig, ax = plt.subplots(figsize=(12, 6))
        
        configs = list(results_by_config.keys())
        survival_rates = []
        colors = [get_config_color(c) for c in configs]
        
        for config in configs:
            results = results_by_config[config]
            avg_survival = statistics.mean(
                r.team_survival_rate * 100 for r in results
            ) if results else 0
            survival_rates.append(avg_survival)
            
        bars = ax.bar(configs, survival_rates, color=colors, edgecolor='white', linewidth=1)
        
        # Add value labels
        for bar, rate in zip(bars, survival_rates):
            height = bar.get_height()
            ax.annotate(f'{rate:.1f}%',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom',
                       fontweight='bold')
                       
        ax.set_xlabel('Configuration', fontweight='bold')
        ax.set_ylabel('Team Survival Rate (%)', fontweight='bold')
        ax.set_title('Average Team Survival Rate by Configuration', fontweight='bold', fontsize=16)
        ax.set_ylim(0, 100)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        filepath = self.output_dir / filename
        fig.savefig(filepath, dpi=150, bbox_inches='tight')
        self.figures['team_survival'] = fig
        self.saved_files.append(str(filepath))
        
        print(f"[Visualizer] Saved team survival plot: {filepath}")
        return str(filepath)
        
    def plot_comprehensive_summary(
        self,
        results_by_config: Dict[str, List[SimulationMetrics]],
        filename: str = "comprehensive_summary.png"
    ) -> Optional[str]:
        """
        Create a comprehensive 2x2 summary plot.
        
        Args:
            results_by_config: Dictionary mapping config names to results
            filename: Output filename
            
        Returns:
            Path to saved file or None
        """
        if not self._check_matplotlib():
            return None
            
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        configs = list(results_by_config.keys())
        colors = [get_config_color(c) for c in configs]
        
        # 1. Win Rates (top-left)
        win_rates = []
        for config in configs:
            results = results_by_config[config]
            wins = sum(1 for r in results if r.boss_defeated)
            win_rates.append((wins / len(results) * 100) if results else 0)
            
        axes[0, 0].bar(configs, win_rates, color=colors, edgecolor='white')
        axes[0, 0].set_title('Win Rate (%)', fontweight='bold', fontsize=12)
        axes[0, 0].set_ylim(0, 100)
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].grid(axis='y', alpha=0.3)
        
        # 2. Average Steps (top-right)
        avg_steps = []
        for config in configs:
            results = results_by_config[config]
            avg_steps.append(
                statistics.mean(r.total_steps for r in results) if results else 0
            )
            
        axes[0, 1].bar(configs, avg_steps, color=colors, edgecolor='white')
        axes[0, 1].set_title('Average Simulation Steps', fontweight='bold', fontsize=12)
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].grid(axis='y', alpha=0.3)
        
        # 3. Team Survival (bottom-left)
        survival_rates = []
        for config in configs:
            results = results_by_config[config]
            survival_rates.append(
                statistics.mean(r.team_survival_rate * 100 for r in results) if results else 0
            )
            
        axes[1, 0].bar(configs, survival_rates, color=colors, edgecolor='white')
        axes[1, 0].set_title('Team Survival Rate (%)', fontweight='bold', fontsize=12)
        axes[1, 0].set_ylim(0, 100)
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].grid(axis='y', alpha=0.3)
        
        # 4. Average Combats (bottom-right)
        avg_combats = []
        for config in configs:
            results = results_by_config[config]
            avg_combats.append(
                statistics.mean(r.total_combats for r in results) if results else 0
            )
            
        axes[1, 1].bar(configs, avg_combats, color=colors, edgecolor='white')
        axes[1, 1].set_title('Average Combat Count', fontweight='bold', fontsize=12)
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].grid(axis='y', alpha=0.3)
        
        plt.suptitle('PREDATOR: BADLANDS - Experiment Summary', 
                    fontweight='bold', fontsize=18, y=1.02)
        plt.tight_layout()
        
        filepath = self.output_dir / filename
        fig.savefig(filepath, dpi=150, bbox_inches='tight')
        self.figures['comprehensive_summary'] = fig
        self.saved_files.append(str(filepath))
        
        print(f"[Visualizer] Saved comprehensive summary plot: {filepath}")
        return str(filepath)
        
    def plot_agent_performance_comparison(
        self,
        all_runs: List[SimulationMetrics],
        filename: str = "agent_performance.png"
    ) -> Optional[str]:
        """
        Plot performance comparison across different agent types.
        
        Args:
            all_runs: List of all simulation metrics
            filename: Output filename
            
        Returns:
            Path to saved file or None
        """
        if not self._check_matplotlib():
            return None
            
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        # Aggregate agent data
        agent_data: Dict[str, Dict[str, List]] = {}
        
        for run in all_runs:
            for agent_id, metrics in run.agent_metrics.items():
                agent_type = metrics.agent_type
                if agent_type not in agent_data:
                    agent_data[agent_type] = {
                        'kills': [],
                        'survival': [],
                        'honour': []
                    }
                agent_data[agent_type]['kills'].append(metrics.kills)
                agent_data[agent_type]['survival'].append(metrics.survival_time)
                if metrics.honour_history:
                    agent_data[agent_type]['honour'].append(metrics.final_honour)
                    
        agent_types = list(agent_data.keys())
        type_colors = [COLORS['primary'], COLORS['secondary'], COLORS['success'],
                      COLORS['warning'], COLORS['danger'], COLORS['boss']]
                      
        # 1. Average Kills
        avg_kills = [statistics.mean(agent_data[t]['kills']) if agent_data[t]['kills'] else 0 
                    for t in agent_types]
        axes[0].barh(agent_types, avg_kills, color=type_colors[:len(agent_types)])
        axes[0].set_xlabel('Average Kills', fontweight='bold')
        axes[0].set_title('Kills by Agent Type', fontweight='bold', fontsize=12)
        axes[0].grid(axis='x', alpha=0.3)
        
        # 2. Average Survival Time
        avg_survival = [statistics.mean(agent_data[t]['survival']) if agent_data[t]['survival'] else 0
                       for t in agent_types]
        axes[1].barh(agent_types, avg_survival, color=type_colors[:len(agent_types)])
        axes[1].set_xlabel('Average Survival Steps', fontweight='bold')
        axes[1].set_title('Survival by Agent Type', fontweight='bold', fontsize=12)
        axes[1].grid(axis='x', alpha=0.3)
        
        # 3. Final Honour (for applicable agents)
        avg_honour = [statistics.mean(agent_data[t]['honour']) if agent_data[t]['honour'] else 0
                     for t in agent_types]
        axes[2].barh(agent_types, avg_honour, color=type_colors[:len(agent_types)])
        axes[2].set_xlabel('Average Final Honour', fontweight='bold')
        axes[2].set_title('Honour by Agent Type', fontweight='bold', fontsize=12)
        axes[2].grid(axis='x', alpha=0.3)
        
        plt.suptitle('Agent Performance Comparison', fontweight='bold', fontsize=16, y=1.02)
        plt.tight_layout()
        
        filepath = self.output_dir / filename
        fig.savefig(filepath, dpi=150, bbox_inches='tight')
        self.figures['agent_performance'] = fig
        self.saved_files.append(str(filepath))
        
        print(f"[Visualizer] Saved agent performance plot: {filepath}")
        return str(filepath)
        
    def generate_all_plots(
        self,
        results_by_config: Dict[str, List[SimulationMetrics]]
    ) -> List[str]:
        """
        Generate all available plots for the experiment results.
        
        Args:
            results_by_config: Dictionary mapping config names to results
            
        Returns:
            List of saved file paths
        """
        if not self._check_matplotlib():
            return []
            
        all_runs = []
        for results in results_by_config.values():
            all_runs.extend(results)
            
        # Generate all plots
        self.plot_win_rates(results_by_config)
        self.plot_survival_distribution(results_by_config)
        self.plot_honour_progression(all_runs)
        self.plot_average_honour_by_config(results_by_config)
        self.plot_resource_efficiency(results_by_config)
        self.plot_combat_statistics(results_by_config)
        self.plot_team_survival_rates(results_by_config)
        self.plot_comprehensive_summary(results_by_config)
        self.plot_agent_performance_comparison(all_runs)
        
        print(f"\n[Visualizer] Generated {len(self.saved_files)} plots")
        return self.saved_files
        
    def close_all(self) -> None:
        """Close all matplotlib figures."""
        if MATPLOTLIB_AVAILABLE:
            plt.close('all')
            self.figures.clear()


def generate_report_plots(
    results_by_config: Dict[str, List[SimulationMetrics]],
    output_dir: str = "data/experiments/plots"
) -> List[str]:
    """
    Convenience function to generate all plots for a report.
    
    Args:
        results_by_config: Dictionary mapping config names to results
        output_dir: Output directory for plots
        
    Returns:
        List of saved file paths
    """
    visualizer = ExperimentVisualizer(output_dir)
    files = visualizer.generate_all_plots(results_by_config)
    visualizer.close_all()
    return files
