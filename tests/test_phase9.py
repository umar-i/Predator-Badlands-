import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from unittest.mock import Mock, MagicMock, patch
import random
import math


from coordination import (
    Role, GoalType, ActionPriority, SharedGoal, CoordinatedAction,
    ThreatAssessment, SharedGoalPlanner, RoleManager, FormationManager,
    CoordinationProtocol
)

from learning import (
    StateType, ActionSpace, State, Experience, RewardCalculator,
    TabularQLearning, ThiaLearning, BossPatternType, BossPattern,
    AdaptiveBossAI, LearningSystem
)

from procedural import (
    HazardType, PatternType, DifficultyLevel, HazardConfig,
    ProceduralHazard, NoiseGenerator, HazardGenerator,
    AdversaryPattern, PatternLibrary, AdversaryPatternGenerator,
    ProceduralEventGenerator, ProceduralSystem
)


class MockAgent:
    def __init__(self, name, x=0, y=0, health=100, max_health=100, 
                 stamina=100, max_stamina=100):
        self.name = name
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health
        self.stamina = stamina
        self.max_stamina = max_stamina
        self.is_alive = health > 0
        self.honour = 0
    
    @property
    def health_percentage(self):
        return (self.health / self.max_health) * 100 if self.max_health > 0 else 0
    
    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.is_alive = False
    
    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
    
    def gain_honour(self, amount):
        self.honour += amount
    
    def move_to(self, x, y):
        self.x = x
        self.y = y
        return True
    
    def can_move(self):
        return self.is_alive and self.stamina > 0


class MockBoss(MockAgent):
    def __init__(self, x=10, y=10):
        super().__init__("Boss", x, y, health=500, max_health=500)
        self.phase = 1
        self.attack_range = 2
        self.territory_center = (x, y)
        self.territory_radius = 7
        self.is_enraged = False


class MockGrid:
    def __init__(self, width=30, height=30):
        self.width = width
        self.height = height
    
    def wrap_coordinates(self, x, y):
        return x % self.width, y % self.height
    
    def get_cells_in_radius(self, x, y, radius):
        return []
    
    def get_cell(self, x, y):
        mock_cell = Mock()
        mock_cell.terrain = Mock()
        mock_cell.terrain.is_hazardous = False
        return mock_cell


class TestThreatAssessment(unittest.TestCase):
    
    def setUp(self):
        self.threat = ThreatAssessment()
    
    def test_assess_threat_boss(self):
        boss = MockBoss()
        boss.phase = 2
        
        threat_level = self.threat.assess_threat(boss, (0, 0))
        
        self.assertGreater(threat_level, 0)
        self.assertIn(id(boss), self.threat.threat_levels)
    
    def test_assess_threat_wildlife(self):
        wildlife = MockAgent("Wildlife", 5, 5)
        wildlife.aggression_level = 0.8
        
        threat_level = self.threat.assess_threat(wildlife, (0, 0))
        
        self.assertGreater(threat_level, 0)
    
    def test_get_highest_threat(self):
        enemies = [
            MockAgent("Weak", 1, 1, health=20),
            MockBoss(2, 2),
            MockAgent("Medium", 3, 3, health=50)
        ]
        enemies[1].phase = 2
        
        highest, level = self.threat.get_highest_threat(enemies, (0, 0))
        
        self.assertIsNotNone(highest)
        self.assertEqual(highest.name, "Boss")
    
    def test_danger_zones(self):
        self.threat.mark_danger_zone((5, 5), radius=2)
        
        self.assertTrue(self.threat.is_position_dangerous((5, 5)))
        self.assertTrue(self.threat.is_position_dangerous((6, 6)))
        self.assertFalse(self.threat.is_position_dangerous((10, 10)))
        
        self.threat.clear_danger_zones()
        self.assertFalse(self.threat.is_position_dangerous((5, 5)))
    
    def test_dead_enemy_no_threat(self):
        dead_enemy = MockAgent("Dead", 1, 1, health=0)
        
        threat_level = self.threat.assess_threat(dead_enemy, (0, 0))
        
        self.assertEqual(threat_level, 0)


