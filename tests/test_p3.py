import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent import Agent
from predator import PredatorAgent, Dek
from grid import Grid


class MockAgent(Agent):
    
    def __init__(self, name="MockAgent", x=0, y=0):
        super().__init__(name, x, y)
    
    def decide_action(self):
        return "idle"
    
    def update(self):
        pass


class TestAgentBasics(unittest.TestCase):
    
    def test_agent_creation(self):
        agent = MockAgent("TestAgent", 5, 10)
        self.assertEqual(agent.name, "TestAgent")
        self.assertEqual(agent.x, 5)
        self.assertEqual(agent.y, 10)
    
    def test_agent_default_stats(self):
        agent = MockAgent()
        self.assertEqual(agent.max_health, 100)
        self.assertEqual(agent.health, 100)
        self.assertEqual(agent.max_stamina, 100)
        self.assertEqual(agent.stamina, 100)
        self.assertTrue(agent.is_alive)
        self.assertEqual(agent.age, 0)
    
    def test_agent_position_property(self):
        agent = MockAgent("Test", 7, 12)
        self.assertEqual(agent.position, (7, 12))
    
    def test_agent_health_percentage(self):
        agent = MockAgent()
        agent.health = 50
        self.assertEqual(agent.health_percentage, 50.0)
    
    def test_agent_stamina_percentage(self):
        agent = MockAgent()
        agent.stamina = 75
        self.assertEqual(agent.stamina_percentage, 75.0)
    
    def test_agent_symbol(self):
        agent = MockAgent()
        self.assertEqual(agent.symbol, '?')


class TestAgentHealth(unittest.TestCase):
    
    def test_take_damage(self):
        agent = MockAgent()
        agent.take_damage(30)
        self.assertEqual(agent.health, 70)
        self.assertTrue(agent.is_alive)
    
    def test_take_damage_fatal(self):
        agent = MockAgent()
        agent.take_damage(150)
        self.assertEqual(agent.health, 0)
        self.assertFalse(agent.is_alive)
    
    def test_take_damage_no_negative(self):
        agent = MockAgent()
        agent.take_damage(200)
        self.assertEqual(agent.health, 0)
    
    def test_heal(self):
        agent = MockAgent()
        agent.take_damage(50)
        agent.heal(30)
        self.assertEqual(agent.health, 80)
    
    def test_heal_no_overflow(self):
        agent = MockAgent()
        agent.take_damage(20)
        agent.heal(50)
        self.assertEqual(agent.health, 100)


class TestAgentStamina(unittest.TestCase):
    
    def test_consume_stamina(self):
        agent = MockAgent()
        result = agent.consume_stamina(30)
        self.assertEqual(agent.stamina, 70)
        self.assertTrue(result)
    
    def test_consume_stamina_depleted(self):
        agent = MockAgent()
        agent.consume_stamina(100)
        result = agent.consume_stamina(10)
        self.assertEqual(agent.stamina, 0)
        self.assertFalse(result)
    
    def test_restore_stamina(self):
        agent = MockAgent()
        agent.consume_stamina(50)
        agent.restore_stamina(30)
        self.assertEqual(agent.stamina, 80)
    
    def test_restore_stamina_no_overflow(self):
        agent = MockAgent()
        agent.consume_stamina(20)
        agent.restore_stamina(50)
        self.assertEqual(agent.stamina, 100)


