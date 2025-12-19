from agent import Agent
import random


class PredatorAgent(Agent):
    
    def __init__(self, name, x=0, y=0, max_health=150, max_stamina=120):
        super().__init__(name, x, y, max_health, max_stamina)
        self.honour = 0
        self.reputation = 0
        self.trophies = []
        self.clan_rank = "Unblooded"
        self.weapons = ["wrist_blades", "shoulder_cannon"]
        self.thermal_vision = True
        self.stealth_active = False
        
    @property
    def symbol(self):
        return 'P'
    
    def add_trophy(self, trophy):
        self.trophies.append(trophy)
        self.honour += trophy.get('value', 1)
    
    def gain_honour(self, amount):
        self.honour += amount
        self.update_rank()
    
    def lose_honour(self, amount):
        self.honour = max(0, self.honour - amount)
        self.update_rank()
    
    def update_rank(self):
        if self.honour >= 100:
            self.clan_rank = "Elder"
        elif self.honour >= 50:
            self.clan_rank = "Blooded"
        elif self.honour >= 10:
            self.clan_rank = "Young Blood"
        else:
            self.clan_rank = "Unblooded"
    
    def activate_stealth(self):
        if self.stamina >= 20:
            self.stealth_active = True
            self.consume_stamina(20)
    
    def deactivate_stealth(self):
        self.stealth_active = False
    
    def hunt_nearby_prey(self):
        if not self.grid:
            return None
        
        nearby_cells = self.grid.get_cells_in_radius(self.x, self.y, 3)
        prey_targets = []
        
        for cell in nearby_cells:
            if cell.occupant and cell.occupant != self:
                if hasattr(cell.occupant, 'is_prey') and cell.occupant.is_prey:
                    prey_targets.append(cell.occupant)
        
        return prey_targets
    
    def decide_action(self):
        if not self.can_act():
            return "rest"
        
        if self.stamina < 30:
            return "rest"
        
        prey = self.hunt_nearby_prey()
        if prey:
            return "hunt"
        
        return "patrol"
    
    def patrol_movement(self):
        valid_moves = self.get_valid_moves()
        if valid_moves:
            target_x, target_y = random.choice(valid_moves)
            return self.move_to(target_x, target_y)
        return False
    
    def update(self):
        if self.stealth_active:
            self.consume_stamina(2)
            if self.stamina < 10:
                self.deactivate_stealth()
        
        action = self.decide_action()
        
        if action == "rest":
            self.restore_stamina(10)
        elif action == "patrol":
            self.patrol_movement()
        elif action == "hunt":
            self.hunt_behavior()
    
    def hunt_behavior(self):
        prey = self.hunt_nearby_prey()
        if prey:
            target = min(prey, key=lambda p: self.distance_to(p))
            if self.distance_to(target) == 1:
                self.attack_target(target)
            else:
                self.move_towards(target)
    
    def move_towards(self, target):
        best_move = None
        best_distance = float('inf')
        
        for x, y in self.get_valid_moves():
            distance = self.distance_to_position(x, y)
            if distance < best_distance:
                best_distance = distance
                best_move = (x, y)
        
        if best_move:
            self.move_to(best_move[0], best_move[1])
    
    def attack_target(self, target):
        if self.distance_to(target) == 1:
            damage = random.randint(15, 25)
            target.take_damage(damage)
            if not target.is_alive:
                self.gain_honour(5)
                self.add_trophy({'type': 'kill', 'target': target.name, 'value': 3})


