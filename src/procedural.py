from typing import List, Tuple, Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import random
import math
import time


class HazardType(Enum):
    ACID_POOL = "acid_pool"
    SPIKE_TRAP = "spike_trap"
    FIRE_VENT = "fire_vent"
    QUICKSAND = "quicksand"
    RADIATION = "radiation"
    ELECTRIC_FIELD = "electric_field"
    POISON_GAS = "poison_gas"
    COLLAPSE_ZONE = "collapse_zone"


class PatternType(Enum):
    RANDOM = "random"
    CLUSTERED = "clustered"
    LINEAR = "linear"
    CIRCULAR = "circular"
    SPIRAL = "spiral"
    WAVE = "wave"
    SYMMETRIC = "symmetric"
    PERIMETER = "perimeter"


class DifficultyLevel(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    NIGHTMARE = 4


@dataclass
class HazardConfig:
    hazard_type: HazardType
    damage: int
    radius: int = 1
    duration: int = -1
    spread_chance: float = 0.0
    activation_delay: int = 0
    cooldown: int = 0


@dataclass
class ProceduralHazard:
    hazard_type: HazardType
    position: Tuple[int, int]
    damage: int
    radius: int
    duration: int
    is_active: bool = True
    activation_delay: int = 0
    cooldown_remaining: int = 0
    created_turn: int = 0
    
    def tick(self) -> bool:
        if self.activation_delay > 0:
            self.activation_delay -= 1
            return False
        
        if self.cooldown_remaining > 0:
            self.cooldown_remaining -= 1
            return False
        
        if self.duration > 0:
            self.duration -= 1
            if self.duration == 0:
                self.is_active = False
        
        return self.is_active


HAZARD_TEMPLATES = {
    HazardType.ACID_POOL: HazardConfig(
        hazard_type=HazardType.ACID_POOL,
        damage=8,
        radius=2,
        duration=15,
        spread_chance=0.1
    ),
    HazardType.SPIKE_TRAP: HazardConfig(
        hazard_type=HazardType.SPIKE_TRAP,
        damage=20,
        radius=1,
        duration=-1,
        activation_delay=0,
        cooldown=3
    ),
    HazardType.FIRE_VENT: HazardConfig(
        hazard_type=HazardType.FIRE_VENT,
        damage=12,
        radius=2,
        duration=8,
        activation_delay=1
    ),
    HazardType.QUICKSAND: HazardConfig(
        hazard_type=HazardType.QUICKSAND,
        damage=3,
        radius=2,
        duration=20,
        spread_chance=0.05
    ),
    HazardType.RADIATION: HazardConfig(
        hazard_type=HazardType.RADIATION,
        damage=5,
        radius=3,
        duration=25
    ),
    HazardType.ELECTRIC_FIELD: HazardConfig(
        hazard_type=HazardType.ELECTRIC_FIELD,
        damage=15,
        radius=2,
        duration=5,
        cooldown=4
    ),
    HazardType.POISON_GAS: HazardConfig(
        hazard_type=HazardType.POISON_GAS,
        damage=6,
        radius=3,
        duration=12,
        spread_chance=0.15
    ),
    HazardType.COLLAPSE_ZONE: HazardConfig(
        hazard_type=HazardType.COLLAPSE_ZONE,
        damage=25,
        radius=2,
        duration=1,
        activation_delay=2
    )
}


class NoiseGenerator:
    
    def __init__(self, seed: int = None):
        self.seed = seed if seed else int(time.time())
        random.seed(self.seed)
        self.permutation = list(range(256))
        random.shuffle(self.permutation)
        self.permutation *= 2
    
    def fade(self, t: float) -> float:
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def lerp(self, a: float, b: float, t: float) -> float:
        return a + t * (b - a)
    
    def grad(self, hash_val: int, x: float, y: float) -> float:
        h = hash_val & 3
        if h == 0:
            return x + y
        elif h == 1:
            return -x + y
        elif h == 2:
            return x - y
        else:
            return -x - y
    
    def perlin_2d(self, x: float, y: float) -> float:
        xi = int(x) & 255
        yi = int(y) & 255
        
        xf = x - int(x)
        yf = y - int(y)
        
        u = self.fade(xf)
        v = self.fade(yf)
        
        aa = self.permutation[self.permutation[xi] + yi]
        ab = self.permutation[self.permutation[xi] + yi + 1]
        ba = self.permutation[self.permutation[xi + 1] + yi]
        bb = self.permutation[self.permutation[xi + 1] + yi + 1]
        
        x1 = self.lerp(self.grad(aa, xf, yf), self.grad(ba, xf - 1, yf), u)
        x2 = self.lerp(self.grad(ab, xf, yf - 1), self.grad(bb, xf - 1, yf - 1), u)
        
        return self.lerp(x1, x2, v)
    
    def octave_perlin(self, x: float, y: float, octaves: int = 4, persistence: float = 0.5) -> float:
        total = 0.0
        frequency = 1.0
        amplitude = 1.0
        max_value = 0.0
        
        for _ in range(octaves):
            total += self.perlin_2d(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= 2
        
        return total / max_value


class HazardGenerator:
    
    def __init__(self, grid_width: int, grid_height: int, seed: int = None):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.noise = NoiseGenerator(seed)
        self.hazards: List[ProceduralHazard] = []
        self.hazard_map: Dict[Tuple[int, int], List[ProceduralHazard]] = {}
        self.generation_history = []
        self.current_turn = 0
    
    def generate_hazard_at(self, position: Tuple[int, int], hazard_type: HazardType, 
                          turn: int = 0) -> ProceduralHazard:
        config = HAZARD_TEMPLATES[hazard_type]
        
        hazard = ProceduralHazard(
            hazard_type=hazard_type,
            position=position,
            damage=config.damage,
            radius=config.radius,
            duration=config.duration,
            activation_delay=config.activation_delay,
            cooldown_remaining=0,
            created_turn=turn
        )
        
        self.hazards.append(hazard)
        
        if position not in self.hazard_map:
            self.hazard_map[position] = []
        self.hazard_map[position].append(hazard)
        
        self.generation_history.append({
            'turn': turn,
            'type': hazard_type.value,
            'position': position
        })
        
        return hazard
    
    def generate_pattern(self, pattern_type: PatternType, center: Tuple[int, int],
                        hazard_type: HazardType, count: int = 5, 
                        spread: int = 5, turn: int = 0) -> List[ProceduralHazard]:
        
        generated = []
        positions = self._get_pattern_positions(pattern_type, center, count, spread)
        
        for pos in positions:
            x, y = pos
            if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                hazard = self.generate_hazard_at((x, y), hazard_type, turn)
                generated.append(hazard)
        
        return generated
    
    def _get_pattern_positions(self, pattern_type: PatternType, center: Tuple[int, int],
                               count: int, spread: int) -> List[Tuple[int, int]]:
        cx, cy = center
        positions = []
        
        if pattern_type == PatternType.RANDOM:
            for _ in range(count):
                x = cx + random.randint(-spread, spread)
                y = cy + random.randint(-spread, spread)
                positions.append((x, y))
        
        elif pattern_type == PatternType.CLUSTERED:
            for _ in range(count):
                angle = random.random() * 2 * math.pi
                distance = random.random() * spread * 0.6
                x = int(cx + math.cos(angle) * distance)
                y = int(cy + math.sin(angle) * distance)
                positions.append((x, y))
        
        elif pattern_type == PatternType.LINEAR:
            direction = random.choice([(1, 0), (0, 1), (1, 1), (1, -1)])
            for i in range(count):
                x = cx + direction[0] * i * (spread // count)
                y = cy + direction[1] * i * (spread // count)
                positions.append((x, y))
        
        elif pattern_type == PatternType.CIRCULAR:
            for i in range(count):
                angle = (2 * math.pi * i) / count
                x = int(cx + math.cos(angle) * spread)
                y = int(cy + math.sin(angle) * spread)
                positions.append((x, y))
        
        elif pattern_type == PatternType.SPIRAL:
            for i in range(count):
                angle = (4 * math.pi * i) / count
                distance = (spread * i) / count
                x = int(cx + math.cos(angle) * distance)
                y = int(cy + math.sin(angle) * distance)
                positions.append((x, y))
        
        elif pattern_type == PatternType.WAVE:
            for i in range(count):
                x = cx - spread + (2 * spread * i) // count
                y = int(cy + math.sin(i * 0.5) * (spread // 2))
                positions.append((x, y))
        
        elif pattern_type == PatternType.SYMMETRIC:
            half_count = count // 2
            for i in range(half_count):
                offset_x = random.randint(1, spread)
                offset_y = random.randint(-spread // 2, spread // 2)
                positions.append((cx + offset_x, cy + offset_y))
                positions.append((cx - offset_x, cy + offset_y))
        
        elif pattern_type == PatternType.PERIMETER:
            side = int(math.sqrt(count))
            for i in range(side):
                positions.append((cx - spread, cy - spread + (2 * spread * i) // side))
                positions.append((cx + spread, cy - spread + (2 * spread * i) // side))
                positions.append((cx - spread + (2 * spread * i) // side, cy - spread))
                positions.append((cx - spread + (2 * spread * i) // side, cy + spread))
        
        return positions[:count]
    
    def generate_noise_based_hazards(self, hazard_type: HazardType, 
                                     threshold: float = 0.3,
                                     scale: float = 0.1,
                                     turn: int = 0) -> List[ProceduralHazard]:
        generated = []
        
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                noise_value = self.noise.octave_perlin(x * scale, y * scale)
                
                if noise_value > threshold:
                    hazard = self.generate_hazard_at((x, y), hazard_type, turn)
                    generated.append(hazard)
        
        return generated
    
    def update_hazards(self, turn: int) -> List[Tuple[int, int]]:
        self.current_turn = turn
        expired_positions = []
        
        active_hazards = []
        for hazard in self.hazards:
            if hazard.tick():
                active_hazards.append(hazard)
                
                config = HAZARD_TEMPLATES[hazard.hazard_type]
                if config.spread_chance > 0 and random.random() < config.spread_chance:
                    self._spread_hazard(hazard, turn)
            else:
                expired_positions.append(hazard.position)
                if hazard.position in self.hazard_map:
                    if hazard in self.hazard_map[hazard.position]:
                        self.hazard_map[hazard.position].remove(hazard)
        
        self.hazards = active_hazards
        return expired_positions
    
    def _spread_hazard(self, source: ProceduralHazard, turn: int):
        x, y = source.position
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        dx, dy = random.choice(directions)
        
        new_x, new_y = x + dx, y + dy
        
        if 0 <= new_x < self.grid_width and 0 <= new_y < self.grid_height:
            if (new_x, new_y) not in self.hazard_map or not self.hazard_map[(new_x, new_y)]:
                self.generate_hazard_at((new_x, new_y), source.hazard_type, turn)
    
    def get_hazards_at(self, position: Tuple[int, int]) -> List[ProceduralHazard]:
        return self.hazard_map.get(position, [])
    
    def get_hazards_in_radius(self, center: Tuple[int, int], radius: int) -> List[ProceduralHazard]:
        result = []
        cx, cy = center
        
        for hazard in self.hazards:
            if hazard.is_active:
                hx, hy = hazard.position
                distance = math.sqrt((hx - cx)**2 + (hy - cy)**2)
                if distance <= radius + hazard.radius:
                    result.append(hazard)
        
        return result
    
    def calculate_damage_at(self, position: Tuple[int, int]) -> int:
        total_damage = 0
        px, py = position
        
        for hazard in self.hazards:
            if hazard.is_active and hazard.activation_delay == 0:
                hx, hy = hazard.position
                distance = math.sqrt((hx - px)**2 + (hy - py)**2)
                if distance <= hazard.radius:
                    damage_factor = 1.0 - (distance / (hazard.radius + 1))
                    total_damage += int(hazard.damage * damage_factor)
        
        return total_damage
    
    def clear_hazards(self):
        self.hazards.clear()
        self.hazard_map.clear()


@dataclass
class AdversaryPattern:
    name: str
    movement_sequence: List[Tuple[int, int]]
    attack_sequence: List[str]
    ability_cooldowns: Dict[str, int]
    phase_transitions: Dict[int, 'AdversaryPattern'] = None
    
    def __post_init__(self):
        if self.phase_transitions is None:
            self.phase_transitions = {}


class PatternLibrary:
    
    MOVEMENT_PATTERNS = {
        'patrol_square': [
            (1, 0), (1, 0), (0, 1), (0, 1),
            (-1, 0), (-1, 0), (0, -1), (0, -1)
        ],
        'patrol_circle': [
            (1, 0), (1, 1), (0, 1), (-1, 1),
            (-1, 0), (-1, -1), (0, -1), (1, -1)
        ],
        'aggressive_chase': [
            (2, 0), (2, 0), (1, 1), (1, 1)
        ],
        'defensive_retreat': [
            (-1, 0), (-1, -1), (-1, 0), (0, -1)
        ],
        'flanking_left': [
            (0, -2), (1, -1), (2, 0), (1, 1)
        ],
        'flanking_right': [
            (0, 2), (1, 1), (2, 0), (1, -1)
        ],
        'random_aggressive': None,
        'hold_position': [(0, 0)]
    }
    
    ATTACK_PATTERNS = {
        'basic_melee': ['attack', 'attack', 'wait', 'attack'],
        'heavy_hitter': ['charge', 'heavy_attack', 'wait', 'wait', 'heavy_attack'],
        'ranged_kite': ['ranged', 'move_back', 'ranged', 'move_back'],
        'berserk': ['attack', 'attack', 'attack', 'heavy_attack'],
        'tactical': ['scan', 'attack', 'defend', 'attack'],
        'boss_phase1': ['attack', 'ability', 'attack', 'attack', 'ability'],
        'boss_phase2': ['ability', 'attack', 'ability', 'attack', 'ultimate']
    }


class AdversaryPatternGenerator:
    
    def __init__(self, difficulty: DifficultyLevel = DifficultyLevel.MEDIUM):
        self.difficulty = difficulty
        self.patterns: Dict[str, AdversaryPattern] = {}
        self.active_patterns: Dict[str, int] = {}
        self.pattern_effectiveness: Dict[str, float] = {}
        
    def generate_pattern(self, adversary_type: str, behavior_bias: str = 'balanced') -> AdversaryPattern:
        if behavior_bias == 'aggressive':
            movement = self._generate_aggressive_movement()
            attacks = self._generate_aggressive_attacks()
        elif behavior_bias == 'defensive':
            movement = self._generate_defensive_movement()
            attacks = self._generate_defensive_attacks()
        elif behavior_bias == 'tactical':
            movement = self._generate_tactical_movement()
            attacks = self._generate_tactical_attacks()
        else:
            movement = self._generate_balanced_movement()
            attacks = self._generate_balanced_attacks()
        
        cooldowns = self._generate_ability_cooldowns()
        
        pattern = AdversaryPattern(
            name=f"{adversary_type}_{behavior_bias}_{random.randint(1000, 9999)}",
            movement_sequence=movement,
            attack_sequence=attacks,
            ability_cooldowns=cooldowns
        )
        
        self.patterns[pattern.name] = pattern
        return pattern
    
    def _generate_aggressive_movement(self) -> List[Tuple[int, int]]:
        base = PatternLibrary.MOVEMENT_PATTERNS['aggressive_chase'].copy()
        
        for _ in range(random.randint(2, 4)):
            base.append((random.randint(1, 2), random.randint(-1, 1)))
        
        return base
    
    def _generate_defensive_movement(self) -> List[Tuple[int, int]]:
        base = PatternLibrary.MOVEMENT_PATTERNS['defensive_retreat'].copy()
        
        for _ in range(random.randint(2, 4)):
            base.append((random.randint(-2, 0), random.randint(-1, 1)))
        
        return base
    
    def _generate_tactical_movement(self) -> List[Tuple[int, int]]:
        patterns = ['flanking_left', 'flanking_right', 'patrol_circle']
        chosen = random.choice(patterns)
        base = PatternLibrary.MOVEMENT_PATTERNS[chosen].copy()
        
        random.shuffle(base)
        return base
    
    def _generate_balanced_movement(self) -> List[Tuple[int, int]]:
        base = PatternLibrary.MOVEMENT_PATTERNS['patrol_square'].copy()
        
        for i in range(len(base)):
            if random.random() < 0.3:
                base[i] = (
                    base[i][0] + random.randint(-1, 1),
                    base[i][1] + random.randint(-1, 1)
                )
        
        return base
    
    def _generate_aggressive_attacks(self) -> List[str]:
        return PatternLibrary.ATTACK_PATTERNS['berserk'].copy()
    
    def _generate_defensive_attacks(self) -> List[str]:
        return PatternLibrary.ATTACK_PATTERNS['tactical'].copy()
    
    def _generate_tactical_attacks(self) -> List[str]:
        base = PatternLibrary.ATTACK_PATTERNS['tactical'].copy()
        base.extend(['flank', 'attack'])
        return base
    
    def _generate_balanced_attacks(self) -> List[str]:
        return PatternLibrary.ATTACK_PATTERNS['basic_melee'].copy()
    
    def _generate_ability_cooldowns(self) -> Dict[str, int]:
        base_cooldown = {
            DifficultyLevel.EASY: 5,
            DifficultyLevel.MEDIUM: 4,
            DifficultyLevel.HARD: 3,
            DifficultyLevel.NIGHTMARE: 2
        }[self.difficulty]
        
        return {
            'special_attack': base_cooldown,
            'area_attack': base_cooldown + 2,
            'buff': base_cooldown + 1,
            'summon': base_cooldown * 2,
            'ultimate': base_cooldown * 3
        }
    
    def generate_boss_pattern(self, phase: int = 1) -> AdversaryPattern:
        if phase == 1:
            movement = PatternLibrary.MOVEMENT_PATTERNS['patrol_square'].copy()
            attacks = PatternLibrary.ATTACK_PATTERNS['boss_phase1'].copy()
        else:
            movement = self._generate_aggressive_movement()
            attacks = PatternLibrary.ATTACK_PATTERNS['boss_phase2'].copy()
        
        cooldowns = {
            'earthquake': 4 - phase,
            'energy_blast': 3 - phase,
            'regeneration': 5,
            'ultimate': 8 - phase
        }
        
        pattern = AdversaryPattern(
            name=f"boss_phase_{phase}",
            movement_sequence=movement,
            attack_sequence=attacks,
            ability_cooldowns=cooldowns
        )
        
        if phase == 1:
            pattern.phase_transitions[50] = self.generate_boss_pattern(2)
        
        return pattern
    
    def mutate_pattern(self, pattern: AdversaryPattern, mutation_rate: float = 0.2) -> AdversaryPattern:
        new_movement = pattern.movement_sequence.copy()
        for i in range(len(new_movement)):
            if random.random() < mutation_rate:
                new_movement[i] = (
                    new_movement[i][0] + random.randint(-1, 1),
                    new_movement[i][1] + random.randint(-1, 1)
                )
        
        new_attacks = pattern.attack_sequence.copy()
        if random.random() < mutation_rate:
            idx = random.randint(0, len(new_attacks) - 1)
            options = ['attack', 'heavy_attack', 'defend', 'wait', 'ability']
            new_attacks[idx] = random.choice(options)
        
        new_cooldowns = pattern.ability_cooldowns.copy()
        for ability in new_cooldowns:
            if random.random() < mutation_rate:
                new_cooldowns[ability] = max(1, new_cooldowns[ability] + random.randint(-1, 1))
        
        return AdversaryPattern(
            name=f"{pattern.name}_mutated",
            movement_sequence=new_movement,
            attack_sequence=new_attacks,
            ability_cooldowns=new_cooldowns
        )
    
    def record_effectiveness(self, pattern_name: str, success: bool):
        if pattern_name not in self.pattern_effectiveness:
            self.pattern_effectiveness[pattern_name] = 0.5
        
        current = self.pattern_effectiveness[pattern_name]
        delta = 0.1 if success else -0.1
        self.pattern_effectiveness[pattern_name] = max(0.1, min(1.0, current + delta))
    
    def get_best_pattern(self) -> Optional[AdversaryPattern]:
        if not self.pattern_effectiveness:
            return None
        
        best_name = max(self.pattern_effectiveness.keys(), 
                       key=lambda k: self.pattern_effectiveness[k])
        return self.patterns.get(best_name)


class ProceduralEventGenerator:
    
    def __init__(self, grid_width: int, grid_height: int):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.event_queue = []
        self.event_history = []
        self.event_weights = {
            'hazard_spawn': 0.3,
            'item_spawn': 0.2,
            'weather_change': 0.15,
            'enemy_spawn': 0.15,
            'environmental_effect': 0.2
        }
    
    def generate_event(self, turn: int, game_state: Dict) -> Optional[Dict]:
        event_type = self._weighted_random_choice(self.event_weights)
        
        if event_type == 'hazard_spawn':
            return self._generate_hazard_event(turn, game_state)
        elif event_type == 'item_spawn':
            return self._generate_item_event(turn, game_state)
        elif event_type == 'weather_change':
            return self._generate_weather_event(turn)
        elif event_type == 'enemy_spawn':
            return self._generate_enemy_event(turn, game_state)
        elif event_type == 'environmental_effect':
            return self._generate_environmental_event(turn)
        
        return None
    
    def _weighted_random_choice(self, weights: Dict[str, float]) -> str:
        total = sum(weights.values())
        r = random.random() * total
        cumulative = 0.0
        
        for choice, weight in weights.items():
            cumulative += weight
            if r <= cumulative:
                return choice
        
        return list(weights.keys())[0]
    
    def _generate_hazard_event(self, turn: int, game_state: Dict) -> Dict:
        hazard_type = random.choice(list(HazardType))
        pattern = random.choice(list(PatternType))
        
        player_pos = game_state.get('player_position', (15, 15))
        
        angle = random.random() * 2 * math.pi
        distance = random.randint(5, 12)
        center_x = int(player_pos[0] + math.cos(angle) * distance)
        center_y = int(player_pos[1] + math.sin(angle) * distance)
        
        center_x = max(0, min(self.grid_width - 1, center_x))
        center_y = max(0, min(self.grid_height - 1, center_y))
        
        return {
            'type': 'hazard_spawn',
            'turn': turn,
            'hazard_type': hazard_type,
            'pattern': pattern,
            'center': (center_x, center_y),
            'count': random.randint(3, 7),
            'spread': random.randint(3, 6)
        }
    
    def _generate_item_event(self, turn: int, game_state: Dict) -> Dict:
        item_types = ['medkit', 'energy_pack', 'weapon_upgrade', 'shield']
        
        return {
            'type': 'item_spawn',
            'turn': turn,
            'item_type': random.choice(item_types),
            'position': (
                random.randint(0, self.grid_width - 1),
                random.randint(0, self.grid_height - 1)
            )
        }
    
    def _generate_weather_event(self, turn: int) -> Dict:
        weather_types = ['clear', 'sandstorm', 'acid_rain', 'electrical_storm']
        
        return {
            'type': 'weather_change',
            'turn': turn,
            'weather': random.choice(weather_types),
            'duration': random.randint(5, 15)
        }
    
    def _generate_enemy_event(self, turn: int, game_state: Dict) -> Dict:
        enemy_types = ['wildlife', 'hunter', 'swarm']
        
        return {
            'type': 'enemy_spawn',
            'turn': turn,
            'enemy_type': random.choice(enemy_types),
            'count': random.randint(1, 3),
            'position': (
                random.randint(0, self.grid_width - 1),
                random.randint(0, self.grid_height - 1)
            )
        }
    
    def _generate_environmental_event(self, turn: int) -> Dict:
        effects = ['earthquake', 'terrain_shift', 'visibility_change', 'power_surge']
        
        return {
            'type': 'environmental_effect',
            'turn': turn,
            'effect': random.choice(effects),
            'intensity': random.uniform(0.5, 1.5),
            'duration': random.randint(3, 8)
        }
    
    def queue_event(self, event: Dict, delay: int = 0):
        event['execute_turn'] = event.get('turn', 0) + delay
        self.event_queue.append(event)
        self.event_queue.sort(key=lambda e: e['execute_turn'])
    
    def get_pending_events(self, current_turn: int) -> List[Dict]:
        pending = []
        remaining = []
        
        for event in self.event_queue:
            if event['execute_turn'] <= current_turn:
                pending.append(event)
                self.event_history.append(event)
            else:
                remaining.append(event)
        
        self.event_queue = remaining
        return pending


class ProceduralSystem:
    
    def __init__(self, grid_width: int = 30, grid_height: int = 30, 
                 difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
                 seed: int = None):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.difficulty = difficulty
        
        self.hazard_generator = HazardGenerator(grid_width, grid_height, seed)
        self.pattern_generator = AdversaryPatternGenerator(difficulty)
        self.event_generator = ProceduralEventGenerator(grid_width, grid_height)
        
        self.current_turn = 0
        self.stats = {
            'hazards_generated': 0,
            'patterns_generated': 0,
            'events_triggered': 0
        }
    
    def initialize(self, initial_hazard_count: int = 5):
        for _ in range(initial_hazard_count):
            hazard_type = random.choice(list(HazardType))
            position = (
                random.randint(0, self.grid_width - 1),
                random.randint(0, self.grid_height - 1)
            )
            self.hazard_generator.generate_hazard_at(position, hazard_type, 0)
            self.stats['hazards_generated'] += 1
    
    def update(self, turn: int, game_state: Dict) -> Dict:
        self.current_turn = turn
        
        result = {
            'expired_hazards': [],
            'new_hazards': [],
            'events': [],
            'damage_map': {}
        }
        
        result['expired_hazards'] = self.hazard_generator.update_hazards(turn)
        
        spawn_chance = {
            DifficultyLevel.EASY: 0.05,
            DifficultyLevel.MEDIUM: 0.1,
            DifficultyLevel.HARD: 0.15,
            DifficultyLevel.NIGHTMARE: 0.25
        }[self.difficulty]
        
        if random.random() < spawn_chance:
            event = self.event_generator.generate_event(turn, game_state)
            if event:
                if event['type'] == 'hazard_spawn':
                    new_hazards = self.hazard_generator.generate_pattern(
                        event['pattern'],
                        event['center'],
                        event['hazard_type'],
                        event['count'],
                        event['spread'],
                        turn
                    )
                    result['new_hazards'].extend(new_hazards)
                    self.stats['hazards_generated'] += len(new_hazards)
                
                result['events'].append(event)
                self.stats['events_triggered'] += 1
        
        pending_events = self.event_generator.get_pending_events(turn)
        result['events'].extend(pending_events)
        
        return result
    
    def get_damage_at_position(self, position: Tuple[int, int]) -> int:
        return self.hazard_generator.calculate_damage_at(position)
    
    def get_hazards_near(self, position: Tuple[int, int], radius: int = 5) -> List[ProceduralHazard]:
        return self.hazard_generator.get_hazards_in_radius(position, radius)
    
    def generate_boss_patterns(self) -> Tuple[AdversaryPattern, AdversaryPattern]:
        phase1 = self.pattern_generator.generate_boss_pattern(1)
        phase2 = self.pattern_generator.generate_boss_pattern(2)
        self.stats['patterns_generated'] += 2
        return phase1, phase2
    
    def generate_enemy_pattern(self, enemy_type: str, behavior: str = 'balanced') -> AdversaryPattern:
        pattern = self.pattern_generator.generate_pattern(enemy_type, behavior)
        self.stats['patterns_generated'] += 1
        return pattern
    
    def get_stats(self) -> Dict:
        return {
            **self.stats,
            'active_hazards': len(self.hazard_generator.hazards),
            'pending_events': len(self.event_generator.event_queue),
            'difficulty': self.difficulty.name
        }
