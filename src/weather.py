import random


class WeatherState:
    def __init__(self, name, move_multiplier, global_damage, visibility_penalty):
        self.name = name
        self.move_multiplier = move_multiplier
        self.global_damage = global_damage
        self.visibility_penalty = visibility_penalty


class WeatherSystem:
    def __init__(self, seed=None):
        self.random = random.Random(seed)
        self.turns_in_state = 0
        self.current = self._calm()
    def _calm(self):
        return WeatherState("Calm", 1.0, 0, 0)
    def _sandstorm(self):
        return WeatherState("Sandstorm", 1.3, 0, 2)
    def _acid_rain(self):
        return WeatherState("AcidRain", 1.1, 3, 0)
    def _electrical_storm(self):
        return WeatherState("ElectricalStorm", 1.2, 1, 1)
    def maybe_transition(self):
        self.turns_in_state += 1
        p = 0.05 if self.current.name == "Calm" else 0.12
        if self.random.random() < p:
            self.current = self.random.choice([
                self._calm(), self._sandstorm(), self._acid_rain(), self._electrical_storm()
            ])
            self.turns_in_state = 0
            return True
        return False
    def movement_cost_multiplier(self):
        return self.current.move_multiplier
    def damage_this_turn(self):
        return self.current.global_damage
    def visibility_penalty(self):
        return self.current.visibility_penalty
