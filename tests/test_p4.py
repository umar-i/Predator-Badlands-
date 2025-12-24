import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from actions import ActionType, Direction, CombatResult, Trophy, ActionResult
from items import Item, Medkit, EnergyPack, RepairKit, WeaponItem, random_item


class TestActionType(unittest.TestCase):
    
    def test_action_type_values(self):
        self.assertEqual(ActionType.MOVE.value, "move")
        self.assertEqual(ActionType.ATTACK.value, "attack")
        self.assertEqual(ActionType.REST.value, "rest")
        self.assertEqual(ActionType.COLLECT_TROPHY.value, "collect_trophy")
        self.assertEqual(ActionType.STEALTH.value, "stealth")
        self.assertEqual(ActionType.HUNT.value, "hunt")
        self.assertEqual(ActionType.CARRY.value, "carry")
        self.assertEqual(ActionType.DROP.value, "drop")
        self.assertEqual(ActionType.SCAN.value, "scan")
    
    def test_action_type_count(self):
        action_types = list(ActionType)
        self.assertGreaterEqual(len(action_types), 10)


class TestDirection(unittest.TestCase):
    
    def test_direction_values(self):
        self.assertEqual(Direction.NORTH.value, (0, -1))
        self.assertEqual(Direction.SOUTH.value, (0, 1))
        self.assertEqual(Direction.EAST.value, (1, 0))
        self.assertEqual(Direction.WEST.value, (-1, 0))
    
    def test_diagonal_directions(self):
        self.assertEqual(Direction.NORTHEAST.value, (1, -1))
        self.assertEqual(Direction.NORTHWEST.value, (-1, -1))
        self.assertEqual(Direction.SOUTHEAST.value, (1, 1))
        self.assertEqual(Direction.SOUTHWEST.value, (-1, 1))
    
    def test_direction_count(self):
        directions = list(Direction)
        self.assertEqual(len(directions), 8)


class TestCombatResult(unittest.TestCase):
    
    def setUp(self):
        class MockAgent:
            def __init__(self, name, health):
                self.name = name
                self.health = health
        
        self.MockAgent = MockAgent
    
    def test_combat_result_creation(self):
        attacker = self.MockAgent("Attacker", 100)
        defender = self.MockAgent("Defender", 50)
        
        result = CombatResult(attacker, defender, 25, False)
        
        self.assertEqual(result.attacker, attacker)
        self.assertEqual(result.defender, defender)
        self.assertEqual(result.damage_dealt, 25)
        self.assertFalse(result.kill)
    
    def test_combat_result_kill(self):
        attacker = self.MockAgent("Attacker", 100)
        defender = self.MockAgent("Defender", 0)
        
        result = CombatResult(attacker, defender, 50, True)
        self.assertTrue(result.kill)
    
    def test_combat_result_to_dict(self):
        attacker = self.MockAgent("Attacker", 100)
        defender = self.MockAgent("Defender", 25)
        
        result = CombatResult(attacker, defender, 30, False)
        data = result.to_dict()
        
        self.assertEqual(data['attacker'], "Attacker")
        self.assertEqual(data['defender'], "Defender")
        self.assertEqual(data['damage'], 30)
        self.assertFalse(data['kill'])
        self.assertEqual(data['attacker_health'], 100)
        self.assertEqual(data['defender_health'], 25)


