from enum import Enum


class ActionType(Enum):
    MOVE = "move"
    ATTACK = "attack"
    REST = "rest"
    COLLECT_TROPHY = "collect_trophy"
    STEALTH = "stealth"
    HUNT = "hunt"
    CARRY = "carry"
    DROP = "drop"


class Direction(Enum):
    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST = (1, 0)
    WEST = (-1, 0)
    NORTHEAST = (1, -1)
    NORTHWEST = (-1, -1)
    SOUTHEAST = (1, 1)
    SOUTHWEST = (-1, 1)


class CombatResult:
    
    def __init__(self, attacker, defender, damage_dealt, kill=False):
        self.attacker = attacker
        self.defender = defender
        self.damage_dealt = damage_dealt
        self.kill = kill
        self.timestamp = 0
    
    def to_dict(self):
        return {
            'attacker': self.attacker.name,
            'defender': self.defender.name,
            'damage': self.damage_dealt,
            'kill': self.kill,
            'timestamp': self.timestamp,
            'attacker_health': self.attacker.health,
            'defender_health': self.defender.health
        }


class Trophy:
    
    def __init__(self, name, trophy_type, value, origin_creature=None):
        self.name = name
        self.trophy_type = trophy_type
        self.value = value
        self.origin_creature = origin_creature
        self.collected_at = 0
    
    def get_honour_value(self):
        multipliers = {
            'skull': 2.0,
            'spine': 1.5,
            'claw': 1.0,
            'artifact': 3.0,
            'boss_part': 5.0
        }
        return int(self.value * multipliers.get(self.trophy_type, 1.0))
    
    def to_dict(self):
        return {
            'name': self.name,
            'type': self.trophy_type,
            'value': self.value,
            'honour_value': self.get_honour_value(),
            'origin': self.origin_creature,
            'collected_at': self.collected_at
        }


class ActionResult:
    
    def __init__(self, action_type, success, stamina_cost=0, message=""):
        self.action_type = action_type
        self.success = success
        self.stamina_cost = stamina_cost
        self.message = message
        self.combat_result = None
        self.trophy_collected = None
    
    def add_combat_result(self, combat_result):
        self.combat_result = combat_result
    
    def add_trophy(self, trophy):
        self.trophy_collected = trophy
    
    def to_dict(self):
        result = {
            'action': self.action_type.value,
            'success': self.success,
            'stamina_cost': self.stamina_cost,
            'message': self.message
        }
        
        if self.combat_result:
            result['combat'] = self.combat_result.to_dict()
        
        if self.trophy_collected:
            result['trophy'] = self.trophy_collected.to_dict()
        
        return result