class TestAgentMovement(unittest.TestCase):
    
    def test_can_move(self):
        agent = MockAgent()
        self.assertTrue(agent.can_move())
    
    def test_cannot_move_when_dead(self):
        agent = MockAgent()
        agent.is_alive = False
        self.assertFalse(agent.can_move())
    
    def test_cannot_move_no_stamina(self):
        agent = MockAgent()
        agent.stamina = 0
        self.assertFalse(agent.can_move())
    
    def test_can_act_alive(self):
        agent = MockAgent()
        self.assertTrue(agent.can_act())
    
    def test_cannot_act_dead(self):
        agent = MockAgent()
        agent.is_alive = False
        self.assertFalse(agent.can_act())
    
    def test_set_grid(self):
        agent = MockAgent()
        grid = Grid(20, 20)
        agent.set_grid(grid)
        self.assertEqual(agent.grid, grid)
    
    def test_get_adjacent_positions(self):
        agent = MockAgent("Test", 5, 5)
        grid = Grid(20, 20)
        agent.set_grid(grid)
        positions = agent.get_adjacent_positions()
        self.assertEqual(len(positions), 8)
    
    def test_get_valid_moves(self):
        agent = MockAgent("Test", 5, 5)
        grid = Grid(20, 20)
        grid.place_agent(agent, 5, 5)
        agent.set_grid(grid)
        moves = agent.get_valid_moves()
        self.assertEqual(len(moves), 8)
    
    def test_distance_to(self):
        agent1 = MockAgent("Agent1", 5, 5)
        agent2 = MockAgent("Agent2", 7, 7)
        grid = Grid(20, 20)
        agent1.set_grid(grid)
        
        distance = agent1.distance_to(agent2)
        self.assertEqual(distance, 2)
    
    def test_distance_to_position(self):
        agent = MockAgent("Test", 5, 5)
        grid = Grid(20, 20)
        agent.set_grid(grid)
        
        distance = agent.distance_to_position(10, 10)
        self.assertEqual(distance, 5)


class TestAgentStep(unittest.TestCase):
    
    def test_step_increments_age(self):
        agent = MockAgent()
        grid = Grid(20, 20)
        agent.set_grid(grid)
        
        agent.step()
        self.assertEqual(agent.age, 1)
    
    def test_step_restores_stamina_every_10(self):
        agent = MockAgent()
        grid = Grid(20, 20)
        agent.set_grid(grid)
        agent.stamina = 50
        
        for _ in range(10):
            agent.step()
        
        self.assertEqual(agent.stamina, 55)
    
    def test_step_dead_agent(self):
        agent = MockAgent()
        agent.is_alive = False
        initial_age = agent.age
        agent.step()
        self.assertEqual(agent.age, initial_age)


class TestPredatorAgent(unittest.TestCase):
    
    def test_predator_creation(self):
        predator = PredatorAgent("Hunter", 5, 10)
        self.assertEqual(predator.name, "Hunter")
        self.assertEqual(predator.x, 5)
        self.assertEqual(predator.y, 10)
    
    def test_predator_default_stats(self):
        predator = PredatorAgent("Hunter")
        self.assertEqual(predator.max_health, 150)
        self.assertEqual(predator.max_stamina, 120)
        self.assertEqual(predator.honour, 0)
        self.assertEqual(predator.reputation, 0)
    
    def test_predator_initial_equipment(self):
        predator = PredatorAgent("Hunter")
        self.assertIn("wrist_blades", predator.weapons)
        self.assertIn("shoulder_cannon", predator.weapons)
        self.assertTrue(predator.thermal_vision)
        self.assertFalse(predator.stealth_active)
    
    def test_predator_symbol(self):
        predator = PredatorAgent("Hunter")
        self.assertEqual(predator.symbol, 'P')
    
    def test_predator_clan_rank_initial(self):
        predator = PredatorAgent("Hunter")
        self.assertEqual(predator.clan_rank, "Unblooded")


class TestPredatorHonour(unittest.TestCase):
    
    def test_gain_honour(self):
        predator = PredatorAgent("Hunter")
        predator.gain_honour(25)
        self.assertEqual(predator.honour, 25)
    
    def test_lose_honour(self):
        predator = PredatorAgent("Hunter")
        predator.honour = 50
        predator.lose_honour(20)
        self.assertEqual(predator.honour, 30)
    
    def test_lose_honour_no_negative(self):
        predator = PredatorAgent("Hunter")
        predator.honour = 10
        predator.lose_honour(30)
        self.assertEqual(predator.honour, 0)
    
    def test_rank_unblooded(self):
        predator = PredatorAgent("Hunter")
        predator.gain_honour(5)
        self.assertEqual(predator.clan_rank, "Unblooded")
    
    def test_rank_young_blood(self):
        predator = PredatorAgent("Hunter")
        predator.gain_honour(15)
        self.assertEqual(predator.clan_rank, "Young Blood")
    
    def test_rank_blooded(self):
        predator = PredatorAgent("Hunter")
        predator.gain_honour(60)
        self.assertEqual(predator.clan_rank, "Blooded")
    
    def test_rank_elder(self):
        predator = PredatorAgent("Hunter")
        predator.gain_honour(120)
        self.assertEqual(predator.clan_rank, "Elder")


