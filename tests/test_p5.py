import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from creatures import WildlifeAgent, BossAdversary
from synthetic import SyntheticAgent, Thia
from grid import Grid


class TestWildlifeAgent(unittest.TestCase):
    
    def test_wildlife_creation(self):
        wildlife = WildlifeAgent("Beast", "carnivore", 5, 10)
        
        self.assertEqual(wildlife.name, "Beast")
        self.assertEqual(wildlife.species, "carnivore")
        self.assertEqual(wildlife.x, 5)
        self.assertEqual(wildlife.y, 10)
    
    def test_wildlife_default_stats(self):
        wildlife = WildlifeAgent("Beast", "herbivore")
        
        self.assertEqual(wildlife.max_health, 50)
        self.assertEqual(wildlife.max_stamina, 80)
        self.assertTrue(wildlife.is_prey)
    
    def test_wildlife_symbol(self):
        wildlife = WildlifeAgent("Beast", "carnivore")
        self.assertEqual(wildlife.symbol, 'W')
    
    def test_wildlife_aggression(self):
        wildlife = WildlifeAgent("Beast", "carnivore")
        self.assertEqual(wildlife.aggression_level, 0.2)
        self.assertEqual(wildlife.territory_size, 3)
    
    def test_set_aggression(self):
        wildlife = WildlifeAgent("Beast", "carnivore")
        wildlife.set_aggression(0.7)
        self.assertEqual(wildlife.aggression_level, 0.7)
    
    def test_set_aggression_clamp_high(self):
        wildlife = WildlifeAgent("Beast", "carnivore")
        wildlife.set_aggression(1.5)
        self.assertEqual(wildlife.aggression_level, 1.0)
    
    def test_set_aggression_clamp_low(self):
        wildlife = WildlifeAgent("Beast", "carnivore")
        wildlife.set_aggression(-0.5)
        self.assertEqual(wildlife.aggression_level, 0.0)
    
    def test_add_pack_member(self):
        wildlife1 = WildlifeAgent("Beast1", "carnivore")
        wildlife2 = WildlifeAgent("Beast2", "carnivore")
        
        wildlife1.add_pack_member(wildlife2)
        
        self.assertIn(wildlife2, wildlife1.pack_members)
        self.assertIn(wildlife1, wildlife2.pack_members)


class TestWildlifeBehavior(unittest.TestCase):
    
    def test_detect_threats_empty(self):
        wildlife = WildlifeAgent("Beast", "herbivore")
        grid = Grid(20, 20)
        wildlife.set_grid(grid)
        grid.place_agent(wildlife, 10, 10)
        
        threats = wildlife.detect_threats()
        self.assertEqual(threats, [])
    
    def test_decide_action_rest_low_stamina(self):
        wildlife = WildlifeAgent("Beast", "herbivore")
        wildlife.stamina = 15
        grid = Grid(20, 20)
        wildlife.set_grid(grid)
        
        action = wildlife.decide_action()
        self.assertEqual(action, "rest")
    
    def test_decide_action_forage(self):
        wildlife = WildlifeAgent("Beast", "herbivore")
        grid = Grid(20, 20)
        wildlife.set_grid(grid)
        grid.place_agent(wildlife, 10, 10)
        
        action = wildlife.decide_action()
        self.assertEqual(action, "forage")
    
    def test_decide_action_dead(self):
        wildlife = WildlifeAgent("Beast", "herbivore")
        wildlife.is_alive = False
        
        action = wildlife.decide_action()
        self.assertEqual(action, "rest")


class TestBossAdversary(unittest.TestCase):
    
    def test_boss_creation(self):
        boss = BossAdversary("Nemesis", 15, 15)
        
        self.assertEqual(boss.name, "Nemesis")
        self.assertEqual(boss.x, 15)
        self.assertEqual(boss.y, 15)
    
    def test_boss_default_creation(self):
        boss = BossAdversary()
        
        self.assertEqual(boss.name, "Ultimate Adversary")
        self.assertEqual(boss.x, 10)
        self.assertEqual(boss.y, 10)
    
    def test_boss_stats(self):
        boss = BossAdversary()
        
        self.assertEqual(boss.max_health, 150)
        self.assertEqual(boss.max_stamina, 300)
        self.assertEqual(boss.size, 3)
        self.assertEqual(boss.attack_range, 2)
    
    def test_boss_symbol(self):
        boss = BossAdversary()
        self.assertEqual(boss.symbol, 'B')
    
    def test_boss_special_abilities(self):
        boss = BossAdversary()
        
        self.assertIn("earthquake", boss.special_abilities)
        self.assertIn("energy_blast", boss.special_abilities)
        self.assertIn("regeneration", boss.special_abilities)
    
    def test_boss_initial_state(self):
        boss = BossAdversary()
        
        self.assertEqual(boss.rage_level, 0)
        self.assertEqual(boss.phase, 1)
        self.assertIsNone(boss.last_attacker)
        self.assertIsNone(boss.focus_target)