class TestTrophy(unittest.TestCase):
    
    def test_trophy_creation(self):
        trophy = Trophy("Beast Skull", "skull", 10, "WildBeast")
        
        self.assertEqual(trophy.name, "Beast Skull")
        self.assertEqual(trophy.trophy_type, "skull")
        self.assertEqual(trophy.value, 10)
        self.assertEqual(trophy.origin_creature, "WildBeast")
    
    def test_trophy_honour_value_skull(self):
        trophy = Trophy("Skull", "skull", 10)
        self.assertEqual(trophy.get_honour_value(), 20)
    
    def test_trophy_honour_value_spine(self):
        trophy = Trophy("Spine", "spine", 10)
        self.assertEqual(trophy.get_honour_value(), 15)
    
    def test_trophy_honour_value_claw(self):
        trophy = Trophy("Claw", "claw", 10)
        self.assertEqual(trophy.get_honour_value(), 10)
    
    def test_trophy_honour_value_artifact(self):
        trophy = Trophy("Ancient Relic", "artifact", 10)
        self.assertEqual(trophy.get_honour_value(), 30)
    
    def test_trophy_honour_value_boss_part(self):
        trophy = Trophy("Boss Heart", "boss_part", 10)
        self.assertEqual(trophy.get_honour_value(), 50)
    
    def test_trophy_honour_value_unknown(self):
        trophy = Trophy("Unknown", "unknown", 10)
        self.assertEqual(trophy.get_honour_value(), 10)
    
    def test_trophy_to_dict(self):
        trophy = Trophy("Test Trophy", "skull", 15, "TestCreature")
        data = trophy.to_dict()
        
        self.assertEqual(data['name'], "Test Trophy")
        self.assertEqual(data['type'], "skull")
        self.assertEqual(data['value'], 15)
        self.assertEqual(data['honour_value'], 30)
        self.assertEqual(data['origin'], "TestCreature")


class TestActionResult(unittest.TestCase):
    
    def test_action_result_creation(self):
        result = ActionResult(ActionType.MOVE, True, 5, "Moved successfully")
        
        self.assertEqual(result.action_type, ActionType.MOVE)
        self.assertTrue(result.success)
        self.assertEqual(result.stamina_cost, 5)
        self.assertEqual(result.message, "Moved successfully")
    
    def test_action_result_failure(self):
        result = ActionResult(ActionType.ATTACK, False, 0, "Target out of range")
        
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Target out of range")
    
    def test_add_combat_result(self):
        class MockAgent:
            def __init__(self, name, health):
                self.name = name
                self.health = health
        
        attacker = MockAgent("A", 100)
        defender = MockAgent("D", 50)
        combat = CombatResult(attacker, defender, 20, False)
        
        result = ActionResult(ActionType.ATTACK, True, 10)
        result.add_combat_result(combat)
        
        self.assertEqual(result.combat_result, combat)
    
    def test_add_trophy(self):
        result = ActionResult(ActionType.COLLECT_TROPHY, True, 5)
        trophy = Trophy("Test", "skull", 10)
        result.add_trophy(trophy)
        
        self.assertEqual(result.trophy_collected, trophy)
    
    def test_action_result_to_dict(self):
        result = ActionResult(ActionType.REST, True, 0, "Resting")
        data = result.to_dict()
        
        self.assertEqual(data['action'], "rest")
        self.assertTrue(data['success'])
        self.assertEqual(data['stamina_cost'], 0)
        self.assertEqual(data['message'], "Resting")


class TestItem(unittest.TestCase):
    
    def test_item_creation(self):
        item = Item("Test Item", "generic", 10)
        
        self.assertEqual(item.name, "Test Item")
        self.assertEqual(item.item_type, "generic")
        self.assertEqual(item.value, 10)
    
    def test_item_symbol(self):
        item = Item("Test", "generic", 5)
        self.assertEqual(item.symbol, '*')
    
    def test_item_apply_default(self):
        item = Item("Test", "generic", 5)
        result = item.apply(None)
        self.assertFalse(result)


class TestMedkit(unittest.TestCase):
    
    def test_medkit_creation(self):
        medkit = Medkit(30)
        
        self.assertEqual(medkit.name, "Medkit")
        self.assertEqual(medkit.item_type, "medkit")
        self.assertEqual(medkit.value, 30)
    
    def test_medkit_default_value(self):
        medkit = Medkit()
        self.assertEqual(medkit.value, 25)
    
    def test_medkit_apply(self):
        class MockAgent:
            def __init__(self):
                self.health = 50
                self.max_health = 100
            
            def heal(self, amount):
                self.health = min(self.max_health, self.health + amount)
        
        agent = MockAgent()
        medkit = Medkit(25)
        result = medkit.apply(agent)
        
        self.assertTrue(result)
        self.assertEqual(agent.health, 75)
    
    def test_medkit_apply_no_heal_needed(self):
        class MockAgent:
            def __init__(self):
                self.health = 100
                self.max_health = 100
            
            def heal(self, amount):
                self.health = min(self.max_health, self.health + amount)
        
        agent = MockAgent()
        medkit = Medkit(25)
        result = medkit.apply(agent)
        
        self.assertFalse(result)