class TestSharedGoalPlanner(unittest.TestCase):
    
    def setUp(self):
        self.planner = SharedGoalPlanner()
        self.dek = MockAgent("Dek", 5, 5)
        self.thia = MockAgent("Thia", 6, 5)
    
    def test_register_agent(self):
        self.planner.register_agent(self.dek, Role.LEADER)
        
        self.assertIn("Dek", self.planner.agents)
        self.assertEqual(self.planner.agents["Dek"]['role'], Role.LEADER)
    
    def test_add_goal(self):
        goal = SharedGoal(
            goal_type=GoalType.HUNT_TARGET,
            priority=ActionPriority.HIGH,
            target=MockAgent("Target", 10, 10)
        )
        
        self.planner.add_goal(goal)
        
        self.assertEqual(len(self.planner.goals), 1)
    
    def test_goal_sorting_by_priority(self):
        low_goal = SharedGoal(GoalType.SURVIVE, ActionPriority.LOW)
        high_goal = SharedGoal(GoalType.DEFEAT_BOSS, ActionPriority.HIGH)
        critical_goal = SharedGoal(GoalType.ESCAPE_DANGER, ActionPriority.CRITICAL)
        
        self.planner.add_goal(low_goal)
        self.planner.add_goal(high_goal)
        self.planner.add_goal(critical_goal)
        
        self.assertEqual(self.planner.goals[0].priority, ActionPriority.CRITICAL)
    
    def test_evaluate_situation_low_health(self):
        self.planner.register_agent(self.dek, Role.LEADER)
        self.dek.health = 20
        
        new_goals = self.planner.evaluate_situation(self.dek, self.thia, [], None)
        
        survive_goals = [g for g in new_goals if g.goal_type == GoalType.SURVIVE]
        self.assertGreater(len(survive_goals), 0)
    
    def test_assign_goal(self):
        goal = SharedGoal(GoalType.HUNT_TARGET, ActionPriority.MEDIUM)
        self.planner.register_agent(self.dek, Role.LEADER)
        self.planner.add_goal(goal)
        
        self.planner.assign_goal(goal, "Dek")
        
        self.assertIn("Dek", goal.assigned_agents)
    
    def test_update_goal_progress(self):
        goal = SharedGoal(GoalType.HUNT_TARGET, ActionPriority.MEDIUM)
        self.planner.add_goal(goal)
        
        self.planner.update_goal_progress(goal, 0.5)
        self.assertEqual(goal.progress, 0.5)
        
        self.planner.update_goal_progress(goal, 0.6)
        self.assertTrue(goal.completed)


class TestRoleManager(unittest.TestCase):
    
    def setUp(self):
        self.role_manager = RoleManager()
        self.dek = MockAgent("Dek")
        self.thia = MockAgent("Thia")
    
    def test_assign_role(self):
        self.role_manager.assign_role(self.dek, Role.LEADER)
        
        self.assertEqual(self.role_manager.get_role("Dek"), Role.LEADER)
    
    def test_get_capabilities(self):
        self.role_manager.assign_role(self.dek, Role.LEADER)
        
        capabilities = self.role_manager.get_capabilities("Dek")
        
        self.assertTrue(capabilities.get('can_command', False))
    
    def test_stat_bonus(self):
        self.role_manager.assign_role(self.thia, Role.SUPPORT)
        
        healing_bonus = self.role_manager.get_stat_bonus("Thia", "healing")
        
        self.assertGreater(healing_bonus, 1.0)
    
    def test_recommend_action(self):
        self.role_manager.assign_role(self.thia, Role.SUPPORT)
        
        available = ['attack', 'heal', 'move']
        recommended = self.role_manager.recommend_action("Thia", available)
        
        self.assertEqual(recommended, 'heal')
    
    def test_evaluate_role_effectiveness(self):
        self.role_manager.assign_role(self.dek, Role.ATTACKER)
        
        recent_actions = ['attack', 'attack', 'move', 'attack']
        effectiveness = self.role_manager.evaluate_role_effectiveness(self.dek, recent_actions)
        
        self.assertGreater(effectiveness, 0.5)


