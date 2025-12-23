from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Any
import random
import math


class Role(Enum):
    LEADER = "leader"
    SUPPORT = "support"
    SCOUT = "scout"
    TANK = "tank"
    HEALER = "healer"
    ATTACKER = "attacker"


class GoalType(Enum):
    SURVIVE = "survive"
    HUNT_TARGET = "hunt_target"
    PROTECT_ALLY = "protect_ally"
    COLLECT_ITEM = "collect_item"
    REACH_POSITION = "reach_position"
    ESCAPE_DANGER = "escape_danger"
    DEFEAT_BOSS = "defeat_boss"
    HEAL_ALLY = "heal_ally"
    COVER_ALLY = "cover_ally"
    FLANK_ENEMY = "flank_enemy"


class ActionPriority(Enum):
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class SharedGoal:
    goal_type: GoalType
    priority: ActionPriority
    target: Any = None
    position: Tuple[int, int] = None
    assigned_agents: List[str] = None
    progress: float = 0.0
    completed: bool = False
    
    def __post_init__(self):
        if self.assigned_agents is None:
            self.assigned_agents = []


@dataclass
class CoordinatedAction:
    agent_name: str
    action_type: str
    target: Any = None
    position: Tuple[int, int] = None
    priority: ActionPriority = ActionPriority.MEDIUM
    requires_sync: bool = False
    sync_with: List[str] = None
    
    def __post_init__(self):
        if self.sync_with is None:
            self.sync_with = []


class ThreatAssessment:
    
    def __init__(self):
        self.threat_levels = {}
        self.threat_history = []
        self.danger_zones = set()
        
    def assess_threat(self, enemy, observer_position: Tuple[int, int]) -> float:
        if not enemy or not enemy.is_alive:
            return 0.0
        
        distance = math.sqrt(
            (enemy.x - observer_position[0])**2 + 
            (enemy.y - observer_position[1])**2
        )
        
        base_threat = 0.0
        
        if hasattr(enemy, 'phase'):
            base_threat = 100.0 if enemy.phase == 2 else 80.0
        elif hasattr(enemy, 'is_enraged') and enemy.is_enraged:
            base_threat = 60.0
        elif hasattr(enemy, 'aggression_level'):
            base_threat = 30.0 + enemy.aggression_level * 20
        else:
            base_threat = 20.0
        
        health_factor = enemy.health / enemy.max_health if hasattr(enemy, 'max_health') else 0.5
        
        distance_modifier = max(0.1, 1.0 - (distance / 15.0))
        
        threat_score = base_threat * health_factor * distance_modifier
        
        enemy_id = id(enemy)
        self.threat_levels[enemy_id] = threat_score
        self.threat_history.append((enemy_id, threat_score))
        
        if len(self.threat_history) > 100:
            self.threat_history = self.threat_history[-100:]
        
        return threat_score
    
    def get_highest_threat(self, enemies: List, observer_position: Tuple[int, int]):
        if not enemies:
            return None, 0.0
        
        max_threat = 0.0
        highest_threat_enemy = None
        
        for enemy in enemies:
            threat = self.assess_threat(enemy, observer_position)
            if threat > max_threat:
                max_threat = threat
                highest_threat_enemy = enemy
        
        return highest_threat_enemy, max_threat
    
    def mark_danger_zone(self, position: Tuple[int, int], radius: int = 2):
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                self.danger_zones.add((position[0] + dx, position[1] + dy))
    
    def is_position_dangerous(self, position: Tuple[int, int]) -> bool:
        return position in self.danger_zones
    
    def clear_danger_zones(self):
        self.danger_zones.clear()


