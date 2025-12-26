import json
import os


DEFAULT_CONFIG = {
    "grid": {
        "width": 40,
        "height": 30
    },
    "difficulty": {
        "boss_health_multiplier": 1.0,
        "wildlife_count": 4,
        "resource_count": 15,
        "weather_intensity": 1.0
    },
    "simulation": {
        "max_turns": 200,
        "turn_delay_ms": 300
    },
    "display": {
        "cell_size": 22,
        "show_grid_lines": True,
        "thermal_vision": True
    }
}


class GameConfig:
    
    def __init__(self, config_path=None):
        self.config = DEFAULT_CONFIG.copy()
        self.config_path = config_path or "config.json"
        self.load()
    
    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded = json.load(f)
                    self._merge_config(loaded)
            except (json.JSONDecodeError, IOError):
                pass
    
    def save(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _merge_config(self, loaded):
        for section, values in loaded.items():
            if section in self.config and isinstance(values, dict):
                self.config[section].update(values)
            else:
                self.config[section] = values
    
    def get(self, section, key, default=None):
        return self.config.get(section, {}).get(key, default)
    
    def set(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
    
    @property
    def grid_width(self):
        return self.get("grid", "width", 30)
    
    @property
    def grid_height(self):
        return self.get("grid", "height", 30)
    
    @property
    def boss_health_multiplier(self):
        return self.get("difficulty", "boss_health_multiplier", 1.0)
    
    @property
    def wildlife_count(self):
        return self.get("difficulty", "wildlife_count", 4)
    
    @property
    def resource_count(self):
        return self.get("difficulty", "resource_count", 15)
    
    @property
    def max_turns(self):
        return self.get("simulation", "max_turns", 200)
    
    @property
    def turn_delay(self):
        return self.get("simulation", "turn_delay_ms", 300)
    
    @property
    def cell_size(self):
        return self.get("display", "cell_size", 22)
    
    @property
    def thermal_vision(self):
        return self.get("display", "thermal_vision", True)