class TestFormationManager(unittest.TestCase):
    
    def setUp(self):
        self.formation = FormationManager()
    
    def test_set_formation(self):
        self.formation.set_formation('aggressive')
        
        self.assertEqual(self.formation.current_formation, 'aggressive')
        self.assertIn('aggressive', self.formation.formation_history)
    
    def test_get_formation_positions(self):
        self.formation.set_formation('flanking')
        
        positions = self.formation.get_formation_positions((10, 10), (15, 10))
        
        self.assertIn('leader', positions)
        self.assertIn('support', positions)
    
    def test_recommend_formation_retreat(self):
        situation = {
            'leader_health': 20,
            'support_health': 50,
            'enemy_count': 3,
            'enemy_distance': 2,
            'boss_present': False
        }
        
        recommended = self.formation.recommend_formation(situation)
        
        self.assertEqual(recommended, 'retreat')
    
    def test_recommend_formation_boss(self):
        situation = {
            'leader_health': 80,
            'support_health': 70,
            'enemy_count': 1,
            'enemy_distance': 4,
            'boss_present': True
        }
        
        recommended = self.formation.recommend_formation(situation)
        
        self.assertIn(recommended, ['flanking', 'surround'])


class TestCoordinationProtocol(unittest.TestCase):
    
    def setUp(self):
        self.protocol = CoordinationProtocol()
        self.dek = MockAgent("Dek", 10, 10)
        self.thia = MockAgent("Thia", 11, 10)
        self.grid = MockGrid()
    
    def test_initialize(self):
        self.protocol.initialize(self.dek, self.thia)
        
        self.assertIn("Dek", self.protocol.goal_planner.agents)
        self.assertIn("Thia", self.protocol.goal_planner.agents)
    
    def test_communicate(self):
        comm = self.protocol.communicate(self.dek, self.thia, 'request_help', {'reason': 'low_health'})
        
        self.assertEqual(comm['sender'], 'Dek')
        self.assertEqual(comm['receiver'], 'Thia')
        self.assertEqual(len(self.protocol.communication_log), 1)
    
    def test_request_help(self):
        self.protocol.initialize(self.dek, self.thia)
        
        action = self.protocol.request_help(self.dek, 'under_attack')
        
        self.assertEqual(action.action_type, 'request_help')
        self.assertTrue(action.requires_sync)
    
    def test_provide_cover(self):
        action = self.protocol.provide_cover(self.thia, self.dek)
        
        self.assertEqual(action.action_type, 'provide_cover')
        self.assertEqual(action.target, self.dek)
    
    def test_plan_coordinated_turn(self):
        self.protocol.initialize(self.dek, self.thia)
        enemies = [MockAgent("Enemy", 12, 10)]
        
        planned = self.protocol.plan_coordinated_turn(self.dek, self.thia, enemies, self.grid)
        
        self.assertIn("Dek", planned)
        self.assertIn("Thia", planned)
    
    def test_coordination_score_update(self):
        self.protocol.initialize(self.dek, self.thia)
        
        initial_score = self.protocol.coordination_score
        
        enemies = [MockBoss(12, 10)]
        self.protocol.plan_coordinated_turn(self.dek, self.thia, enemies, self.grid)
        
        self.assertGreaterEqual(self.protocol.coordination_score, 0)


class TestState(unittest.TestCase):
    
    def test_discretize_health(self):
        self.assertEqual(State.discretize_health(90), 3)
        self.assertEqual(State.discretize_health(60), 2)
        self.assertEqual(State.discretize_health(30), 1)
        self.assertEqual(State.discretize_health(10), 0)
    
    def test_discretize_distance(self):
        self.assertEqual(State.discretize_distance(1), 0)
        self.assertEqual(State.discretize_distance(3), 1)
        self.assertEqual(State.discretize_distance(6), 2)
        self.assertEqual(State.discretize_distance(15), 3)
    
    def test_discretize_stamina(self):
        self.assertEqual(State.discretize_stamina(80), 2)
        self.assertEqual(State.discretize_stamina(50), 1)
        self.assertEqual(State.discretize_stamina(20), 0)
    
    def test_state_to_tuple(self):
        state = State(
            health_level=2,
            enemy_distance=1,
            enemy_count=2,
            ally_nearby=True,
            stamina_level=2,
            boss_phase=1
        )
        
        tuple_form = state.to_tuple()
        
        self.assertEqual(len(tuple_form), 6)
        self.assertEqual(tuple_form[3], 1)


