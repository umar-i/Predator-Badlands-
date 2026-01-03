import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import GameConfig, DEFAULT_CONFIG

# Check if tkinter is available
try:
    import tkinter as tk
    TKINTER_AVAILABLE = True
    # Also check if display is available
    try:
        root = tk.Tk()
        root.destroy()
    except:
        TKINTER_AVAILABLE = False
except ImportError:
    TKINTER_AVAILABLE = False


def requires_tkinter(test_class):
    """Decorator to skip test class if tkinter is not available."""
    if not TKINTER_AVAILABLE:
        return unittest.skip("Tkinter not available")(test_class)
    return test_class


class TestDefaultConfig(unittest.TestCase):
    
    def test_default_config_exists(self):
        self.assertIsNotNone(DEFAULT_CONFIG)
    
    def test_default_grid_settings(self):
        self.assertEqual(DEFAULT_CONFIG["grid"]["width"], 40)
        self.assertEqual(DEFAULT_CONFIG["grid"]["height"], 30)
    
    def test_default_difficulty_settings(self):
        self.assertEqual(DEFAULT_CONFIG["difficulty"]["boss_health_multiplier"], 1.0)
        self.assertEqual(DEFAULT_CONFIG["difficulty"]["wildlife_count"], 4)
        self.assertEqual(DEFAULT_CONFIG["difficulty"]["resource_count"], 15)
        self.assertEqual(DEFAULT_CONFIG["difficulty"]["weather_intensity"], 1.0)
    
    def test_default_simulation_settings(self):
        self.assertEqual(DEFAULT_CONFIG["simulation"]["max_turns"], 200)
        self.assertEqual(DEFAULT_CONFIG["simulation"]["turn_delay_ms"], 300)
    
    def test_default_display_settings(self):
        self.assertEqual(DEFAULT_CONFIG["display"]["cell_size"], 22)
        self.assertTrue(DEFAULT_CONFIG["display"]["show_grid_lines"])
        self.assertTrue(DEFAULT_CONFIG["display"]["thermal_vision"])


class TestGameConfig(unittest.TestCase):
    
    def test_config_creation(self):
        config = GameConfig(config_path="test_nonexistent.json")
        self.assertIsNotNone(config.config)
    
    def test_get_existing_value(self):
        config = GameConfig(config_path="test_nonexistent.json")
        value = config.get("grid", "width", 0)
        self.assertEqual(value, 40)
    
    def test_get_missing_value_default(self):
        config = GameConfig(config_path="test_nonexistent.json")
        value = config.get("nonexistent", "key", "default")
        self.assertEqual(value, "default")
    
    def test_set_value(self):
        config = GameConfig(config_path="test_nonexistent.json")
        config.set("grid", "width", 50)
        value = config.get("grid", "width", 0)
        self.assertEqual(value, 50)
    
    def test_set_new_section(self):
        config = GameConfig(config_path="test_nonexistent.json")
        config.set("new_section", "new_key", "new_value")
        value = config.get("new_section", "new_key", None)
        self.assertEqual(value, "new_value")


class TestGameConfigProperties(unittest.TestCase):
    
    def test_grid_width_property(self):
        config = GameConfig(config_path="test_nonexistent_config.json")
        width = config.grid_width
        self.assertIsInstance(width, int)
        self.assertGreater(width, 0)
    
    def test_grid_height_property(self):
        config = GameConfig(config_path="test_nonexistent_config.json")
        height = config.grid_height
        self.assertIsInstance(height, int)
        self.assertGreater(height, 0)
    
    def test_boss_health_multiplier_property(self):
        config = GameConfig(config_path="test_nonexistent.json")
        self.assertEqual(config.boss_health_multiplier, 1.0)
    
    def test_wildlife_count_property(self):
        config = GameConfig(config_path="test_nonexistent.json")
        self.assertEqual(config.wildlife_count, 4)
    
    def test_resource_count_property(self):
        config = GameConfig(config_path="test_nonexistent.json")
        self.assertEqual(config.resource_count, 15)
    
    def test_max_turns_property(self):
        config = GameConfig(config_path="test_nonexistent.json")
        self.assertEqual(config.max_turns, 200)
    
    def test_turn_delay_property(self):
        config = GameConfig(config_path="test_nonexistent.json")
        self.assertEqual(config.turn_delay, 300)
    
    def test_cell_size_property(self):
        config = GameConfig(config_path="test_nonexistent.json")
        self.assertEqual(config.cell_size, 22)
    
    def test_thermal_vision_property(self):
        config = GameConfig(config_path="test_nonexistent.json")
        self.assertTrue(config.thermal_vision)


