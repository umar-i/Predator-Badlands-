import random


class Item:
    def __init__(self, name, item_type, value):
        self.name = name
        self.item_type = item_type
        self.value = value
    def apply(self, agent):
        return False
    @property
    def symbol(self):
        return '*'


class Medkit(Item):
    def __init__(self, value=25):
        super().__init__("Medkit", "medkit", value)
    def apply(self, agent):
        if hasattr(agent, 'heal'):
            before = agent.health
            agent.heal(self.value)
            return agent.health > before
        return False


class EnergyPack(Item):
    def __init__(self, value=30):
        super().__init__("Energy Pack", "energy", value)
    def apply(self, agent):
        if hasattr(agent, 'restore_stamina'):
            before = agent.stamina
            agent.restore_stamina(self.value)
            return agent.stamina > before
        return False


class RepairKit(Item):
    def __init__(self, value=20):
        super().__init__("Repair Kit", "repair", value)
    def apply(self, agent):
        if hasattr(agent, 'repair_damage'):
            before = getattr(agent, 'damage_level', 0)
            agent.repair_damage(self.value)
            after = getattr(agent, 'damage_level', 0)
            return after < before
        return False


class WeaponItem(Item):
    def __init__(self, weapon_name):
        super().__init__(weapon_name, "weapon", 1)
        self.weapon_name = weapon_name
    def apply(self, agent):
        if hasattr(agent, 'weapons'):
            if self.weapon_name not in agent.weapons:
                agent.weapons.append(self.weapon_name)
                return True
        return False


def random_item():
    roll = random.random()
    if roll < 0.35:
        return Medkit(random.randint(15, 35))
    if roll < 0.7:
        return EnergyPack(random.randint(20, 40))
    if roll < 0.9:
        return RepairKit(random.randint(15, 30))
    return WeaponItem(random.choice(["net_gun", "plasma_caster", "combistick"]))