class TestRewardCalculator(unittest.TestCase):
    
    def setUp(self):
        self.calculator = RewardCalculator()
        self.agent = MockAgent("Dek")
    
    def test_survive_turn_reward(self):
        prev_state = {'health': 100, 'kills': 0, 'damage_dealt': 0}
        curr_state = {'health': 100, 'kills': 0, 'damage_dealt': 0, 'health_pct': 100}
        
        reward = self.calculator.calculate_turn_reward(
            self.agent, prev_state, curr_state, ActionSpace.ATTACK
        )
        
        self.assertGreater(reward, 0)
    
    def test_damage_taken_penalty(self):
        prev_state = {'health': 100, 'kills': 0, 'damage_dealt': 0}
        curr_state = {'health': 70, 'kills': 0, 'damage_dealt': 0, 'health_pct': 70}
        
        reward = self.calculator.calculate_turn_reward(
            self.agent, prev_state, curr_state, ActionSpace.ATTACK
        )
        
        self.assertLess(reward, 1.0)
    
    def test_kill_reward(self):
        prev_state = {'health': 100, 'kills': 0, 'damage_dealt': 0}
        curr_state = {'health': 100, 'kills': 1, 'damage_dealt': 30, 
                     'health_pct': 100, 'last_kill_type': 'wildlife'}
        
        reward = self.calculator.calculate_turn_reward(
            self.agent, prev_state, curr_state, ActionSpace.ATTACK
        )
        
        self.assertGreater(reward, 5)
    
    def test_boss_kill_reward(self):
        prev_state = {'health': 100, 'kills': 0, 'damage_dealt': 0}
        curr_state = {'health': 100, 'kills': 1, 'damage_dealt': 50, 
                     'health_pct': 100, 'last_kill_type': 'boss'}
        
        reward = self.calculator.calculate_turn_reward(
            self.agent, prev_state, curr_state, ActionSpace.ATTACK
        )
        
        self.assertGreater(reward, 50)
    
    def test_average_reward(self):
        for _ in range(10):
            self.calculator.reward_history.append(random.uniform(-10, 10))
        
        avg = self.calculator.get_average_reward(5)
        
        self.assertIsInstance(avg, float)


class TestTabularQLearning(unittest.TestCase):
    
    def setUp(self):
        self.q_learning = TabularQLearning(
            learning_rate=0.1,
            discount_factor=0.95,
            exploration_rate=0.5
        )
        self.dek = MockAgent("Dek", 5, 5)
        self.thia = MockAgent("Thia", 6, 5)
    
    def test_get_state_from_environment(self):
        enemies = [MockAgent("Enemy", 7, 5)]
        
        state = self.q_learning.get_state_from_environment(self.dek, enemies, self.thia)
        
        self.assertIsInstance(state, State)
        self.assertTrue(state.ally_nearby)
    
    def test_get_q_value_new_state(self):
        state = State(2, 1, 1, True, 2, 1)
        
        q_value = self.q_learning.get_q_value(state, ActionSpace.ATTACK)
        
        self.assertEqual(q_value, 0.0)
    
    def test_update_q_value(self):
        state = State(2, 1, 1, True, 2, 1)
        next_state = State(2, 0, 0, True, 2, 1)
        
        self.q_learning.update(state, ActionSpace.ATTACK, 10.0, next_state, False)
        
        new_q = self.q_learning.get_q_value(state, ActionSpace.ATTACK)
        self.assertGreater(new_q, 0)
    
    def test_select_action_exploration(self):
        self.q_learning.epsilon = 1.0
        state = State(2, 1, 1, True, 2, 1)
        
        actions = set()
        for _ in range(100):
            action = self.q_learning.select_action(state)
            actions.add(action)
        
        self.assertGreater(len(actions), 1)
    
    def test_select_action_exploitation(self):
        self.q_learning.epsilon = 0.0
        state = State(2, 1, 1, True, 2, 1)
        
        self.q_learning.q_table[state.to_tuple()] = {
            ActionSpace.ATTACK.value: 100.0,
            ActionSpace.RETREAT.value: 10.0,
            ActionSpace.HEAL.value: 5.0
        }
        
        action = self.q_learning.select_action(state)
        
        self.assertEqual(action, ActionSpace.ATTACK)
    
    def test_decay_exploration(self):
        initial_epsilon = self.q_learning.epsilon
        
        for _ in range(10):
            self.q_learning.decay_exploration()
        
        self.assertLess(self.q_learning.epsilon, initial_epsilon)
    
    def test_store_experience(self):
        state = State(2, 1, 1, True, 2, 1)
        next_state = State(2, 0, 0, True, 2, 1)
        
        exp = Experience(state, ActionSpace.ATTACK, 10.0, next_state, False)
        self.q_learning.store_experience(exp)
        
        self.assertEqual(len(self.q_learning.experience_buffer), 1)
    
    def test_get_best_action(self):
        state = State(2, 1, 1, True, 2, 1)
        
        self.q_learning.q_table[state.to_tuple()] = {
            ActionSpace.ATTACK.value: 50.0,
            ActionSpace.RETREAT.value: 10.0,
            ActionSpace.HEAL.value: 30.0
        }
        
        best = self.q_learning.get_best_action(state)
        
        self.assertEqual(best, ActionSpace.ATTACK)