class SharedGoalPlanner:
    
    def __init__(self):
        self.goals = []
        self.completed_goals = []
        self.goal_history = []
        self.agents = {}
        self.threat_assessment = ThreatAssessment()
        
    def register_agent(self, agent, role: Role):
        self.agents[agent.name] = {
            'agent': agent,
            'role': role,
            'current_goal': None,
            'action_queue': []
        }
    
    def add_goal(self, goal: SharedGoal):
        for existing in self.goals:
            if existing.goal_type == goal.goal_type and existing.target == goal.target:
                if goal.priority.value < existing.priority.value:
                    existing.priority = goal.priority
                return
        
        self.goals.append(goal)
        self._sort_goals()
    
    def _sort_goals(self):
        self.goals.sort(key=lambda g: (g.priority.value, -g.progress))
    
    def remove_goal(self, goal: SharedGoal):
        if goal in self.goals:
            self.goals.remove(goal)
            self.completed_goals.append(goal)
            self.goal_history.append(goal)
    
    def get_active_goals(self) -> List[SharedGoal]:
        return [g for g in self.goals if not g.completed]
    
    def assign_goal(self, goal: SharedGoal, agent_name: str):
        if agent_name not in goal.assigned_agents:
            goal.assigned_agents.append(agent_name)
        
        if agent_name in self.agents:
            self.agents[agent_name]['current_goal'] = goal
    
    def evaluate_situation(self, dek, thia, enemies: List, grid) -> List[SharedGoal]:
        new_goals = []
        
        if dek.health < dek.max_health * 0.3:
            new_goals.append(SharedGoal(
                goal_type=GoalType.SURVIVE,
                priority=ActionPriority.CRITICAL,
                assigned_agents=[dek.name]
            ))
        
        if thia and thia.is_alive and thia.health < thia.max_health * 0.4:
            new_goals.append(SharedGoal(
                goal_type=GoalType.HEAL_ALLY,
                priority=ActionPriority.HIGH,
                target=thia,
                assigned_agents=[dek.name]
            ))
        
        if enemies:
            highest_threat, threat_level = self.threat_assessment.get_highest_threat(
                enemies, (dek.x, dek.y)
            )
            
            if highest_threat:
                if threat_level > 70:
                    new_goals.append(SharedGoal(
                        goal_type=GoalType.DEFEAT_BOSS,
                        priority=ActionPriority.HIGH,
                        target=highest_threat,
                        assigned_agents=[dek.name, thia.name if thia else None]
                    ))
                elif threat_level > 30:
                    new_goals.append(SharedGoal(
                        goal_type=GoalType.HUNT_TARGET,
                        priority=ActionPriority.MEDIUM,
                        target=highest_threat,
                        assigned_agents=[dek.name]
                    ))
        
        for goal in new_goals:
            self.add_goal(goal)
        
        return new_goals
    
    def update_goal_progress(self, goal: SharedGoal, progress_delta: float):
        goal.progress = min(1.0, goal.progress + progress_delta)
        
        if goal.progress >= 1.0:
            goal.completed = True
            self.remove_goal(goal)
    
    def get_agent_goal(self, agent_name: str) -> Optional[SharedGoal]:
        if agent_name in self.agents:
            return self.agents[agent_name]['current_goal']
        return None