class TestGameConfigMerge(unittest.TestCase):
    
    def test_merge_partial_config(self):
        config = GameConfig(config_path="test_nonexistent.json")
        
        partial_config = {
            "grid": {
                "width": 50
            }
        }
        
        config._merge_config(partial_config)
        
        self.assertEqual(config.get("grid", "width", 0), 50)
        self.assertEqual(config.get("grid", "height", 0), 30)
    
    def test_merge_new_section(self):
        config = GameConfig(config_path="test_nonexistent.json")
        
        new_section = {
            "custom": {
                "setting1": "value1"
            }
        }
        
        config._merge_config(new_section)
        
        self.assertEqual(config.get("custom", "setting1", None), "value1")


@requires_tkinter
class TestVisualizerColors(unittest.TestCase):
    
    def test_thermal_colors_import(self):
        from visualizer import PredatorVisualizer
        
        colors = PredatorVisualizer.THERMAL_COLORS
        
        self.assertIn('background', colors)
        self.assertIn('dek', colors)
        self.assertIn('thia', colors)
        self.assertIn('boss', colors)
        self.assertIn('wildlife', colors)
    
    def test_thermal_color_values(self):
        from visualizer import PredatorVisualizer
        
        colors = PredatorVisualizer.THERMAL_COLORS
        
        self.assertEqual(colors['background'], '#050505')
        self.assertEqual(colors['dek'], '#00ff00')
        self.assertEqual(colors['thia'], '#00ffff')
        self.assertEqual(colors['boss'], '#ff00ff')


@requires_tkinter
class TestVisualizerAgentConfig(unittest.TestCase):
    
    def test_agent_config_exists(self):
        from visualizer import PredatorVisualizer
        
        config = PredatorVisualizer.AGENT_CONFIG
        
        self.assertIn('Dek', config)
        self.assertIn('Thia', config)
        self.assertIn('BossAdversary', config)
        self.assertIn('WildlifeAgent', config)
    
    def test_dek_config(self):
        from visualizer import PredatorVisualizer
        
        dek_config = PredatorVisualizer.AGENT_CONFIG['Dek']
        
        self.assertEqual(dek_config['color'], 'dek')
        self.assertEqual(dek_config['label'], 'DEK')
        self.assertEqual(dek_config['icon'], 'predator_mask')
        self.assertEqual(dek_config['priority'], 1)
    
    def test_thia_config(self):
        from visualizer import PredatorVisualizer
        
        thia_config = PredatorVisualizer.AGENT_CONFIG['Thia']
        
        self.assertEqual(thia_config['color'], 'thia')
        self.assertEqual(thia_config['label'], 'THIA')
        self.assertEqual(thia_config['icon'], 'android')
    
    def test_boss_config(self):
        from visualizer import PredatorVisualizer
        
        boss_config = PredatorVisualizer.AGENT_CONFIG['BossAdversary']
        
        self.assertEqual(boss_config['color'], 'boss')
        self.assertEqual(boss_config['label'], 'BOSS')
        self.assertEqual(boss_config['priority'], 0)
    
    def test_wildlife_config(self):
        from visualizer import PredatorVisualizer
        
        wildlife_config = PredatorVisualizer.AGENT_CONFIG['WildlifeAgent']
        
        self.assertEqual(wildlife_config['color'], 'wildlife')
        self.assertEqual(wildlife_config['label'], 'BEAST')


@requires_tkinter
class TestVisualizerTerrainColors(unittest.TestCase):
    
    def test_terrain_colors_defined(self):
        from visualizer import PredatorVisualizer
        
        colors = PredatorVisualizer.THERMAL_COLORS
        
        self.assertIn('empty', colors)
        self.assertIn('desert', colors)
        self.assertIn('rocky', colors)
        self.assertIn('canyon', colors)
        self.assertIn('hostile', colors)
        self.assertIn('trap', colors)
        self.assertIn('teleport', colors)