class TestThiaLearning(unittest.TestCase):
    
    def setUp(self):
        self.thia_learning = ThiaLearning()
    
    def test_get_support_action_low_partner_health(self):
        own_state = State(2, 2, 1, True, 2, 1)
        partner_state = State(0, 1, 1, True, 1, 1)
        
        action = self.thia_learning.get_support_action(own_state, partner_state)
        
        self.assertEqual(action, ActionSpace.HEAL)
    
    def test_get_support_action_partner_in_combat(self):
        own_state = State(2, 2, 1, True, 2, 1)
        partner_state = State(2, 0, 2, True, 2, 1)
        
        action = self.thia_learning.get_support_action(own_state, partner_state)
        
        self.assertEqual(action, ActionSpace.COORDINATE)
    
    def test_update_support_learning(self):
        own_state = State(2, 2, 1, True, 2, 1)
        partner_state = State(2, 1, 1, True, 2, 1)
        next_own = State(2, 2, 1, True, 2, 1)
        next_partner = State(2, 1, 0, True, 2, 1)
        
        self.thia_learning.update_support_learning(
            own_state, partner_state, ActionSpace.COORDINATE, 15.0,
            next_own, next_partner
        )
        
        combined_key = (own_state.to_tuple(), partner_state.to_tuple())
        self.assertIn(combined_key, self.thia_learning.support_q_table)


class TestAdaptiveBossAI(unittest.TestCase):
    
    def setUp(self):
        self.boss = MockBoss(15, 15)
        self.boss_ai = AdaptiveBossAI(self.boss)
    
    def test_initial_pattern(self):
        self.assertEqual(self.boss_ai.current_pattern.pattern_type, BossPatternType.TERRITORIAL)
    
    def test_observe_player_action(self):
        player = MockAgent("Dek", 10, 10)
        
        self.boss_ai.observe_player_action(player, 'attack', True)
        
        self.assertEqual(len(self.boss_ai.player_behavior_memory), 1)
    
    def test_record_damage_source(self):
        attacker = MockAgent("Dek", 10, 10)
        
        self.boss_ai.record_damage_source(attacker, 50)
        
        self.assertIn("Dek", self.boss_ai.damage_received_sources)
        self.assertEqual(self.boss_ai.damage_received_sources["Dek"]['total_damage'], 50)
    
    def test_adaptation_to_aggressive_player(self):
        player = MockAgent("Dek", 10, 10)
        
        for _ in range(10):
            self.boss_ai.observe_player_action(player, 'attack', True)
        
        self.assertGreater(self.boss_ai.player_tendencies['aggression'], 0.5)
    
    def test_get_adaptive_action(self):
        enemies = [MockAgent("Dek", 14, 15)]
        grid = MockGrid()
        
        action = self.boss_ai.get_adaptive_action(enemies, grid)
        
        self.assertIn('type', action)
        self.assertIn('damage_modifier', action)
    
    def test_berserk_pattern_low_health(self):
        self.boss.health = 50
        self.boss_ai.pattern_change_cooldown = 0
        
        self.boss_ai._consider_pattern_change()
        
        self.assertEqual(self.boss_ai.current_pattern.pattern_type, BossPatternType.BERSERK)
    
    def test_execute_adaptive_action_attack(self):
        target = MockAgent("Dek", 15, 16, health=100)
        action = {'type': 'attack', 'target': target, 'damage_modifier': 1.0}
        grid = MockGrid()
        
        result = self.boss_ai.execute_adaptive_action(action, grid)
        
        self.assertTrue(result)
        self.assertLess(target.health, 100)
    
    def test_get_adaptation_stats(self):
        stats = self.boss_ai.get_adaptation_stats()
        
        self.assertIn('current_pattern', stats)
        self.assertIn('adaptation_level', stats)
        self.assertIn('player_tendencies', stats)