class RoleManager:
    
    ROLE_CAPABILITIES = {
        Role.LEADER: {
            'can_command': True,
            'priority_actions': ['coordinate', 'attack', 'strategize'],
            'stat_bonus': {'damage': 1.1, 'honour': 1.2}
        },
        Role.SUPPORT: {
            'can_heal': True,
            'priority_actions': ['heal', 'buff', 'scan'],
            'stat_bonus': {'healing': 1.3, 'scan_range': 1.5}
        },
        Role.SCOUT: {
            'can_scout': True,
            'priority_actions': ['scan', 'move', 'report'],
            'stat_bonus': {'speed': 1.3, 'detection': 1.5}
        },
        Role.TANK: {
            'can_absorb': True,
            'priority_actions': ['block', 'taunt', 'defend'],
            'stat_bonus': {'health': 1.3, 'armor': 1.2}
        },
        Role.HEALER: {
            'can_heal': True,
            'priority_actions': ['heal', 'restore', 'protect'],
            'stat_bonus': {'healing': 1.5, 'support': 1.3}
        },
        Role.ATTACKER: {
            'can_attack': True,
            'priority_actions': ['attack', 'flank', 'charge'],
            'stat_bonus': {'damage': 1.4, 'critical': 1.2}
        }
    }
    
    def __init__(self):
        self.agent_roles = {}
        self.role_assignments_history = []
        
    def assign_role(self, agent, role: Role):
        self.agent_roles[agent.name] = {
            'role': role,
            'capabilities': self.ROLE_CAPABILITIES[role],
            'effectiveness': 1.0
        }
        self.role_assignments_history.append((agent.name, role))
    
    def get_role(self, agent_name: str) -> Optional[Role]:
        if agent_name in self.agent_roles:
            return self.agent_roles[agent_name]['role']
        return None
    
    def get_capabilities(self, agent_name: str) -> Dict:
        if agent_name in self.agent_roles:
            return self.agent_roles[agent_name]['capabilities']
        return {}
    
    def get_stat_bonus(self, agent_name: str, stat: str) -> float:
        if agent_name in self.agent_roles:
            bonuses = self.agent_roles[agent_name]['capabilities'].get('stat_bonus', {})
            return bonuses.get(stat, 1.0)
        return 1.0
    
    def can_perform(self, agent_name: str, action: str) -> bool:
        if agent_name not in self.agent_roles:
            return True
        
        capabilities = self.agent_roles[agent_name]['capabilities']
        priority_actions = capabilities.get('priority_actions', [])
        
        return action in priority_actions or len(priority_actions) == 0
    
    def recommend_action(self, agent_name: str, available_actions: List[str]) -> str:
        if agent_name not in self.agent_roles:
            return available_actions[0] if available_actions else None
        
        priority_actions = self.agent_roles[agent_name]['capabilities'].get('priority_actions', [])
        
        for action in priority_actions:
            if action in available_actions:
                return action
        
        return available_actions[0] if available_actions else None
    
    def evaluate_role_effectiveness(self, agent, recent_actions: List[str]) -> float:
        if agent.name not in self.agent_roles:
            return 1.0
        
        role_data = self.agent_roles[agent.name]
        priority_actions = role_data['capabilities'].get('priority_actions', [])
        
        if not recent_actions:
            return 1.0
        
        matching_actions = sum(1 for a in recent_actions if a in priority_actions)
        effectiveness = matching_actions / len(recent_actions) if recent_actions else 1.0
        
        role_data['effectiveness'] = effectiveness
        return effectiveness


class FormationManager:
    
    FORMATIONS = {
        'defensive': {
            'leader_offset': (0, 0),
            'support_offset': (-1, 1),
            'spacing': 2
        },
        'aggressive': {
            'leader_offset': (1, 0),
            'support_offset': (0, 0),
            'spacing': 1
        },
        'flanking': {
            'leader_offset': (0, 2),
            'support_offset': (0, -2),
            'spacing': 4
        },
        'retreat': {
            'leader_offset': (-1, 0),
            'support_offset': (-2, 0),
            'spacing': 1
        },
        'surround': {
            'leader_offset': (2, 0),
            'support_offset': (-2, 0),
            'spacing': 4
        }
    }
    
    def __init__(self):
        self.current_formation = 'defensive'
        self.formation_history = []
        
    def set_formation(self, formation_name: str):
        if formation_name in self.FORMATIONS:
            self.current_formation = formation_name
            self.formation_history.append(formation_name)
    
    def get_formation_positions(self, leader_pos: Tuple[int, int], target_pos: Tuple[int, int] = None) -> Dict[str, Tuple[int, int]]:
        formation = self.FORMATIONS[self.current_formation]
        
        if target_pos:
            dx = target_pos[0] - leader_pos[0]
            dy = target_pos[1] - leader_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            if distance > 0:
                dx, dy = dx/distance, dy/distance
            else:
                dx, dy = 1, 0
        else:
            dx, dy = 1, 0
        
        leader_offset = formation['leader_offset']
        support_offset = formation['support_offset']
        
        positions = {
            'leader': (
                leader_pos[0] + int(leader_offset[0] * dx - leader_offset[1] * dy),
                leader_pos[1] + int(leader_offset[0] * dy + leader_offset[1] * dx)
            ),
            'support': (
                leader_pos[0] + int(support_offset[0] * dx - support_offset[1] * dy),
                leader_pos[1] + int(support_offset[0] * dy + support_offset[1] * dx)
            )
        }
        
        return positions
    
    def recommend_formation(self, situation: Dict) -> str:
        leader_health = situation.get('leader_health', 100)
        support_health = situation.get('support_health', 100)
        enemy_count = situation.get('enemy_count', 0)
        enemy_distance = situation.get('enemy_distance', 10)
        boss_present = situation.get('boss_present', False)
        
        if leader_health < 30 or support_health < 30:
            return 'retreat'
        
        if boss_present:
            if enemy_distance < 3:
                return 'flanking'
            else:
                return 'surround'
        
        if enemy_count > 2:
            return 'defensive'
        
        if enemy_distance < 5:
            return 'aggressive'
        
        return 'defensive'


