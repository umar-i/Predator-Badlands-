from agent import Agent
import random


class SyntheticAgent(Agent):
    
    def __init__(self, name, model, x=0, y=0, max_health=80, max_stamina=200):
        super().__init__(name, x, y, max_health, max_stamina)
        self.model = model
        self.damage_level = 0
        self.knowledge_database = {}
        self.battery_level = 100
        self.malfunction_chance = 0.0
        
    @property
    def symbol(self):
        return 'S'
    
    @property
    def is_functional(self):
        return self.battery_level > 0 and self.damage_level < 80
    
    def take_damage(self, amount):
        super().take_damage(amount)
        self.damage_level += amount * 0.5
        if self.damage_level > 50:
            self.malfunction_chance = min(0.3, self.damage_level / 100)
    
    def repair_damage(self, amount):
        self.damage_level = max(0, self.damage_level - amount)
        self.malfunction_chance = max(0, self.damage_level / 100 - 0.5)
    
    def consume_battery(self, amount):
        self.battery_level = max(0, self.battery_level - amount)
        if self.battery_level <= 0:
            self.is_alive = False
    
    def recharge_battery(self, amount):
        self.battery_level = min(100, self.battery_level + amount)
        if self.battery_level > 0:
            self.is_alive = True
    
    def add_knowledge(self, key, value):
        self.knowledge_database[key] = value
    
    def get_knowledge(self, key):
        return self.knowledge_database.get(key, None)
    
    def scan_area(self):
        if not self.grid or not self.is_functional:
            return []
        
        scan_results = []
        nearby_cells = self.grid.get_cells_in_radius(self.x, self.y, 4)
        
        for cell in nearby_cells:
            if cell.occupant and cell.occupant != self:
                scan_results.append({
                    'type': 'agent',
                    'position': cell.position,
                    'agent': cell.occupant
                })
            if cell.terrain.is_hazardous:
                scan_results.append({
                    'type': 'hazard',
                    'position': cell.position,
                    'terrain': cell.terrain.terrain_type
                })
        
        return scan_results
    
    def decide_action(self):
        if not self.can_act() or not self.is_functional:
            return "shutdown"
        
        if self.battery_level < 20:
            return "conserve_power"
        
        if random.random() < self.malfunction_chance:
            return "malfunction"
        
        return "operate"
    
    def update(self):
        self.consume_battery(1)
        
        action = self.decide_action()
        
        if action == "shutdown":
            return
        elif action == "conserve_power":
            self.recharge_battery(2)
        elif action == "malfunction":
            self.random_malfunction()
        elif action == "operate":
            self.normal_operation()
    
    def random_malfunction(self):
        malfunctions = ["move_random", "stutter", "shutdown_brief"]
        malfunction = random.choice(malfunctions)
        
        if malfunction == "move_random":
            valid_moves = self.get_valid_moves()
            if valid_moves:
                x, y = random.choice(valid_moves)
                self.move_to(x, y)
        elif malfunction == "stutter":
            self.consume_battery(5)
        elif malfunction == "shutdown_brief":
            self.consume_battery(10)
    
    def normal_operation(self):
        pass


class Thia(SyntheticAgent):
    
    def __init__(self, x=0, y=0):
        super().__init__("Thia", "Weyland-Yutani", x, y, max_health=60, max_stamina=150)
        self.damage_level = 40
        self.missing_limb = True
        self.carried_by = None
        self.cooperation_level = 0
        self.trust_in_dek = 0
        
    @property
    def symbol(self):
        return 'T'
    
    @property
    def can_move_independently(self):
        return not self.missing_limb and self.damage_level < 60
    
    def be_carried_by(self, agent):
        self.carried_by = agent
        self.x = agent.x
        self.y = agent.y
    
    def be_dropped(self):
        self.carried_by = None
    
    def provide_intel(self, topic):
        intel_database = {
            'adversary_weakness': 'electromagnetic_pulse',
            'safe_routes': [(5, 5), (10, 15), (18, 3)],
            'hazard_locations': [(7, 12), (15, 8), (2, 18)],
            'escape_routes': [(0, 19), (19, 0)]
        }
        return intel_database.get(topic, "No data available")
    
    def build_trust(self, amount):
        self.trust_in_dek = min(100, self.trust_in_dek + amount)
        self.cooperation_level = self.trust_in_dek // 20
    
    def lose_trust(self, amount):
        self.trust_in_dek = max(0, self.trust_in_dek - amount)
        self.cooperation_level = self.trust_in_dek // 20
    
    def decide_action(self):
        if not self.can_act() or not self.is_functional:
            return "shutdown"
        
        if self.carried_by:
            return "assist_carrier"
        
        if not self.can_move_independently:
            return "wait_for_help"
        
        return super().decide_action()
    
    def normal_operation(self):
        if self.carried_by:
            self.assist_movement()
        elif self.can_move_independently:
            self.independent_movement()
    
    def assist_movement(self):
        if self.cooperation_level >= 3:
            scan_data = self.scan_area()
            hazards = [s for s in scan_data if s['type'] == 'hazard']
            if hazards and self.carried_by:
                self.carried_by.restore_stamina(5)
    
    def independent_movement(self):
        if self.trust_in_dek > 50:
            valid_moves = self.get_valid_moves()
            if valid_moves:
                safe_moves = []
                for x, y in valid_moves:
                    cell = self.grid.get_cell(x, y)
                    if not cell.terrain.is_hazardous:
                        safe_moves.append((x, y))
                
                if safe_moves:
                    self.move_to(*random.choice(safe_moves))
                else:
                    self.move_to(*random.choice(valid_moves))


class SyntheticEnemy(SyntheticAgent):
    
    def __init__(self, name, x=0, y=0):
        super().__init__(name, "Unknown-Corp", x, y, max_health=100, max_stamina=180)
        self.hostile = True
        self.target_priority = ["Thia", "Dek", "PredatorAgent"]
        
    @property
    def symbol(self):
        return 'E'
    
    def find_targets(self):
        if not self.grid:
            return []
        
        targets = []
        nearby_cells = self.grid.get_cells_in_radius(self.x, self.y, 6)
        
        for cell in nearby_cells:
            if cell.occupant and cell.occupant != self:
                agent = cell.occupant
                for priority_type in self.target_priority:
                    if priority_type.lower() in agent.__class__.__name__.lower():
                        targets.append((agent, self.target_priority.index(priority_type)))
                        break
        
        return sorted(targets, key=lambda x: x[1])
    
    def normal_operation(self):
        targets = self.find_targets()
        if targets:
            primary_target = targets[0][0]
            if self.distance_to(primary_target) == 1:
                self.attack_target(primary_target)
            else:
                self.move_towards_target(primary_target)
        else:
            self.patrol_movement()
    
    def attack_target(self, target):
        damage = random.randint(12, 20)
        target.take_damage(damage)
    
    def move_towards_target(self, target):
        best_move = None
        best_distance = float('inf')
        
        for x, y in self.get_valid_moves():
            distance = self.distance_to_position(x, y)
            if distance < best_distance:
                best_distance = distance
                best_move = (x, y)
        
        if best_move:
            self.move_to(best_move[0], best_move[1])
    
    def patrol_movement(self):
        valid_moves = self.get_valid_moves()
        if valid_moves:
            self.move_to(*random.choice(valid_moves))