class TestLearningSystem(unittest.TestCase):
    
    def setUp(self):
        self.system = LearningSystem()
        self.dek = MockAgent("Dek", 10, 10)
        self.thia = MockAgent("Thia", 11, 10)
        self.boss = MockBoss(20, 20)
    
    def test_initialize_boss_ai(self):
        self.system.initialize_boss_ai(self.boss)
        
        self.assertIsNotNone(self.system.boss_ai)
    
    def test_get_dek_action(self):
        enemies = [MockAgent("Enemy", 12, 10)]
        
        action = self.system.get_dek_action(self.dek, enemies, self.thia)
        
        self.assertIsInstance(action, ActionSpace)
    
    def test_get_thia_action(self):
        enemies = [MockAgent("Enemy", 12, 10)]
        
        action = self.system.get_thia_action(self.thia, self.dek, enemies)
        
        self.assertIsInstance(action, ActionSpace)
    
    def test_get_boss_action(self):
        self.system.initialize_boss_ai(self.boss)
        enemies = [self.dek, self.thia]
        grid = MockGrid()
        
        action = self.system.get_boss_action(enemies, grid)
        
        self.assertIn('type', action)
    
    def test_get_learning_stats(self):
        stats = self.system.get_learning_stats()
        
        self.assertIn('dek_stats', stats)
        self.assertIn('thia_stats', stats)
    
    def test_end_episode(self):
        self.system.dek_learning.reward_calculator.cumulative_reward = 100.0
        
        self.system.end_episode()
        
        self.assertEqual(len(self.system.episode_rewards), 1)
        self.assertEqual(self.system.dek_learning.training_stats['episodes'], 1)


class TestNoiseGenerator(unittest.TestCase):
    
    def setUp(self):
        self.noise = NoiseGenerator(seed=42)
    
    def test_perlin_2d_range(self):
        for _ in range(100):
            x = random.uniform(0, 100)
            y = random.uniform(0, 100)
            value = self.noise.perlin_2d(x, y)
            
            self.assertGreaterEqual(value, -2)
            self.assertLessEqual(value, 2)
    
    def test_octave_perlin_consistency(self):
        value1 = self.noise.octave_perlin(5.0, 5.0)
        value2 = self.noise.octave_perlin(5.0, 5.0)
        
        self.assertEqual(value1, value2)


class TestHazardGenerator(unittest.TestCase):
    
    def setUp(self):
        self.generator = HazardGenerator(30, 30, seed=42)
    
    def test_generate_hazard_at(self):
        hazard = self.generator.generate_hazard_at((10, 10), HazardType.ACID_POOL, 0)
        
        self.assertEqual(hazard.position, (10, 10))
        self.assertEqual(hazard.hazard_type, HazardType.ACID_POOL)
        self.assertTrue(hazard.is_active)
    
    def test_generate_pattern_circular(self):
        hazards = self.generator.generate_pattern(
            PatternType.CIRCULAR, (15, 15), HazardType.FIRE_VENT, 
            count=6, spread=5, turn=0
        )
        
        self.assertEqual(len(hazards), 6)
    
    def test_generate_pattern_clustered(self):
        hazards = self.generator.generate_pattern(
            PatternType.CLUSTERED, (15, 15), HazardType.SPIKE_TRAP,
            count=8, spread=4, turn=0
        )
        
        self.assertGreater(len(hazards), 0)
        self.assertLessEqual(len(hazards), 8)
    
    def test_update_hazards_expiration(self):
        hazard = self.generator.generate_hazard_at((10, 10), HazardType.FIRE_VENT, 0)
        hazard.duration = 2
        hazard.activation_delay = 0
        
        self.generator.update_hazards(1)
        self.assertEqual(hazard.duration, 1)
        
        self.generator.update_hazards(2)
        self.assertEqual(hazard.duration, 0)
    
    def test_calculate_damage_at(self):
        self.generator.generate_hazard_at((10, 10), HazardType.ACID_POOL, 0)
        
        damage = self.generator.calculate_damage_at((10, 10))
        
        self.assertGreater(damage, 0)
    
    def test_get_hazards_in_radius(self):
        self.generator.generate_hazard_at((10, 10), HazardType.RADIATION, 0)
        self.generator.generate_hazard_at((12, 10), HazardType.ACID_POOL, 0)
        self.generator.generate_hazard_at((50, 50), HazardType.SPIKE_TRAP, 0)
        
        nearby = self.generator.get_hazards_in_radius((11, 10), 5)
        
        self.assertEqual(len(nearby), 2)
    
    def test_clear_hazards(self):
        self.generator.generate_hazard_at((10, 10), HazardType.ACID_POOL, 0)
        self.generator.generate_hazard_at((15, 15), HazardType.FIRE_VENT, 0)
        
        self.generator.clear_hazards()
        
        self.assertEqual(len(self.generator.hazards), 0)


