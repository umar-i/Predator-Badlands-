from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import random
import math
import json


class StateType(Enum):
    HEALTH = "health"
    DISTANCE = "distance"
    ENEMY_COUNT = "enemy_count"
    STAMINA = "stamina"
    FORMATION = "formation"


class ActionSpace(Enum):
    ATTACK = 0
    RETREAT = 1
    HEAL = 2
    MOVE_TOWARDS = 3
    MOVE_AWAY = 4
    COORDINATE = 5
    DEFEND = 6
    FLANK = 7
    REST = 8
    SPECIAL = 9


@dataclass
class State:
    health_level: int
    enemy_distance: int
    enemy_count: int
    ally_nearby: bool
    stamina_level: int
    boss_phase: int = 1
    
    def to_tuple(self) -> Tuple:
        return (
            self.health_level,
            self.enemy_distance,
            self.enemy_count,
            1 if self.ally_nearby else 0,
            self.stamina_level,
            self.boss_phase
        )
    
    @staticmethod
    def discretize_health(health_pct: float) -> int:
        if health_pct >= 80:
            return 3
        elif health_pct >= 50:
            return 2
        elif health_pct >= 25:
            return 1
        return 0
    
    @staticmethod
    def discretize_distance(distance: float) -> int:
        if distance <= 1.5:
            return 0
        elif distance <= 4:
            return 1
        elif distance <= 8:
            return 2
        return 3
    
    @staticmethod
    def discretize_stamina(stamina_pct: float) -> int:
        if stamina_pct >= 70:
            return 2
        elif stamina_pct >= 30:
            return 1
        return 0
    
    @staticmethod
    def discretize_enemy_count(count: int) -> int:
        if count == 0:
            return 0
        elif count == 1:
            return 1
        elif count <= 3:
            return 2
        return 3


@dataclass
class Experience:
    state: State
    action: ActionSpace
    reward: float
    next_state: State
    done: bool


class RewardCalculator:
    
    REWARD_VALUES = {
        'kill_wildlife': 10.0,
        'kill_boss': 100.0,
        'damage_dealt': 0.5,
        'damage_taken': -0.3,
        'death': -100.0,
        'ally_death': -50.0,
        'heal_ally': 5.0,
        'collect_item': 3.0,
        'honour_gained': 2.0,
        'coordination_bonus': 8.0,
        'survive_turn': 0.1,
        'low_health_penalty': -1.0,
        'retreat_when_needed': 5.0,
        'unnecessary_retreat': -3.0
    }
    
    def __init__(self):
        self.cumulative_reward = 0.0
        self.reward_history = []
        
    def calculate_turn_reward(self, agent, prev_state: Dict, curr_state: Dict, action_taken: ActionSpace) -> float:
        reward = 0.0
        
        reward += self.REWARD_VALUES['survive_turn']
        
        health_change = curr_state.get('health', 0) - prev_state.get('health', 0)
        if health_change < 0:
            reward += abs(health_change) * self.REWARD_VALUES['damage_taken']
        
        if curr_state.get('kills', 0) > prev_state.get('kills', 0):
            kill_type = curr_state.get('last_kill_type', 'wildlife')
            if kill_type == 'boss':
                reward += self.REWARD_VALUES['kill_boss']
            else:
                reward += self.REWARD_VALUES['kill_wildlife']
        
        damage_dealt = curr_state.get('damage_dealt', 0) - prev_state.get('damage_dealt', 0)
        if damage_dealt > 0:
            reward += damage_dealt * self.REWARD_VALUES['damage_dealt']
        
        if curr_state.get('healed_ally', False):
            reward += self.REWARD_VALUES['heal_ally']
        
        if curr_state.get('coordinated_action', False):
            reward += self.REWARD_VALUES['coordination_bonus']
        
        honour_change = curr_state.get('honour', 0) - prev_state.get('honour', 0)
        if honour_change > 0:
            reward += honour_change * self.REWARD_VALUES['honour_gained']
        
        if curr_state.get('health_pct', 100) < 25:
            reward += self.REWARD_VALUES['low_health_penalty']
        
        if action_taken == ActionSpace.RETREAT:
            if prev_state.get('health_pct', 100) < 30:
                reward += self.REWARD_VALUES['retreat_when_needed']
            elif prev_state.get('health_pct', 100) > 70:
                reward += self.REWARD_VALUES['unnecessary_retreat']
        
        if not agent.is_alive:
            reward += self.REWARD_VALUES['death']
        
        self.cumulative_reward += reward
        self.reward_history.append(reward)
        
        if len(self.reward_history) > 1000:
            self.reward_history = self.reward_history[-1000:]
        
        return reward
    
    def get_average_reward(self, window: int = 100) -> float:
        if not self.reward_history:
            return 0.0
        recent = self.reward_history[-window:]
        return sum(recent) / len(recent)