@requires_tkinter
class TestVisualizerHealthColors(unittest.TestCase):
    
    def test_health_colors_defined(self):
        from visualizer import PredatorVisualizer
        
        colors = PredatorVisualizer.THERMAL_COLORS
        
        self.assertIn('health_high', colors)
        self.assertIn('health_mid', colors)
        self.assertIn('health_low', colors)
        self.assertIn('health_bg', colors)
    
    def test_health_color_values(self):
        from visualizer import PredatorVisualizer
        
        colors = PredatorVisualizer.THERMAL_COLORS
        
        self.assertEqual(colors['health_high'], '#00ff00')
        self.assertEqual(colors['health_mid'], '#ffff00')
        self.assertEqual(colors['health_low'], '#ff0000')


@requires_tkinter
class TestVisualizerTextColors(unittest.TestCase):
    
    def test_text_colors_defined(self):
        from visualizer import PredatorVisualizer
        
        colors = PredatorVisualizer.THERMAL_COLORS
        
        self.assertIn('text_primary', colors)
        self.assertIn('text_secondary', colors)
        self.assertIn('text_warning', colors)
        self.assertIn('text_danger', colors)


@requires_tkinter
class TestVisualizerPanelColors(unittest.TestCase):
    
    def test_panel_colors_defined(self):
        from visualizer import PredatorVisualizer
        
        colors = PredatorVisualizer.THERMAL_COLORS
        
        self.assertIn('panel_bg', colors)
        self.assertIn('panel_border', colors)
        self.assertIn('tooltip_bg', colors)
        self.assertIn('tooltip_border', colors)


@requires_tkinter
class TestVisualizerPrioritySystem(unittest.TestCase):
    
    def test_boss_highest_priority(self):
        from visualizer import PredatorVisualizer
        
        config = PredatorVisualizer.AGENT_CONFIG
        
        boss_priority = config['BossAdversary']['priority']
        dek_priority = config['Dek']['priority']
        
        self.assertLess(boss_priority, dek_priority)
    
    def test_priority_ordering(self):
        from visualizer import PredatorVisualizer
        
        config = PredatorVisualizer.AGENT_CONFIG
        
        priorities = [
            (config['BossAdversary']['priority'], 'BossAdversary'),
            (config['Dek']['priority'], 'Dek'),
            (config['Thia']['priority'], 'Thia'),
        ]
        
        sorted_priorities = sorted(priorities, key=lambda x: x[0])
        
        self.assertEqual(sorted_priorities[0][1], 'BossAdversary')


class TestConfigIntegration(unittest.TestCase):
    
    def test_config_affects_grid_size(self):
        config = GameConfig(config_path="test_nonexistent.json")
        
        from grid import Grid
        grid = Grid(config.grid_width, config.grid_height)
        
        # Default is 50x50 when no config file found
        self.assertEqual(grid.width, config.grid_width)
        self.assertEqual(grid.height, config.grid_height)


@requires_tkinter
class TestVisualizerAgentSizes(unittest.TestCase):
    
    def test_agent_sizes_defined(self):
        from visualizer import PredatorVisualizer
        
        config = PredatorVisualizer.AGENT_CONFIG
        
        for agent_type, agent_config in config.items():
            self.assertIn('size', agent_config)
            self.assertIsInstance(agent_config['size'], int)
    
    def test_boss_largest_size(self):
        from visualizer import PredatorVisualizer
        
        config = PredatorVisualizer.AGENT_CONFIG
        
        boss_size = config['BossAdversary']['size']
        
        for agent_type, agent_config in config.items():
            if agent_type != 'BossAdversary':
                self.assertLessEqual(agent_config['size'], boss_size)


@requires_tkinter
class TestVisualizerGlowEffects(unittest.TestCase):
    
    def test_glow_colors_defined(self):
        from visualizer import PredatorVisualizer
        
        colors = PredatorVisualizer.THERMAL_COLORS
        
        self.assertIn('dek_glow', colors)
        self.assertIn('thia_glow', colors)
        self.assertIn('wildlife_glow', colors)
        self.assertIn('boss_glow', colors)


class TestRendererModule(unittest.TestCase):
    
    def test_renderer_imports(self):
        try:
            from renderer import Renderer
            self.assertTrue(True)
        except ImportError:
            self.skipTest("Renderer module not implemented")


if __name__ == '__main__':
    unittest.main()