class TestEnergyPack(unittest.TestCase):
    
    def test_energy_pack_creation(self):
        pack = EnergyPack(40)
        
        self.assertEqual(pack.name, "Energy Pack")
        self.assertEqual(pack.item_type, "energy")
        self.assertEqual(pack.value, 40)
    
    def test_energy_pack_default_value(self):
        pack = EnergyPack()
        self.assertEqual(pack.value, 30)
    
    def test_energy_pack_apply(self):
        class MockAgent:
            def __init__(self):
                self.stamina = 50
                self.max_stamina = 100
            
            def restore_stamina(self, amount):
                self.stamina = min(self.max_stamina, self.stamina + amount)
        
        agent = MockAgent()
        pack = EnergyPack(30)
        result = pack.apply(agent)
        
        self.assertTrue(result)
        self.assertEqual(agent.stamina, 80)


class TestRepairKit(unittest.TestCase):
    
    def test_repair_kit_creation(self):
        kit = RepairKit(25)
        
        self.assertEqual(kit.name, "Repair Kit")
        self.assertEqual(kit.item_type, "repair")
        self.assertEqual(kit.value, 25)
    
    def test_repair_kit_default_value(self):
        kit = RepairKit()
        self.assertEqual(kit.value, 20)
    
    def test_repair_kit_apply(self):
        class MockAgent:
            def __init__(self):
                self.damage_level = 40
            
            def repair_damage(self, amount):
                self.damage_level = max(0, self.damage_level - amount)
        
        agent = MockAgent()
        kit = RepairKit(20)
        result = kit.apply(agent)
        
        self.assertTrue(result)
        self.assertEqual(agent.damage_level, 20)
    
    def test_repair_kit_no_damage(self):
        class MockAgent:
            def __init__(self):
                self.damage_level = 0
            
            def repair_damage(self, amount):
                self.damage_level = max(0, self.damage_level - amount)
        
        agent = MockAgent()
        kit = RepairKit(20)
        result = kit.apply(agent)
        
        self.assertFalse(result)


class TestWeaponItem(unittest.TestCase):
    
    def test_weapon_creation(self):
        weapon = WeaponItem("plasma_caster")
        
        self.assertEqual(weapon.name, "plasma_caster")
        self.assertEqual(weapon.item_type, "weapon")
        self.assertEqual(weapon.weapon_name, "plasma_caster")
    
    def test_weapon_apply(self):
        class MockAgent:
            def __init__(self):
                self.weapons = ["wrist_blades"]
        
        agent = MockAgent()
        weapon = WeaponItem("net_gun")
        result = weapon.apply(agent)
        
        self.assertTrue(result)
        self.assertIn("net_gun", agent.weapons)
    
    def test_weapon_apply_already_owned(self):
        class MockAgent:
            def __init__(self):
                self.weapons = ["plasma_caster"]
        
        agent = MockAgent()
        weapon = WeaponItem("plasma_caster")
        result = weapon.apply(agent)
        
        self.assertFalse(result)
        self.assertEqual(agent.weapons.count("plasma_caster"), 1)


class TestRandomItem(unittest.TestCase):
    
    def test_random_item_returns_item(self):
        item = random_item()
        self.assertIsNotNone(item)
        self.assertTrue(hasattr(item, 'name'))
        self.assertTrue(hasattr(item, 'item_type'))
    
    def test_random_item_types(self):
        item_types = set()
        for _ in range(100):
            item = random_item()
            item_types.add(item.item_type)
        
        self.assertIn("medkit", item_types)
        self.assertIn("energy", item_types)


if __name__ == '__main__':
    unittest.main()
