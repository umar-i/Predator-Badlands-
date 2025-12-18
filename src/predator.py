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