class TestBossEnrage(unittest.TestCase):
    
    def test_is_not_enraged_initial(self):
        boss = BossAdversary()
        self.assertFalse(boss.is_enraged)
    
    def test_is_enraged_at_50(self):
        boss = BossAdversary()
        boss.rage_level = 50
        self.assertTrue(boss.is_enraged)
    
    def test_is_enraged_above_50(self):
        boss = BossAdversary()
        boss.rage_level = 75
        self.assertTrue(boss.is_enraged)


class TestBossDamage(unittest.TestCase):
    
    def test_take_damage_increases_rage(self):
        boss = BossAdversary()
        initial_rage = boss.rage_level
        
        boss.take_damage(20)
        
        self.assertGreater(boss.rage_level, initial_rage)
        self.assertEqual(boss.rage_level, 10)
    
    def test_take_damage_phase_transition(self):
        boss = BossAdversary()
        boss.health = 100  # 66% of 150 HP
        
        boss.take_damage(30)  # Drop to ~47% triggers phase 2
        
        self.assertEqual(boss.phase, 2)
    
    def test_take_damage_no_phase_transition(self):
        boss = BossAdversary()
        boss.take_damage(50)
        
        self.assertEqual(boss.phase, 1)


class TestBossActions(unittest.TestCase):
    
    def test_decide_action_dead(self):
        boss = BossAdversary()
        boss.is_alive = False
        
        action = boss.decide_action()
        self.assertEqual(action, "rest")
    
    def test_decide_action_no_enemies(self):
        boss = BossAdversary()
        grid = Grid(30, 30)
        boss.set_grid(grid)
        grid.place_agent(boss, 15, 15)
        
        action = boss.decide_action()
        self.assertEqual(action, "patrol")
    
    def test_decide_action_low_health(self):
        boss = BossAdversary()
        boss.health = 30  # 20% of 150 HP - actually low health
        grid = Grid(30, 30)
        boss.set_grid(grid)
        grid.place_agent(boss, 15, 15)
        
        from predator import Dek
        enemy = Dek(16, 15)  # Use Dek which has is_exiled attribute
        enemy.set_grid(grid)
        grid.place_agent(enemy, 16, 15)
        
        action = boss.decide_action()
        self.assertEqual(action, "regenerate")


class TestSyntheticAgent(unittest.TestCase):
    
    def test_synthetic_creation(self):
        synth = SyntheticAgent("Android", "Model-X", 5, 10)
        
        self.assertEqual(synth.name, "Android")
        self.assertEqual(synth.model, "Model-X")
        self.assertEqual(synth.x, 5)
        self.assertEqual(synth.y, 10)
    
    def test_synthetic_stats(self):
        synth = SyntheticAgent("Android", "Test")
        
        self.assertEqual(synth.max_health, 80)
        self.assertEqual(synth.max_stamina, 200)
        self.assertEqual(synth.battery_level, 100)
        self.assertEqual(synth.damage_level, 0)
        self.assertEqual(synth.malfunction_chance, 0.0)
    
    def test_synthetic_symbol(self):
        synth = SyntheticAgent("Android", "Test")
        self.assertEqual(synth.symbol, 'S')
    
    def test_is_functional(self):
        synth = SyntheticAgent("Android", "Test")
        self.assertTrue(synth.is_functional)
    
    def test_is_not_functional_no_battery(self):
        synth = SyntheticAgent("Android", "Test")
        synth.battery_level = 0
        self.assertFalse(synth.is_functional)
    
    def test_is_not_functional_high_damage(self):
        synth = SyntheticAgent("Android", "Test")
        synth.damage_level = 85
        self.assertFalse(synth.is_functional)


class TestSyntheticBattery(unittest.TestCase):
    
    def test_consume_battery(self):
        synth = SyntheticAgent("Android", "Test")
        synth.consume_battery(30)
        
        self.assertEqual(synth.battery_level, 70)
    
    def test_consume_battery_depleted(self):
        synth = SyntheticAgent("Android", "Test")
        synth.consume_battery(150)
        
        self.assertEqual(synth.battery_level, 0)
        self.assertFalse(synth.is_alive)
    
    def test_recharge_battery(self):
        synth = SyntheticAgent("Android", "Test")
        synth.battery_level = 50
        synth.recharge_battery(30)
        
        self.assertEqual(synth.battery_level, 80)
    
    def test_recharge_battery_max(self):
        synth = SyntheticAgent("Android", "Test")
        synth.battery_level = 90
        synth.recharge_battery(30)
        
        self.assertEqual(synth.battery_level, 100)
    
    def test_recharge_revives(self):
        synth = SyntheticAgent("Android", "Test")
        synth.battery_level = 0
        synth.is_alive = False
        
        synth.recharge_battery(20)
        
        self.assertTrue(synth.is_alive)