class TabularQLearning:
    
    def __init__(self, 
                 learning_rate: float = 0.1,
                 discount_factor: float = 0.95,
                 exploration_rate: float = 0.3,
                 exploration_decay: float = 0.995,
                 min_exploration: float = 0.05):
        
        self.alpha = learning_rate
        self.gamma = discount_factor
        self.epsilon = exploration_rate
        self.epsilon_decay = exploration_decay
        self.epsilon_min = min_exploration
        
        self.q_table: Dict[Tuple, Dict[int, float]] = {}
        self.visit_counts: Dict[Tuple, int] = {}
        self.reward_calculator = RewardCalculator()
        
        self.experience_buffer: List[Experience] = []
        self.max_buffer_size = 500
        
        self.training_stats = {
            'episodes': 0,
            'total_updates': 0,
            'average_q_value': 0.0,
            'best_action_history': []
        }
    
    def get_state_from_environment(self, agent, enemies: List, ally=None) -> State:
        health_pct = (agent.health / agent.max_health) * 100 if agent.max_health > 0 else 0
        health_level = State.discretize_health(health_pct)
        
        stamina_pct = (agent.stamina / agent.max_stamina) * 100 if agent.max_stamina > 0 else 0
        stamina_level = State.discretize_stamina(stamina_pct)
        
        min_distance = 100.0
        boss_phase = 1
        for enemy in enemies:
            if enemy.is_alive:
                dist = math.sqrt((enemy.x - agent.x)**2 + (enemy.y - agent.y)**2)
                min_distance = min(min_distance, dist)
                if hasattr(enemy, 'phase'):
                    boss_phase = enemy.phase
        
        enemy_distance = State.discretize_distance(min_distance)
        enemy_count = State.discretize_enemy_count(len([e for e in enemies if e.is_alive]))
        
        ally_nearby = False
        if ally and ally.is_alive:
            ally_dist = math.sqrt((ally.x - agent.x)**2 + (ally.y - agent.y)**2)
            ally_nearby = ally_dist <= 4
        
        return State(
            health_level=health_level,
            enemy_distance=enemy_distance,
            enemy_count=enemy_count,
            ally_nearby=ally_nearby,
            stamina_level=stamina_level,
            boss_phase=boss_phase
        )
    
    def get_q_value(self, state: State, action: ActionSpace) -> float:
        state_key = state.to_tuple()
        if state_key not in self.q_table:
            self.q_table[state_key] = {a.value: 0.0 for a in ActionSpace}
        return self.q_table[state_key].get(action.value, 0.0)
    
    def get_max_q_value(self, state: State) -> float:
        state_key = state.to_tuple()
        if state_key not in self.q_table:
            return 0.0
        return max(self.q_table[state_key].values())
    
    def get_best_action(self, state: State) -> ActionSpace:
        state_key = state.to_tuple()
        if state_key not in self.q_table:
            self.q_table[state_key] = {a.value: 0.0 for a in ActionSpace}
        
        best_value = float('-inf')
        best_action = ActionSpace.ATTACK
        
        for action in ActionSpace:
            q_val = self.q_table[state_key].get(action.value, 0.0)
            if q_val > best_value:
                best_value = q_val
                best_action = action
        
        return best_action
    
    def select_action(self, state: State, valid_actions: List[ActionSpace] = None) -> ActionSpace:
        if valid_actions is None:
            valid_actions = list(ActionSpace)
        
        if random.random() < self.epsilon:
            return random.choice(valid_actions)
        
        best_action = None
        best_value = float('-inf')
        
        for action in valid_actions:
            q_val = self.get_q_value(state, action)
            if q_val > best_value:
                best_value = q_val
                best_action = action
        
        return best_action if best_action else random.choice(valid_actions)
    
    def update(self, state: State, action: ActionSpace, reward: float, next_state: State, done: bool = False):
        state_key = state.to_tuple()
        
        if state_key not in self.q_table:
            self.q_table[state_key] = {a.value: 0.0 for a in ActionSpace}
        
        current_q = self.q_table[state_key][action.value]
        
        if done:
            target = reward
        else:
            max_next_q = self.get_max_q_value(next_state)
            target = reward + self.gamma * max_next_q
        
        self.q_table[state_key][action.value] = current_q + self.alpha * (target - current_q)
        
        self.visit_counts[state_key] = self.visit_counts.get(state_key, 0) + 1
        
        self.training_stats['total_updates'] += 1
        self._update_average_q()
    
    def store_experience(self, experience: Experience):
        self.experience_buffer.append(experience)
        if len(self.experience_buffer) > self.max_buffer_size:
            self.experience_buffer.pop(0)
    
    def replay_experiences(self, batch_size: int = 32):
        if len(self.experience_buffer) < batch_size:
            return
        
        batch = random.sample(self.experience_buffer, batch_size)
        
        for exp in batch:
            self.update(exp.state, exp.action, exp.reward, exp.next_state, exp.done)
    
    def decay_exploration(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def _update_average_q(self):
        if not self.q_table:
            return
        
        total_q = 0.0
        count = 0
        for state_actions in self.q_table.values():
            for q_val in state_actions.values():
                total_q += q_val
                count += 1
        
        self.training_stats['average_q_value'] = total_q / count if count > 0 else 0.0
    
    def get_action_for_situation(self, state: State) -> ActionSpace:
        if state.health_level == 0:
            return ActionSpace.RETREAT
        
        if state.stamina_level == 0:
            return ActionSpace.REST
        
        return self.select_action(state)
    
    def save_q_table(self, filepath: str):
        serializable = {}
        for state_key, actions in self.q_table.items():
            serializable[str(state_key)] = actions
        
        with open(filepath, 'w') as f:
            json.dump({
                'q_table': serializable,
                'epsilon': self.epsilon,
                'stats': self.training_stats
            }, f)
    
    def load_q_table(self, filepath: str):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.q_table = {}
            for state_str, actions in data['q_table'].items():
                state_key = eval(state_str)
                self.q_table[state_key] = {int(k): v for k, v in actions.items()}
            
            self.epsilon = data.get('epsilon', self.epsilon)
            self.training_stats = data.get('stats', self.training_stats)
        except FileNotFoundError:
            pass
    
    def get_policy_summary(self) -> Dict:
        policy = {}
        for state_key, actions in self.q_table.items():
            best_action = max(actions.keys(), key=lambda a: actions[a])
            policy[state_key] = ActionSpace(best_action).name
        return policy


class ThiaLearning(TabularQLearning):
    
    def __init__(self):
        super().__init__(
            learning_rate=0.15,
            discount_factor=0.9,
            exploration_rate=0.2,
            exploration_decay=0.99,
            min_exploration=0.03
        )
        
        self.support_q_table: Dict[Tuple, Dict[int, float]] = {}
        self.partner_state_memory = []
    
    def get_support_action(self, own_state: State, partner_state: State) -> ActionSpace:
        combined_key = (own_state.to_tuple(), partner_state.to_tuple())
        
        if combined_key not in self.support_q_table:
            self.support_q_table[combined_key] = {a.value: 0.0 for a in ActionSpace}
        
        if partner_state.health_level <= 1:
            return ActionSpace.HEAL
        
        if partner_state.enemy_distance == 0 and partner_state.enemy_count > 0:
            return ActionSpace.COORDINATE
        
        if random.random() < self.epsilon:
            support_actions = [ActionSpace.HEAL, ActionSpace.COORDINATE, ActionSpace.DEFEND, ActionSpace.MOVE_TOWARDS]
            return random.choice(support_actions)
        
        best_action = max(
            self.support_q_table[combined_key].keys(),
            key=lambda a: self.support_q_table[combined_key][a]
        )
        
        return ActionSpace(best_action)
    
    def update_support_learning(self, own_state: State, partner_state: State, 
                                action: ActionSpace, reward: float,
                                next_own_state: State, next_partner_state: State):
        combined_key = (own_state.to_tuple(), partner_state.to_tuple())
        next_combined_key = (next_own_state.to_tuple(), next_partner_state.to_tuple())
        
        if combined_key not in self.support_q_table:
            self.support_q_table[combined_key] = {a.value: 0.0 for a in ActionSpace}
        if next_combined_key not in self.support_q_table:
            self.support_q_table[next_combined_key] = {a.value: 0.0 for a in ActionSpace}
        
        current_q = self.support_q_table[combined_key][action.value]
        max_next_q = max(self.support_q_table[next_combined_key].values())
        
        target = reward + self.gamma * max_next_q
        self.support_q_table[combined_key][action.value] = current_q + self.alpha * (target - current_q)


class BossPatternType(Enum):
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    TERRITORIAL = "territorial"
    PURSUIT = "pursuit"
    AMBUSH = "ambush"
    BERSERK = "berserk"


@dataclass
class BossPattern:
    pattern_type: BossPatternType
    duration: int
    attack_modifier: float = 1.0
    defense_modifier: float = 1.0
    speed_modifier: float = 1.0
    ability_cooldown_modifier: float = 1.0
    priority_target: str = None


class AdaptiveBossAI:
    
    def __init__(self, boss_agent):
        self.boss = boss_agent
        self.current_pattern = BossPattern(BossPatternType.TERRITORIAL, 10)
        self.pattern_history = []
        self.player_behavior_memory = []
        self.damage_received_sources = {}
        self.successful_attacks = []
        self.failed_attacks = []
        self.adaptation_level = 0.0
        self.turn_counter = 0
        self.pattern_change_cooldown = 0
        
        self.player_tendencies = {
            'aggression': 0.5,
            'evasion': 0.5,
            'healing_frequency': 0.0,
            'coordination_level': 0.0,
            'average_distance': 5.0
        }
    
    def observe_player_action(self, player, action_type: str, result: bool):
        observation = {
            'turn': self.turn_counter,
            'action': action_type,
            'success': result,
            'player_health': player.health_percentage if hasattr(player, 'health_percentage') else 50,
            'distance': math.sqrt((player.x - self.boss.x)**2 + (player.y - self.boss.y)**2)
        }
        
        self.player_behavior_memory.append(observation)
        
        if len(self.player_behavior_memory) > 50:
            self.player_behavior_memory = self.player_behavior_memory[-50:]
        
        self._update_player_tendencies()
    
    def _update_player_tendencies(self):
        if len(self.player_behavior_memory) < 5:
            return
        
        recent = self.player_behavior_memory[-20:]
        
        attack_actions = sum(1 for o in recent if 'attack' in o['action'].lower())
        self.player_tendencies['aggression'] = attack_actions / len(recent)
        
        retreat_actions = sum(1 for o in recent if 'retreat' in o['action'].lower() or 'flee' in o['action'].lower())
        self.player_tendencies['evasion'] = retreat_actions / len(recent)
        
        heal_actions = sum(1 for o in recent if 'heal' in o['action'].lower())
        self.player_tendencies['healing_frequency'] = heal_actions / len(recent)
        
        coord_actions = sum(1 for o in recent if 'coordinate' in o['action'].lower() or 'sync' in o['action'].lower())
        self.player_tendencies['coordination_level'] = coord_actions / len(recent)
        
        if recent:
            self.player_tendencies['average_distance'] = sum(o['distance'] for o in recent) / len(recent)
    
    def record_damage_source(self, attacker, damage: int):
        attacker_id = attacker.name if hasattr(attacker, 'name') else str(id(attacker))
        
        if attacker_id not in self.damage_received_sources:
            self.damage_received_sources[attacker_id] = {
                'total_damage': 0,
                'attack_count': 0,
                'last_position': (attacker.x, attacker.y)
            }
        
        self.damage_received_sources[attacker_id]['total_damage'] += damage
        self.damage_received_sources[attacker_id]['attack_count'] += 1
        self.damage_received_sources[attacker_id]['last_position'] = (attacker.x, attacker.y)
        
        self._consider_pattern_change()
    
    def record_attack_result(self, target, damage: int, success: bool):
        result = {
            'turn': self.turn_counter,
            'target': target.name if hasattr(target, 'name') else str(id(target)),
            'damage': damage,
            'success': success
        }
        
        if success:
            self.successful_attacks.append(result)
        else:
            self.failed_attacks.append(result)
        
        if len(self.successful_attacks) > 30:
            self.successful_attacks = self.successful_attacks[-30:]
        if len(self.failed_attacks) > 30:
            self.failed_attacks = self.failed_attacks[-30:]
    
    def _consider_pattern_change(self):
        if self.pattern_change_cooldown > 0:
            return
        
        new_pattern = self._select_adaptive_pattern()
        
        if new_pattern.pattern_type != self.current_pattern.pattern_type:
            self.pattern_history.append(self.current_pattern)
            self.current_pattern = new_pattern
            self.pattern_change_cooldown = 5
            self.adaptation_level = min(1.0, self.adaptation_level + 0.1)
    
    def _select_adaptive_pattern(self) -> BossPattern:
        health_pct = self.boss.health / self.boss.max_health if self.boss.max_health > 0 else 0
        
        if health_pct < 0.2:
            return BossPattern(
                BossPatternType.BERSERK,
                duration=15,
                attack_modifier=2.0,
                defense_modifier=0.5,
                speed_modifier=1.5,
                ability_cooldown_modifier=0.5
            )
        
        if self.player_tendencies['aggression'] > 0.6:
            return BossPattern(
                BossPatternType.DEFENSIVE,
                duration=10,
                attack_modifier=0.8,
                defense_modifier=1.5,
                speed_modifier=0.8,
                ability_cooldown_modifier=1.2
            )
        
        if self.player_tendencies['evasion'] > 0.5:
            return BossPattern(
                BossPatternType.PURSUIT,
                duration=12,
                attack_modifier=1.2,
                defense_modifier=0.9,
                speed_modifier=1.8,
                ability_cooldown_modifier=1.0
            )
        
        if self.player_tendencies['coordination_level'] > 0.4:
            highest_threat = self._get_highest_threat_player()
            return BossPattern(
                BossPatternType.AGGRESSIVE,
                duration=8,
                attack_modifier=1.5,
                defense_modifier=1.0,
                speed_modifier=1.2,
                priority_target=highest_threat
            )
        
        if self.player_tendencies['average_distance'] > 6:
            return BossPattern(
                BossPatternType.AMBUSH,
                duration=10,
                attack_modifier=1.8,
                defense_modifier=0.8,
                speed_modifier=1.0,
                ability_cooldown_modifier=0.8
            )
        
        return BossPattern(
            BossPatternType.TERRITORIAL,
            duration=10,
            attack_modifier=1.0,
            defense_modifier=1.0,
            speed_modifier=1.0
        )
    
    def _get_highest_threat_player(self) -> Optional[str]:
        if not self.damage_received_sources:
            return None
        
        highest_damage = 0
        highest_threat = None
        
        for attacker_id, data in self.damage_received_sources.items():
            if data['total_damage'] > highest_damage:
                highest_damage = data['total_damage']
                highest_threat = attacker_id
        
        return highest_threat
    
    def get_adaptive_action(self, enemies: List, grid) -> Dict:
        self.turn_counter += 1
        self.pattern_change_cooldown = max(0, self.pattern_change_cooldown - 1)
        
        if self.current_pattern.duration <= 0:
            self._consider_pattern_change()
        else:
            self.current_pattern.duration -= 1
        
        pattern = self.current_pattern
        
        action = {
            'type': 'idle',
            'target': None,
            'damage_modifier': pattern.attack_modifier,
            'defense_modifier': pattern.defense_modifier
        }
        
        if pattern.pattern_type == BossPatternType.AGGRESSIVE:
            action = self._aggressive_behavior(enemies)
        elif pattern.pattern_type == BossPatternType.DEFENSIVE:
            action = self._defensive_behavior(enemies, grid)
        elif pattern.pattern_type == BossPatternType.TERRITORIAL:
            action = self._territorial_behavior(enemies, grid)
        elif pattern.pattern_type == BossPatternType.PURSUIT:
            action = self._pursuit_behavior(enemies, grid)
        elif pattern.pattern_type == BossPatternType.AMBUSH:
            action = self._ambush_behavior(enemies, grid)
        elif pattern.pattern_type == BossPatternType.BERSERK:
            action = self._berserk_behavior(enemies)
        
        action['damage_modifier'] = pattern.attack_modifier
        action['defense_modifier'] = pattern.defense_modifier
        
        return action
    
    def _aggressive_behavior(self, enemies: List) -> Dict:
        if not enemies:
            return {'type': 'patrol', 'target': None}
        
        priority_target = None
        if self.current_pattern.priority_target:
            for enemy in enemies:
                if hasattr(enemy, 'name') and enemy.name == self.current_pattern.priority_target:
                    priority_target = enemy
                    break
        
        if not priority_target:
            priority_target = min(enemies, key=lambda e: e.health if e.is_alive else float('inf'))
        
        distance = math.sqrt(
            (priority_target.x - self.boss.x)**2 + 
            (priority_target.y - self.boss.y)**2
        )
        
        if distance <= self.boss.attack_range:
            return {'type': 'attack', 'target': priority_target}
        else:
            return {'type': 'move_towards', 'target': priority_target}
    
    def _defensive_behavior(self, enemies: List, grid) -> Dict:
        if not enemies:
            return {'type': 'regenerate', 'target': None}
        
        nearest = min(enemies, key=lambda e: math.sqrt((e.x - self.boss.x)**2 + (e.y - self.boss.y)**2))
        distance = math.sqrt((nearest.x - self.boss.x)**2 + (nearest.y - self.boss.y)**2)
        
        if distance <= 1.5:
            return {'type': 'attack', 'target': nearest}
        
        if self.boss.health < self.boss.max_health * 0.5:
            return {'type': 'regenerate', 'target': None}
        
        return {'type': 'defend', 'target': None}
    
    def _territorial_behavior(self, enemies: List, grid) -> Dict:
        territory_center = self.boss.territory_center
        territory_radius = self.boss.territory_radius
        
        intruders = []
        for enemy in enemies:
            if enemy.is_alive:
                dist_to_center = math.sqrt(
                    (enemy.x - territory_center[0])**2 + 
                    (enemy.y - territory_center[1])**2
                )
                if dist_to_center <= territory_radius:
                    intruders.append(enemy)
        
        if intruders:
            target = min(intruders, key=lambda e: math.sqrt((e.x - self.boss.x)**2 + (e.y - self.boss.y)**2))
            distance = math.sqrt((target.x - self.boss.x)**2 + (target.y - self.boss.y)**2)
            
            if distance <= self.boss.attack_range:
                return {'type': 'attack', 'target': target}
            else:
                return {'type': 'move_towards', 'target': target}
        
        dist_to_center = math.sqrt(
            (self.boss.x - territory_center[0])**2 + 
            (self.boss.y - territory_center[1])**2
        )
        
        if dist_to_center > territory_radius * 0.5:
            return {'type': 'return_to_territory', 'target': territory_center}
        
        return {'type': 'patrol', 'target': None}
    
    def _pursuit_behavior(self, enemies: List, grid) -> Dict:
        if not enemies:
            return {'type': 'patrol', 'target': None}
        
        weakest = min(enemies, key=lambda e: e.health if e.is_alive else float('inf'))
        
        distance = math.sqrt((weakest.x - self.boss.x)**2 + (weakest.y - self.boss.y)**2)
        
        if distance <= self.boss.attack_range:
            return {'type': 'attack', 'target': weakest}
        else:
            return {'type': 'move_towards', 'target': weakest, 'speed': 2}
    
    def _ambush_behavior(self, enemies: List, grid) -> Dict:
        if not enemies:
            return {'type': 'hide', 'target': None}
        
        nearest = min(enemies, key=lambda e: math.sqrt((e.x - self.boss.x)**2 + (e.y - self.boss.y)**2))
        distance = math.sqrt((nearest.x - self.boss.x)**2 + (nearest.y - self.boss.y)**2)
        
        if distance <= 2:
            return {'type': 'ambush_attack', 'target': nearest, 'damage_bonus': 1.5}
        
        if distance <= 5:
            return {'type': 'wait', 'target': None}
        
        return {'type': 'move_towards', 'target': nearest}
    
    def _berserk_behavior(self, enemies: List) -> Dict:
        if not enemies:
            return {'type': 'rage', 'target': None}
        
        if random.random() < 0.3:
            return {'type': 'special_attack', 'target': enemies, 'aoe': True}
        
        target = random.choice(enemies)
        return {'type': 'berserk_attack', 'target': target, 'damage_bonus': 2.0}
    
    def execute_adaptive_action(self, action: Dict, grid):
        action_type = action.get('type', 'idle')
        target = action.get('target')
        damage_modifier = action.get('damage_modifier', 1.0)
        
        if action_type == 'attack':
            if target and target.is_alive:
                base_damage = random.randint(30, 45)
                if self.boss.phase == 2:
                    base_damage = random.randint(40, 60)
                
                final_damage = int(base_damage * damage_modifier)
                target.take_damage(final_damage)
                self.record_attack_result(target, final_damage, True)
                return True
        
        elif action_type == 'ambush_attack':
            if target and target.is_alive:
                base_damage = random.randint(40, 55)
                damage_bonus = action.get('damage_bonus', 1.5)
                final_damage = int(base_damage * damage_modifier * damage_bonus)
                target.take_damage(final_damage)
                self.record_attack_result(target, final_damage, True)
                return True
        
        elif action_type == 'berserk_attack':
            if target and target.is_alive:
                base_damage = random.randint(50, 70)
                damage_bonus = action.get('damage_bonus', 2.0)
                final_damage = int(base_damage * damage_modifier * damage_bonus)
                target.take_damage(final_damage)
                return True
        
        elif action_type == 'special_attack':
            targets = action.get('target', [])
            if action.get('aoe', False):
                for t in targets:
                    if t.is_alive:
                        damage = random.randint(25, 40)
                        t.take_damage(int(damage * damage_modifier))
                return True
        
        elif action_type == 'move_towards':
            if target:
                self._move_boss_towards(target, grid, action.get('speed', 1))
                return True
        
        elif action_type == 'return_to_territory':
            if target:
                self._move_boss_to_position(target, grid)
                return True
        
        elif action_type == 'regenerate':
            heal_amount = min(30, self.boss.max_health - self.boss.health)
            self.boss.heal(heal_amount)
            return True
        
        elif action_type == 'patrol':
            self._patrol(grid)
            return True
        
        return False
    
    def _move_boss_towards(self, target, grid, speed: int = 1):
        if not grid:
            return
        
        for _ in range(speed):
            best_move = None
            best_distance = float('inf')
            
            target_x = target.x if hasattr(target, 'x') else target[0]
            target_y = target.y if hasattr(target, 'y') else target[1]
            
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    new_x, new_y = grid.wrap_coordinates(self.boss.x + dx, self.boss.y + dy)
                    dist = math.sqrt((new_x - target_x)**2 + (new_y - target_y)**2)
                    if dist < best_distance:
                        best_distance = dist
                        best_move = (new_x, new_y)
            
            if best_move:
                self.boss.move_to(best_move[0], best_move[1])
    
    def _move_boss_to_position(self, position: Tuple[int, int], grid):
        self._move_boss_towards(position, grid)
    
    def _patrol(self, grid):
        if not grid:
            return
        
        valid_moves = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = grid.wrap_coordinates(self.boss.x + dx, self.boss.y + dy)
                dist_to_center = math.sqrt(
                    (new_x - self.boss.territory_center[0])**2 + 
                    (new_y - self.boss.territory_center[1])**2
                )
                if dist_to_center <= self.boss.territory_radius:
                    valid_moves.append((new_x, new_y))
        
        if valid_moves:
            target = random.choice(valid_moves)
            self.boss.move_to(target[0], target[1])
    
    def get_adaptation_stats(self) -> Dict:
        return {
            'current_pattern': self.current_pattern.pattern_type.value,
            'pattern_duration': self.current_pattern.duration,
            'adaptation_level': self.adaptation_level,
            'player_tendencies': self.player_tendencies.copy(),
            'patterns_used': len(self.pattern_history),
            'successful_attacks': len(self.successful_attacks),
            'failed_attacks': len(self.failed_attacks),
            'turn_counter': self.turn_counter
        }


class LearningSystem:
    
    def __init__(self):
        self.dek_learning = TabularQLearning()
        self.thia_learning = ThiaLearning()
        self.boss_ai = None
        self.turn_count = 0
        self.episode_rewards = []
    
    def initialize_boss_ai(self, boss_agent):
        self.boss_ai = AdaptiveBossAI(boss_agent)
    
    def get_dek_action(self, dek, enemies: List, thia=None) -> ActionSpace:
        state = self.dek_learning.get_state_from_environment(dek, enemies, thia)
        return self.dek_learning.select_action(state)
    
    def get_thia_action(self, thia, dek, enemies: List) -> ActionSpace:
        own_state = self.thia_learning.get_state_from_environment(thia, enemies, dek)
        partner_state = self.thia_learning.get_state_from_environment(dek, enemies, thia)
        return self.thia_learning.get_support_action(own_state, partner_state)
    
    def get_boss_action(self, enemies: List, grid) -> Dict:
        if self.boss_ai:
            return self.boss_ai.get_adaptive_action(enemies, grid)
        return {'type': 'idle', 'target': None}
    
    def update_dek_learning(self, dek, prev_state: Dict, curr_state: Dict, 
                           action: ActionSpace, enemies: List, thia=None):
        state_before = self.dek_learning.get_state_from_environment(dek, enemies, thia)
        state_after = self.dek_learning.get_state_from_environment(dek, enemies, thia)
        
        reward = self.dek_learning.reward_calculator.calculate_turn_reward(
            dek, prev_state, curr_state, action
        )
        
        done = not dek.is_alive or curr_state.get('boss_defeated', False)
        
        self.dek_learning.update(state_before, action, reward, state_after, done)
        
        experience = Experience(state_before, action, reward, state_after, done)
        self.dek_learning.store_experience(experience)
    
    def update_thia_learning(self, thia, dek, prev_state: Dict, curr_state: Dict,
                            action: ActionSpace, enemies: List):
        own_state = self.thia_learning.get_state_from_environment(thia, enemies, dek)
        partner_state = self.thia_learning.get_state_from_environment(dek, enemies, thia)
        
        next_own = self.thia_learning.get_state_from_environment(thia, enemies, dek)
        next_partner = self.thia_learning.get_state_from_environment(dek, enemies, thia)
        
        reward = self.thia_learning.reward_calculator.calculate_turn_reward(
            thia, prev_state, curr_state, action
        )
        
        if dek.health > prev_state.get('partner_health', 0):
            reward += 10
        
        self.thia_learning.update_support_learning(
            own_state, partner_state, action, reward, next_own, next_partner
        )
    
    def end_episode(self):
        total_reward = self.dek_learning.reward_calculator.cumulative_reward
        self.episode_rewards.append(total_reward)
        
        self.dek_learning.decay_exploration()
        self.thia_learning.decay_exploration()
        
        self.dek_learning.replay_experiences()
        self.thia_learning.replay_experiences()
        
        self.dek_learning.training_stats['episodes'] += 1
        self.thia_learning.training_stats['episodes'] += 1
    
    def get_learning_stats(self) -> Dict:
        stats = {
            'dek_stats': {
                'q_table_size': len(self.dek_learning.q_table),
                'exploration_rate': self.dek_learning.epsilon,
                'average_q': self.dek_learning.training_stats['average_q_value'],
                'total_updates': self.dek_learning.training_stats['total_updates'],
                'episodes': self.dek_learning.training_stats['episodes']
            },
            'thia_stats': {
                'q_table_size': len(self.thia_learning.q_table),
                'support_table_size': len(self.thia_learning.support_q_table),
                'exploration_rate': self.thia_learning.epsilon,
                'episodes': self.thia_learning.training_stats['episodes']
            },
            'episode_rewards': self.episode_rewards[-10:] if self.episode_rewards else []
        }
        
        if self.boss_ai:
            stats['boss_stats'] = self.boss_ai.get_adaptation_stats()
        
        return stats
    
    def save_learning_data(self, base_path: str):
        self.dek_learning.save_q_table(f"{base_path}/dek_q_table.json")
        self.thia_learning.save_q_table(f"{base_path}/thia_q_table.json")
    
    def load_learning_data(self, base_path: str):
        self.dek_learning.load_q_table(f"{base_path}/dek_q_table.json")
        self.thia_learning.load_q_table(f"{base_path}/thia_q_table.json")