class TestPredatorTrophies(unittest.TestCase):
    
    def test_add_trophy(self):
        predator = PredatorAgent("Hunter")
        trophy = {'type': 'skull', 'target': 'beast', 'value': 5}
        predator.add_trophy(trophy)
        self.assertEqual(len(predator.trophies), 1)
        self.assertEqual(predator.honour, 5)
    
    def test_add_multiple_trophies(self):
        predator = PredatorAgent("Hunter")
        predator.add_trophy({'type': 'skull', 'value': 5})
        predator.add_trophy({'type': 'spine', 'value': 3})
        self.assertEqual(len(predator.trophies), 2)
        self.assertEqual(predator.honour, 8)


class TestPredatorStealth(unittest.TestCase):
    
    def test_activate_stealth(self):
        predator = PredatorAgent("Hunter")
        predator.activate_stealth()
        self.assertTrue(predator.stealth_active)
        self.assertEqual(predator.stamina, 100)
    
    def test_activate_stealth_insufficient_stamina(self):
        predator = PredatorAgent("Hunter")
        predator.stamina = 10
        predator.activate_stealth()
        self.assertFalse(predator.stealth_active)
    
    def test_deactivate_stealth(self):
        predator = PredatorAgent("Hunter")
        predator.activate_stealth()
        predator.deactivate_stealth()
        self.assertFalse(predator.stealth_active)


class TestDekAgent(unittest.TestCase):
    
    def test_dek_creation(self):
        dek = Dek(5, 10)
        self.assertEqual(dek.name, "Dek")
        self.assertEqual(dek.x, 5)
        self.assertEqual(dek.y, 10)
    
    def test_dek_stats(self):
        dek = Dek()
        self.assertEqual(dek.max_health, 180)
        self.assertEqual(dek.max_stamina, 150)
        self.assertTrue(dek.is_exiled)
    
    def test_dek_symbol(self):
        dek = Dek()
        self.assertEqual(dek.symbol, 'D')
    
    def test_dek_thia_state(self):
        dek = Dek()
        self.assertFalse(dek.carrying_thia)
        self.assertIsNone(dek.thia_partner)
        self.assertEqual(dek.quest_progress, 0)


class TestDekCarryThia(unittest.TestCase):
    
    def test_carry_thia(self):
        dek = Dek()
        
        class MockThia:
            pass
        
        thia = MockThia()
        dek.carry_thia(thia)
        
        self.assertTrue(dek.carrying_thia)
        self.assertEqual(dek.thia_partner, thia)
        self.assertEqual(dek.max_stamina, 130)
    
    def test_drop_thia(self):
        dek = Dek()
        
        class MockThia:
            pass
        
        thia = MockThia()
        dek.carry_thia(thia)
        dek.drop_thia()
        
        self.assertFalse(dek.carrying_thia)
        self.assertIsNone(dek.thia_partner)
        self.assertEqual(dek.max_stamina, 150)
    
    def test_movement_cost_while_carrying(self):
        dek = Dek()
        grid = Grid(20, 20)
        dek.set_grid(grid)
        
        normal_cost = dek.get_movement_cost(5, 5)
        
        class MockThia:
            pass
        
        dek.carry_thia(MockThia())
        carrying_cost = dek.get_movement_cost(5, 5)
        
        self.assertEqual(carrying_cost, normal_cost * 2)


class TestPredatorBehavior(unittest.TestCase):
    
    def test_decide_action_rest_low_stamina(self):
        predator = PredatorAgent("Hunter")
        predator.stamina = 20
        action = predator.decide_action()
        self.assertEqual(action, "rest")
    
    def test_decide_action_patrol(self):
        predator = PredatorAgent("Hunter")
        grid = Grid(20, 20)
        predator.set_grid(grid)
        grid.place_agent(predator, 5, 5)
        action = predator.decide_action()
        self.assertEqual(action, "patrol")
    
    def test_decide_action_when_dead(self):
        predator = PredatorAgent("Hunter")
        predator.is_alive = False
        action = predator.decide_action()
        self.assertEqual(action, "rest")
    
    def test_hunt_nearby_prey_empty(self):
        predator = PredatorAgent("Hunter")
        grid = Grid(20, 20)
        predator.set_grid(grid)
        grid.place_agent(predator, 10, 10)
        
        prey = predator.hunt_nearby_prey()
        self.assertEqual(prey, [])


if __name__ == '__main__':
    unittest.main()