class TestAdversaryPatternGenerator(unittest.TestCase):
    
    def setUp(self):
        self.generator = AdversaryPatternGenerator(DifficultyLevel.MEDIUM)
    
    def test_generate_pattern_aggressive(self):
        pattern = self.generator.generate_pattern('wildlife', 'aggressive')
        
        self.assertIsInstance(pattern, AdversaryPattern)
        self.assertGreater(len(pattern.movement_sequence), 0)
        self.assertGreater(len(pattern.attack_sequence), 0)
    
    def test_generate_pattern_defensive(self):
        pattern = self.generator.generate_pattern('hunter', 'defensive')
        
        self.assertIsNotNone(pattern.name)
        self.assertIn('defensive', pattern.name)
    
    def test_generate_boss_pattern_phase1(self):
        pattern = self.generator.generate_boss_pattern(phase=1)
        
        self.assertEqual(pattern.name, "boss_phase_1")
        self.assertIn(50, pattern.phase_transitions)
    
    def test_generate_boss_pattern_phase2(self):
        pattern = self.generator.generate_boss_pattern(phase=2)
        
        self.assertEqual(pattern.name, "boss_phase_2")
    
    def test_mutate_pattern(self):
        original = self.generator.generate_pattern('test', 'balanced')
        
        mutated = self.generator.mutate_pattern(original, mutation_rate=0.8)
        
        self.assertIn('mutated', mutated.name)
    
    def test_record_effectiveness(self):
        self.generator.record_effectiveness('test_pattern', True)
        self.generator.record_effectiveness('test_pattern', True)
        
        self.assertGreater(self.generator.pattern_effectiveness['test_pattern'], 0.5)


class TestProceduralEventGenerator(unittest.TestCase):
    
    def setUp(self):
        self.generator = ProceduralEventGenerator(30, 30)
    
    def test_generate_event(self):
        game_state = {'player_position': (15, 15)}
        
        event = self.generator.generate_event(1, game_state)
        
        self.assertIsNotNone(event)
        self.assertIn('type', event)
    
    def test_queue_event(self):
        event = {'type': 'test', 'turn': 5}
        
        self.generator.queue_event(event, delay=3)
        
        self.assertEqual(len(self.generator.event_queue), 1)
        self.assertEqual(self.generator.event_queue[0]['execute_turn'], 8)
    
    def test_get_pending_events(self):
        self.generator.queue_event({'type': 'early', 'turn': 0}, delay=0)
        self.generator.queue_event({'type': 'late', 'turn': 0}, delay=10)
        
        pending = self.generator.get_pending_events(5)
        
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]['type'], 'early')