class TestSyntheticDamage(unittest.TestCase):
    
    def test_take_damage_increases_damage_level(self):
        synth = SyntheticAgent("Android", "Test")
        synth.take_damage(20)
        
        self.assertEqual(synth.damage_level, 10)
    
    def test_take_damage_malfunction_chance(self):
        synth = SyntheticAgent("Android", "Test")
        synth.take_damage(120)
        
        self.assertGreater(synth.malfunction_chance, 0)
    
    def test_repair_damage(self):
        synth = SyntheticAgent("Android", "Test")
        synth.damage_level = 50
        synth.repair_damage(20)
        
        self.assertEqual(synth.damage_level, 30)
    
    def test_repair_damage_no_negative(self):
        synth = SyntheticAgent("Android", "Test")
        synth.damage_level = 10
        synth.repair_damage(30)
        
        self.assertEqual(synth.damage_level, 0)


class TestSyntheticKnowledge(unittest.TestCase):
    
    def test_add_knowledge(self):
        synth = SyntheticAgent("Android", "Test")
        synth.add_knowledge("location", "base_camp")
        
        self.assertEqual(synth.knowledge_database["location"], "base_camp")
    
    def test_get_knowledge_exists(self):
        synth = SyntheticAgent("Android", "Test")
        synth.add_knowledge("secret", "hidden_value")
        
        result = synth.get_knowledge("secret")
        self.assertEqual(result, "hidden_value")
    
    def test_get_knowledge_not_exists(self):
        synth = SyntheticAgent("Android", "Test")
        result = synth.get_knowledge("nonexistent")
        self.assertIsNone(result)


class TestThia(unittest.TestCase):
    
    def test_thia_creation(self):
        thia = Thia(5, 10)
        
        self.assertEqual(thia.name, "Thia")
        self.assertEqual(thia.model, "Weyland-Yutani")
        self.assertEqual(thia.x, 5)
        self.assertEqual(thia.y, 10)
    
    def test_thia_stats(self):
        thia = Thia()
        
        self.assertEqual(thia.max_health, 60)
        self.assertEqual(thia.max_stamina, 150)
        self.assertEqual(thia.damage_level, 40)
        self.assertTrue(thia.missing_limb)
    
    def test_thia_symbol(self):
        thia = Thia()
        self.assertEqual(thia.symbol, 'T')
    
    def test_thia_mobility(self):
        thia = Thia()
        self.assertEqual(thia.mobility_rating, 2)
    
    def test_thia_cooperation(self):
        thia = Thia()
        
        self.assertEqual(thia.cooperation_level, 0)
        self.assertEqual(thia.trust_in_dek, 0)


class TestThiaMobility(unittest.TestCase):
    
    def test_cannot_move_independently_initial(self):
        thia = Thia()
        self.assertFalse(thia.can_move_independently)
    
    def test_can_move_independently_repaired(self):
        thia = Thia()
        thia.missing_limb = False
        thia.damage_level = 30
        thia.carried_by = None
        
        self.assertTrue(thia.can_move_independently)
    
    def test_cannot_move_independently_carried(self):
        thia = Thia()
        thia.missing_limb = False
        thia.damage_level = 30
        thia.carried_by = "Dek"
        
        self.assertFalse(thia.can_move_independently)
    
    def test_movement_penalty(self):
        thia = Thia()
        penalty = thia.movement_penalty
        
        self.assertGreater(penalty, 0)
    
    def test_movement_penalty_limb(self):
        thia = Thia()
        with_limb_missing = thia.movement_penalty
        
        thia.missing_limb = False
        without_limb_missing = thia.movement_penalty
        
        self.assertGreater(with_limb_missing, without_limb_missing)


class TestThiaIntel(unittest.TestCase):
    
    def test_intel_database_initialized(self):
        thia = Thia()
        
        self.assertIn('adversary_weakness', thia.intel_database)
        self.assertEqual(thia.intel_database['adversary_weakness']['type'], 'weakness')


class TestSyntheticScan(unittest.TestCase):
    
    def test_scan_area_no_grid(self):
        synth = SyntheticAgent("Android", "Test")
        results = synth.scan_area()
        self.assertEqual(results, [])
    
    def test_scan_area_not_functional(self):
        synth = SyntheticAgent("Android", "Test")
        synth.battery_level = 0
        grid = Grid(20, 20)
        synth.set_grid(grid)
        
        results = synth.scan_area()
        self.assertEqual(results, [])
    
    def test_scan_area_empty(self):
        synth = SyntheticAgent("Android", "Test")
        grid = Grid(20, 20)
        synth.set_grid(grid)
        grid.place_agent(synth, 10, 10)
        
        results = synth.scan_area()
        self.assertEqual(results, [])


class TestSyntheticDecision(unittest.TestCase):
    
    def test_decide_action_dead(self):
        synth = SyntheticAgent("Android", "Test")
        synth.is_alive = False
        
        action = synth.decide_action()
        self.assertEqual(action, "shutdown")
    
    def test_decide_action_low_battery(self):
        synth = SyntheticAgent("Android", "Test")
        synth.battery_level = 15
        
        action = synth.decide_action()
        self.assertEqual(action, "conserve_power")
    
    def test_decide_action_normal(self):
        synth = SyntheticAgent("Android", "Test")
        synth.malfunction_chance = 0.0
        
        action = synth.decide_action()
        self.assertEqual(action, "operate")


if __name__ == '__main__':
    unittest.main()