class Dek(PredatorAgent):
    
    def __init__(self, x=0, y=0):
        super().__init__("Dek", x, y, max_health=120, max_stamina=100)
        self.is_exiled = True
        self.carrying_thia = False
        self.thia_partner = None
        self.quest_progress = 0
        
    @property
    def symbol(self):
        return 'D'
    
    def carry_thia(self, thia_agent):
        self.carrying_thia = True
        self.thia_partner = thia_agent
        self.max_stamina -= 20
    
    def drop_thia(self):
        self.carrying_thia = False
        if self.thia_partner:
            self.max_stamina += 20
            self.thia_partner = None
    
    def get_movement_cost(self, x, y):
        base_cost = super().get_movement_cost(x, y)
        if self.carrying_thia:
            base_cost *= 2
        return base_cost
    
    def perform_action(self, action_type, direction=None, target=None):
        from actions import ActionResult, ActionType, Direction, CombatResult, Trophy
        
        if not self.can_act():
            return ActionResult(action_type, False, 0, "Cannot act - not alive")
        
        if action_type == ActionType.MOVE:
            return self.perform_move(direction)
        elif action_type == ActionType.ATTACK:
            return self.perform_attack(target)
        elif action_type == ActionType.REST:
            return self.perform_rest()
        elif action_type == ActionType.COLLECT_TROPHY:
            return self.perform_collect_trophy(target)
        elif action_type == ActionType.STEALTH:
            return self.perform_stealth()
        elif action_type == ActionType.CARRY:
            return self.perform_carry(target)
        elif action_type == ActionType.DROP:
            return self.perform_drop()
        
        return ActionResult(action_type, False, 0, "Unknown action type")
    
    def perform_move(self, direction):
        from actions import ActionResult, ActionType, Direction
        
        if direction not in Direction:
            return ActionResult(ActionType.MOVE, False, 0, "Invalid direction")
        
        dx, dy = direction.value
        new_x = self.x + dx
        new_y = self.y + dy
        
        base_cost = 5
        if self.carrying_thia:
            base_cost = 10
        
        if not self.consume_stamina(base_cost):
            return ActionResult(ActionType.MOVE, False, 0, "Insufficient stamina")
        
        if self.move_to(new_x, new_y):
            message = f"Moved {direction.name.lower()}"
            if self.carrying_thia:
                message += " (carrying Thia)"
            return ActionResult(ActionType.MOVE, True, base_cost, message)
        else:
            self.restore_stamina(base_cost)
            return ActionResult(ActionType.MOVE, False, 0, "Path blocked or invalid")
    
    def perform_attack(self, target):
        from actions import ActionResult, ActionType, CombatResult, Trophy
        import random
        
        if not target or not target.is_alive:
            return ActionResult(ActionType.ATTACK, False, 0, "No valid target")
        
        if self.distance_to(target) > 1:
            return ActionResult(ActionType.ATTACK, False, 0, "Target out of range")
        
        if not self.consume_stamina(15):
            return ActionResult(ActionType.ATTACK, False, 0, "Insufficient stamina for attack")
        
        base_damage = random.randint(20, 35)
        if self.stealth_active:
            base_damage = int(base_damage * 1.5)
            self.deactivate_stealth()
        
        target.take_damage(base_damage)
        
        kill = not target.is_alive
        combat_result = CombatResult(self, target, base_damage, kill)
        
        result = ActionResult(ActionType.ATTACK, True, 15, f"Attacked {target.name}")
        result.add_combat_result(combat_result)
        
        if kill:
            self.gain_honour(5)
            trophy = self.create_trophy_from_kill(target)
            if trophy:
                self.add_trophy(trophy)
                result.add_trophy(trophy)
        
        return result
    
    def perform_rest(self):
        from actions import ActionResult, ActionType
        
        stamina_gained = 20
        health_gained = 5
        
        self.restore_stamina(stamina_gained)
        self.heal(health_gained)
        
        message = f"Rested: +{stamina_gained} stamina, +{health_gained} health"
        return ActionResult(ActionType.REST, True, 0, message)
    
    def perform_collect_trophy(self, target):
        from actions import ActionResult, ActionType, Trophy
        
        if not target or target.is_alive:
            return ActionResult(ActionType.COLLECT_TROPHY, False, 0, "Target must be dead to collect trophy")
        
        if self.distance_to(target) > 1:
            return ActionResult(ActionType.COLLECT_TROPHY, False, 0, "Too far from target")
        
        if not self.consume_stamina(10):
            return ActionResult(ActionType.COLLECT_TROPHY, False, 0, "Insufficient stamina")
        
        trophy = self.create_trophy_from_kill(target)
        if trophy:
            self.add_trophy(trophy)
            result = ActionResult(ActionType.COLLECT_TROPHY, True, 10, f"Collected trophy from {target.name}")
            result.add_trophy(trophy)
            return result
        
        return ActionResult(ActionType.COLLECT_TROPHY, False, 10, "No trophy available")
    
    def perform_stealth(self):
        from actions import ActionResult, ActionType
        
        if self.stealth_active:
            self.deactivate_stealth()
            return ActionResult(ActionType.STEALTH, True, 0, "Stealth deactivated")
        else:
            if self.consume_stamina(25):
                self.activate_stealth()
                return ActionResult(ActionType.STEALTH, True, 25, "Stealth activated")
            else:
                return ActionResult(ActionType.STEALTH, False, 0, "Insufficient stamina for stealth")
    
    def perform_carry(self, target):
        from actions import ActionResult, ActionType
        
        if self.carrying_thia:
            return ActionResult(ActionType.CARRY, False, 0, "Already carrying Thia")
        
        if not hasattr(target, 'model') or target.name != "Thia":
            return ActionResult(ActionType.CARRY, False, 0, "Can only carry Thia")
        
        if self.distance_to(target) > 1:
            return ActionResult(ActionType.CARRY, False, 0, "Too far from Thia")
        
        self.carry_thia(target)
        target.be_carried_by(self)
        return ActionResult(ActionType.CARRY, True, 0, "Now carrying Thia")
    
    def perform_drop(self):
        from actions import ActionResult, ActionType
        
        if not self.carrying_thia:
            return ActionResult(ActionType.DROP, False, 0, "Not carrying anyone")
        
        thia = self.thia_partner
        self.drop_thia()
        thia.be_dropped()
        return ActionResult(ActionType.DROP, True, 0, "Dropped Thia")
    
    def create_trophy_from_kill(self, target):
        from actions import Trophy
        import random
        
        trophy_types = {
            'WildlifeAgent': [('claw', 2), ('skull', 3)],
            'SyntheticAgent': [('circuit', 1), ('core', 4)],
            'BossAdversary': [('boss_part', 10), ('artifact', 15)]
        }
        
        target_class = target.__class__.__name__
        if target_class in trophy_types:
            trophy_options = trophy_types[target_class]
            trophy_name, trophy_value = random.choice(trophy_options)
            
            return Trophy(
                f"{target.name} {trophy_name}",
                trophy_name,
                trophy_value,
                target.name
            )
        
        return None
    
    def decide_action(self):
        if not self.can_act():
            return "rest"
        
        if self.stamina < 20:
            return "rest"
        
        if self.quest_progress < 10:
            return "explore"
        
        return super().decide_action()
    
    def update(self):
        action = self.decide_action()
        
        if action == "rest":
            self.restore_stamina(8)
        elif action == "explore":
            self.exploration_movement()
            self.quest_progress += 1
        else:
            super().update()
    
    def exploration_movement(self):
        unexplored_moves = []
        for x, y in self.get_valid_moves():
            cell = self.grid.get_cell(x, y)
            if cell.terrain.terrain_type.name in ['TELEPORT', 'CANYON', 'ROCKY']:
                unexplored_moves.append((x, y))
        
        if unexplored_moves:
            target_x, target_y = random.choice(unexplored_moves)
            self.move_to(target_x, target_y)
        else:
            self.patrol_movement()


class PredatorClan(PredatorAgent):
    
    def __init__(self, name, x=0, y=0, clan_role="warrior"):
        super().__init__(name, x, y, max_health=140, max_stamina=110)
        self.clan_role = clan_role
        self.territory_center = (x, y)
        self.patrol_radius = 5
        
    @property
    def symbol(self):
        return 'C'
    
    def is_in_territory(self):
        distance = self.distance_to_position(self.territory_center[0], self.territory_center[1])
        return distance <= self.patrol_radius
    
    def decide_action(self):
        if not self.can_act():
            return "rest"
        
        if not self.is_in_territory():
            return "return_territory"
        
        return super().decide_action()
    
    def return_to_territory(self):
        tx, ty = self.territory_center
        if self.distance_to_position(tx, ty) > 1:
            best_move = None
            best_distance = float('inf')
            
            for x, y in self.get_valid_moves():
                distance = self.distance_to_position(x, y)
                if distance < best_distance:
                    best_distance = distance
                    best_move = (x, y)
            
            if best_move:
                self.move_to(best_move[0], best_move[1])
    
    def update(self):
        action = self.decide_action()
        
        if action == "return_territory":
            self.return_to_territory()
        else:
            super().update()