class TestProceduralSystem(unittest.TestCase):
    
    def setUp(self):
        self.system = ProceduralSystem(30, 30, DifficultyLevel.MEDIUM, seed=42)
    
    def test_initialize(self):
        self.system.initialize(initial_hazard_count=10)
        
        self.assertEqual(self.system.stats['hazards_generated'], 10)
    
    def test_update(self):
        self.system.initialize(5)
        game_state = {'player_position': (15, 15)}
        
        result = self.system.update(1, game_state)
        
        self.assertIn('expired_hazards', result)
        self.assertIn('new_hazards', result)
        self.assertIn('events', result)
    
    def test_get_damage_at_position(self):
        self.system.hazard_generator.generate_hazard_at((10, 10), HazardType.ACID_POOL, 0)
        
        damage = self.system.get_damage_at_position((10, 10))
        
        self.assertGreater(damage, 0)
    
    def test_get_hazards_near(self):
        self.system.hazard_generator.generate_hazard_at((10, 10), HazardType.FIRE_VENT, 0)
        
        nearby = self.system.get_hazards_near((11, 11), radius=3)
        
        self.assertGreater(len(nearby), 0)
    
    def test_generate_boss_patterns(self):
        phase1, phase2 = self.system.generate_boss_patterns()
        
        self.assertIsInstance(phase1, AdversaryPattern)
        self.assertIsInstance(phase2, AdversaryPattern)
        self.assertEqual(self.system.stats['patterns_generated'], 2)
    
    def test_generate_enemy_pattern(self):
        pattern = self.system.generate_enemy_pattern('wildlife', 'aggressive')
        
        self.assertIsInstance(pattern, AdversaryPattern)
    
    def test_get_stats(self):
        self.system.initialize(5)
        
        stats = self.system.get_stats()
        
        self.assertIn('hazards_generated', stats)
        self.assertIn('active_hazards', stats)
        self.assertIn('difficulty', stats)


class TestIntegration(unittest.TestCase):
    
    def setUp(self):
        self.dek = MockAgent("Dek", 10, 10)
        self.thia = MockAgent("Thia", 11, 10)
        self.boss = MockBoss(20, 20)
        self.grid = MockGrid()
        
        self.coordination = CoordinationProtocol()
        self.learning = LearningSystem()
        self.procedural = ProceduralSystem(30, 30, DifficultyLevel.MEDIUM)
    
    def test_full_turn_simulation(self):
        self.coordination.initialize(self.dek, self.thia)
        self.learning.initialize_boss_ai(self.boss)
        self.procedural.initialize(5)
        
        enemies = [self.boss, MockAgent("Wildlife", 15, 15)]
        
        dek_action = self.learning.get_dek_action(self.dek, enemies, self.thia)
        self.assertIsInstance(dek_action, ActionSpace)
        
        thia_action = self.learning.get_thia_action(self.thia, self.dek, enemies)
        self.assertIsInstance(thia_action, ActionSpace)
        
        planned = self.coordination.plan_coordinated_turn(self.dek, self.thia, enemies, self.grid)
        self.assertIn("Dek", planned)
        
        boss_action = self.learning.get_boss_action([self.dek, self.thia], self.grid)
        self.assertIn('type', boss_action)
        
        game_state = {'player_position': (self.dek.x, self.dek.y)}
        proc_result = self.procedural.update(1, game_state)
        self.assertIn('events', proc_result)
    
    def test_coordination_with_learning(self):
        self.coordination.initialize(self.dek, self.thia)
        
        enemies = [MockAgent("Enemy", 12, 10)]
        
        state = self.learning.dek_learning.get_state_from_environment(self.dek, enemies, self.thia)
        
        planned = self.coordination.plan_coordinated_turn(self.dek, self.thia, enemies, self.grid)
        
        if self.dek.name in planned:
            action = planned[self.dek.name]
            self.assertIsNotNone(action.action_type)
    
    def test_boss_adaptation_over_time(self):
        self.learning.initialize_boss_ai(self.boss)
        
        for turn in range(20):
            self.learning.boss_ai.observe_player_action(self.dek, 'attack', True)
            
            action = self.learning.get_boss_action([self.dek, self.thia], self.grid)
            self.assertIsNotNone(action)
        
        self.assertGreater(self.learning.boss_ai.player_tendencies['aggression'], 0.5)
    
    def test_hazard_damage_integration(self):
        self.procedural.initialize(0)
        
        self.procedural.hazard_generator.generate_hazard_at(
            (self.dek.x, self.dek.y), HazardType.ACID_POOL, 0
        )
        
        damage = self.procedural.get_damage_at_position((self.dek.x, self.dek.y))
        
        self.assertGreater(damage, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