class CoordinationProtocol:
    
    def __init__(self):
        self.goal_planner = SharedGoalPlanner()
        self.role_manager = RoleManager()
        self.formation_manager = FormationManager()
        self.action_queue = []
        self.sync_actions = []
        self.communication_log = []
        self.coordination_score = 0.0
        
    def initialize(self, dek, thia):
        self.goal_planner.register_agent(dek, Role.LEADER)
        self.role_manager.assign_role(dek, Role.LEADER)
        
        if thia:
            self.goal_planner.register_agent(thia, Role.SUPPORT)
            self.role_manager.assign_role(thia, Role.SUPPORT)
    
    def communicate(self, sender, receiver, message_type: str, data: Any = None):
        comm = {
            'sender': sender.name if hasattr(sender, 'name') else str(sender),
            'receiver': receiver.name if hasattr(receiver, 'name') else str(receiver),
            'type': message_type,
            'data': data
        }
        self.communication_log.append(comm)
        
        if len(self.communication_log) > 50:
            self.communication_log = self.communication_log[-50:]
        
        return comm
    
    def request_help(self, requester, situation: str) -> CoordinatedAction:
        help_action = CoordinatedAction(
            agent_name=requester.name,
            action_type='request_help',
            priority=ActionPriority.HIGH,
            requires_sync=True
        )
        
        for agent_name, data in self.goal_planner.agents.items():
            if agent_name != requester.name:
                help_action.sync_with.append(agent_name)
        
        self.sync_actions.append(help_action)
        return help_action
    
    def provide_cover(self, provider, target) -> CoordinatedAction:
        cover_action = CoordinatedAction(
            agent_name=provider.name,
            action_type='provide_cover',
            target=target,
            priority=ActionPriority.HIGH,
            requires_sync=True,
            sync_with=[target.name]
        )
        
        self.action_queue.append(cover_action)
        return cover_action
    
    def coordinate_attack(self, attackers: List, target) -> List[CoordinatedAction]:
        actions = []
        
        for i, attacker in enumerate(attackers):
            action = CoordinatedAction(
                agent_name=attacker.name,
                action_type='coordinated_attack',
                target=target,
                priority=ActionPriority.HIGH,
                requires_sync=True,
                sync_with=[a.name for a in attackers if a != attacker]
            )
            actions.append(action)
        
        self.sync_actions.extend(actions)
        return actions
    
    def plan_coordinated_turn(self, dek, thia, enemies: List, grid) -> Dict[str, CoordinatedAction]:
        planned_actions = {}
        
        self.goal_planner.evaluate_situation(dek, thia, enemies, grid)
        
        situation = {
            'leader_health': dek.health_percentage,
            'support_health': thia.health_percentage if thia and thia.is_alive else 100,
            'enemy_count': len(enemies),
            'enemy_distance': self._min_enemy_distance(dek, enemies),
            'boss_present': any(hasattr(e, 'phase') for e in enemies)
        }
        
        recommended_formation = self.formation_manager.recommend_formation(situation)
        self.formation_manager.set_formation(recommended_formation)
        
        boss_target = None
        for enemy in enemies:
            if hasattr(enemy, 'phase'):
                boss_target = enemy
                break
        
        formation_positions = self.formation_manager.get_formation_positions(
            (dek.x, dek.y),
            (boss_target.x, boss_target.y) if boss_target else None
        )
        
        dek_action = self._plan_dek_action(dek, thia, enemies, formation_positions, situation)
        planned_actions[dek.name] = dek_action
        
        if thia and thia.is_alive:
            thia_action = self._plan_thia_action(dek, thia, enemies, formation_positions, situation)
            planned_actions[thia.name] = thia_action
        
        self._update_coordination_score(dek, thia, planned_actions)
        
        return planned_actions
    
    def _min_enemy_distance(self, agent, enemies: List) -> float:
        if not enemies:
            return 100.0
        
        min_dist = float('inf')
        for enemy in enemies:
            dist = math.sqrt((enemy.x - agent.x)**2 + (enemy.y - agent.y)**2)
            min_dist = min(min_dist, dist)
        
        return min_dist
    
    def _plan_dek_action(self, dek, thia, enemies, formation_positions, situation) -> CoordinatedAction:
        if dek.health_percentage < 30:
            if thia and thia.is_alive:
                self.communicate(dek, thia, 'request_help', {'reason': 'low_health'})
            return CoordinatedAction(
                agent_name=dek.name,
                action_type='retreat',
                priority=ActionPriority.CRITICAL
            )
        
        boss_targets = [e for e in enemies if hasattr(e, 'phase')]
        if boss_targets:
            boss = boss_targets[0]
            distance = math.sqrt((boss.x - dek.x)**2 + (boss.y - dek.y)**2)
            
            if distance <= 1.5:
                if thia and thia.is_alive:
                    self.communicate(dek, thia, 'attack_signal', {'target': boss})
                    return CoordinatedAction(
                        agent_name=dek.name,
                        action_type='coordinated_attack',
                        target=boss,
                        priority=ActionPriority.HIGH,
                        requires_sync=True,
                        sync_with=[thia.name]
                    )
                return CoordinatedAction(
                    agent_name=dek.name,
                    action_type='attack',
                    target=boss,
                    priority=ActionPriority.HIGH
                )
            else:
                target_pos = formation_positions.get('leader', (boss.x, boss.y))
                return CoordinatedAction(
                    agent_name=dek.name,
                    action_type='move_to',
                    position=target_pos,
                    priority=ActionPriority.MEDIUM
                )
        
        if enemies:
            nearest = min(enemies, key=lambda e: math.sqrt((e.x - dek.x)**2 + (e.y - dek.y)**2))
            distance = math.sqrt((nearest.x - dek.x)**2 + (nearest.y - dek.y)**2)
            
            if distance <= 1.5:
                return CoordinatedAction(
                    agent_name=dek.name,
                    action_type='attack',
                    target=nearest,
                    priority=ActionPriority.MEDIUM
                )
            else:
                return CoordinatedAction(
                    agent_name=dek.name,
                    action_type='move_towards',
                    target=nearest,
                    priority=ActionPriority.LOW
                )
        
        return CoordinatedAction(
            agent_name=dek.name,
            action_type='patrol',
            priority=ActionPriority.LOW
        )
    
    def _plan_thia_action(self, dek, thia, enemies, formation_positions, situation) -> CoordinatedAction:
        if dek.health_percentage < 50:
            distance_to_dek = math.sqrt((thia.x - dek.x)**2 + (thia.y - dek.y)**2)
            
            if distance_to_dek <= 1.5:
                return CoordinatedAction(
                    agent_name=thia.name,
                    action_type='heal_ally',
                    target=dek,
                    priority=ActionPriority.CRITICAL
                )
            else:
                return CoordinatedAction(
                    agent_name=thia.name,
                    action_type='move_to_ally',
                    target=dek,
                    priority=ActionPriority.HIGH
                )
        
        if thia.health_percentage < 30:
            return CoordinatedAction(
                agent_name=thia.name,
                action_type='self_repair',
                priority=ActionPriority.HIGH
            )
        
        boss_targets = [e for e in enemies if hasattr(e, 'phase')]
        if boss_targets and dek.health_percentage > 60:
            boss = boss_targets[0]
            dek_distance = math.sqrt((dek.x - boss.x)**2 + (dek.y - boss.y)**2)
            
            if dek_distance <= 2:
                self.communicate(thia, dek, 'supporting_attack', {'target': boss})
                return CoordinatedAction(
                    agent_name=thia.name,
                    action_type='support_attack',
                    target=boss,
                    priority=ActionPriority.HIGH,
                    requires_sync=True,
                    sync_with=[dek.name]
                )
        
        target_pos = formation_positions.get('support', (dek.x - 1, dek.y))
        return CoordinatedAction(
            agent_name=thia.name,
            action_type='maintain_formation',
            position=target_pos,
            priority=ActionPriority.MEDIUM
        )
    
    def _update_coordination_score(self, dek, thia, planned_actions):
        score = 0.0
        
        synced_actions = sum(1 for a in planned_actions.values() if a.requires_sync)
        score += synced_actions * 10
        
        if thia and thia.is_alive:
            distance = math.sqrt((dek.x - thia.x)**2 + (dek.y - thia.y)**2)
            if distance <= 3:
                score += 20
            elif distance <= 6:
                score += 10
        
        dek_action = planned_actions.get(dek.name)
        if dek_action and thia:
            thia_action = planned_actions.get(thia.name)
            if thia_action:
                if dek_action.target == thia_action.target:
                    score += 30
        
        self.coordination_score = min(100.0, self.coordination_score * 0.9 + score * 0.1)
    
    def execute_coordinated_action(self, action: CoordinatedAction, agent, grid, all_agents: Dict):
        if action.action_type == 'retreat':
            return self._execute_retreat(agent, grid)
        elif action.action_type == 'coordinated_attack':
            return self._execute_coordinated_attack(action, agent, all_agents)
        elif action.action_type == 'attack':
            return self._execute_attack(agent, action.target)
        elif action.action_type == 'move_to':
            return self._execute_move_to(agent, action.position, grid)
        elif action.action_type == 'move_towards':
            return self._execute_move_towards(agent, action.target, grid)
        elif action.action_type == 'heal_ally':
            return self._execute_heal(agent, action.target)
        elif action.action_type == 'move_to_ally':
            return self._execute_move_towards(agent, action.target, grid)
        elif action.action_type == 'support_attack':
            return self._execute_support_attack(agent, action.target)
        elif action.action_type == 'maintain_formation':
            return self._execute_move_to(agent, action.position, grid)
        elif action.action_type == 'self_repair':
            return self._execute_self_repair(agent)
        elif action.action_type == 'patrol':
            return self._execute_patrol(agent, grid)
        
        return False
    
    def _execute_retreat(self, agent, grid):
        enemies = []
        if grid:
            for cell in grid.get_cells_in_radius(agent.x, agent.y, 5):
                if cell.occupant and cell.occupant != agent and cell.occupant.is_alive:
                    if hasattr(cell.occupant, 'aggression_level') or hasattr(cell.occupant, 'phase'):
                        enemies.append(cell.occupant)
        
        if not enemies:
            return False
        
        avg_enemy_x = sum(e.x for e in enemies) / len(enemies)
        avg_enemy_y = sum(e.y for e in enemies) / len(enemies)
        
        best_move = None
        best_distance = -1
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = agent.x + dx, agent.y + dy
                if grid:
                    new_x, new_y = grid.wrap_coordinates(new_x, new_y)
                
                dist = math.sqrt((new_x - avg_enemy_x)**2 + (new_y - avg_enemy_y)**2)
                if dist > best_distance:
                    best_distance = dist
                    best_move = (new_x, new_y)
        
        if best_move and agent.can_move():
            return agent.move_to(best_move[0], best_move[1])
        
        return False
    
    def _execute_coordinated_attack(self, action: CoordinatedAction, agent, all_agents: Dict):
        target = action.target
        if not target or not target.is_alive:
            return False
        
        distance = math.sqrt((agent.x - target.x)**2 + (agent.y - target.y)**2)
        if distance > 1.5:
            return False
        
        sync_bonus = len(action.sync_with) * 5
        base_damage = random.randint(20, 35) + sync_bonus
        
        target.take_damage(base_damage)
        
        if hasattr(agent, 'gain_honour'):
            agent.gain_honour(3)
        
        return True
    
    def _execute_attack(self, agent, target):
        if not target or not target.is_alive:
            return False
        
        distance = math.sqrt((agent.x - target.x)**2 + (agent.y - target.y)**2)
        if distance > 1.5:
            return False
        
        damage = random.randint(15, 30)
        target.take_damage(damage)
        
        if hasattr(agent, 'gain_honour') and not target.is_alive:
            agent.gain_honour(5)
        
        return True
    
    def _execute_move_to(self, agent, position, grid):
        if not position or not agent.can_move():
            return False
        
        target_x, target_y = position
        
        best_move = None
        best_distance = float('inf')
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = agent.x + dx, agent.y + dy
                if grid:
                    new_x, new_y = grid.wrap_coordinates(new_x, new_y)
                
                dist = math.sqrt((new_x - target_x)**2 + (new_y - target_y)**2)
                if dist < best_distance:
                    best_distance = dist
                    best_move = (new_x, new_y)
        
        if best_move:
            return agent.move_to(best_move[0], best_move[1])
        
        return False
    
    def _execute_move_towards(self, agent, target, grid):
        if not target:
            return False
        return self._execute_move_to(agent, (target.x, target.y), grid)
    
    def _execute_heal(self, agent, target):
        if not target or not hasattr(agent, 'battery_level'):
            return False
        
        heal_amount = 15
        target.heal(heal_amount)
        
        if hasattr(agent, 'consume_battery'):
            agent.consume_battery(5)
        
        return True
    
    def _execute_support_attack(self, agent, target):
        if not target or not target.is_alive:
            return False
        
        distance = math.sqrt((agent.x - target.x)**2 + (agent.y - target.y)**2)
        if distance > 3:
            return False
        
        damage = random.randint(10, 20)
        target.take_damage(damage)
        
        return True
    
    def _execute_self_repair(self, agent):
        if hasattr(agent, 'repair_damage'):
            agent.repair_damage(10)
            return True
        if hasattr(agent, 'heal'):
            agent.heal(10)
            return True
        return False
    
    def _execute_patrol(self, agent, grid):
        if not agent.can_move() or not grid:
            return False
        
        valid_moves = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = grid.wrap_coordinates(agent.x + dx, agent.y + dy)
                cell = grid.get_cell(new_x, new_y)
                if cell and not cell.terrain.is_hazardous:
                    valid_moves.append((new_x, new_y))
        
        if valid_moves:
            target = random.choice(valid_moves)
            return agent.move_to(target[0], target[1])
        
        return False
    
    def get_coordination_stats(self) -> Dict:
        return {
            'coordination_score': self.coordination_score,
            'active_goals': len(self.goal_planner.get_active_goals()),
            'completed_goals': len(self.goal_planner.completed_goals),
            'current_formation': self.formation_manager.current_formation,
            'communication_count': len(self.communication_log),
            'synced_actions_pending': len(self.sync_actions)
        }
