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
        self.mobility_rating = 2
        self.carried_by = None
        self.cooperation_level = 0
        self.trust_in_dek = 0
        self.intel_database = self.initialize_intel()
        self.scan_cooldown = 0
        
    @property
    def symbol(self):
        return 'T'
    
    @property
    def can_move_independently(self):
        return not self.missing_limb and self.damage_level < 60 and not self.carried_by
    
    @property
    def movement_penalty(self):
        base_penalty = self.damage_level / 10
        limb_penalty = 50 if self.missing_limb else 0
        return int(base_penalty + limb_penalty)
    
    def initialize_intel(self):
        return {
            'adversary_weakness': {
                'type': 'weakness',
                'data': 'Ultimate Adversary vulnerable to electromagnetic pulse',
                'reliability': 0.85,
                'coordinates': None
            },
            'safe_routes': {
                'type': 'navigation',
                'data': [(5, 5), (10, 15), (18, 3), (2, 12)],
                'reliability': 0.90,
                'coordinates': [(5, 5), (10, 15), (18, 3)]
            },
            'hazard_locations': {
                'type': 'danger',
                'data': [(7, 12), (15, 8), (2, 18), (19, 19)],
                'reliability': 0.95,
                'coordinates': [(7, 12), (15, 8), (2, 18)]
            },
            'escape_routes': {
                'type': 'emergency',
                'data': [(0, 19), (19, 0), (10, 0), (0, 10)],
                'reliability': 0.75,
                'coordinates': [(0, 19), (19, 0)]
            },
            'resource_caches': {
                'type': 'resources',
                'data': [(8, 8), (16, 16), (4, 20)],
                'reliability': 0.60,
                'coordinates': [(8, 8), (16, 16)]
            }
        }
    
    def be_carried_by(self, agent):
        if self.carried_by:
            return False
        
        self.carried_by = agent
        self.x = agent.x
        self.y = agent.y
        self.consume_battery(5)
        return True
    
    def be_dropped(self):
        if not self.carried_by:
            return False
        
        carrier = self.carried_by
        self.carried_by = None
        return True
    
    def attempt_independent_movement(self, direction):
        if not self.can_move_independently:
            return False
        
        stamina_cost = 15 + self.movement_penalty
        if not self.consume_stamina(stamina_cost):
            return False
        
        self.consume_battery(3)
        return True
    
    def provide_intel(self, topic, requesting_agent=None):
        if topic not in self.intel_database:
            return None
        
        intel = self.intel_database[topic]
        
        trust_modifier = 1.0
        if requesting_agent and hasattr(requesting_agent, 'name'):
            if requesting_agent.name == "Dek":
                trust_modifier = 1.0 + (self.trust_in_dek / 100)
            elif "Predator" in requesting_agent.__class__.__name__:
                trust_modifier = 0.8
            else:
                trust_modifier = 0.5
        
        reliability = intel['reliability'] * trust_modifier
        
        if reliability > 0.7:
            return {
                'data': intel['data'],
                'reliability': reliability,
                'source': 'Thia Intelligence Database'
            }
        elif reliability > 0.4:
            partial_data = intel['data'][:len(intel['data'])//2] if isinstance(intel['data'], list) else "Partial data available"
            return {
                'data': partial_data,
                'reliability': reliability,
                'source': 'Thia Intelligence Database (Partial)'
            }
        
        return None
    
    def perform_reconnaissance_scan(self):
        if self.scan_cooldown > 0:
            return None
        
        if not self.is_functional:
            return None
        
        if not self.consume_stamina(20):
            return None
        
        self.consume_battery(10)
        self.scan_cooldown = 3
        
        scan_results = {
            'timestamp': 0,
            'scanner': 'Thia',
            'area_scanned': f"Radius 4 from ({self.x}, {self.y})",
            'threats': [],
            'opportunities': [],
            'terrain_analysis': []
        }
        
        if not self.grid:
            return scan_results
        
        nearby_cells = self.grid.get_cells_in_radius(self.x, self.y, 4)
        
        for cell in nearby_cells:
            if cell.occupant and cell.occupant != self:
                agent = cell.occupant
                threat_level = self.assess_threat_level(agent)
                
                scan_results['threats'].append({
                    'agent': agent.name,
                    'position': cell.position,
                    'threat_level': threat_level,
                    'agent_type': agent.__class__.__name__
                })
            
            if cell.terrain.is_hazardous:
                scan_results['terrain_analysis'].append({
                    'position': cell.position,
                    'terrain_type': cell.terrain.terrain_type.name,
                    'danger_level': cell.terrain.damage
                })
            
            if cell.terrain.terrain_type.name == 'TELEPORT':
                scan_results['opportunities'].append({
                    'type': 'teleportation',
                    'position': cell.position,
                    'destination': cell.teleport_destination
                })
        
        return scan_results
    
    def assess_threat_level(self, agent):
        threat_factors = 0
        
        if hasattr(agent, 'weapons'):
            threat_factors += len(agent.weapons) * 2
        
        if hasattr(agent, 'health') and agent.health > 100:
            threat_factors += 2
        
        if 'Boss' in agent.__class__.__name__:
            threat_factors += 10
        elif 'Predator' in agent.__class__.__name__:
            threat_factors += 3
        elif 'Wildlife' in agent.__class__.__name__:
            threat_factors += 1
        
        if threat_factors >= 8:
            return "EXTREME"
        elif threat_factors >= 5:
            return "HIGH"
        elif threat_factors >= 2:
            return "MODERATE"
        else:
            return "LOW"
    
    def provide_navigation_assistance(self, destination_x, destination_y):
        if not self.grid or not self.is_functional:
            return None
        
        current_distance = self.distance_to_position(destination_x, destination_y)
        
        safe_routes = self.intel_database.get('safe_routes', {}).get('data', [])
        hazard_locations = self.intel_database.get('hazard_locations', {}).get('data', [])
        
        assistance = {
            'destination': (destination_x, destination_y),
            'current_distance': current_distance,
            'recommended_path': [],
            'hazards_to_avoid': [],
            'safe_waypoints': []
        }
        
        for hazard in hazard_locations:
            hazard_distance = self.distance_to_position(hazard[0], hazard[1])
            if hazard_distance <= current_distance + 3:
                assistance['hazards_to_avoid'].append(hazard)
        
        for waypoint in safe_routes:
            waypoint_distance = self.distance_to_position(waypoint[0], waypoint[1])
            if waypoint_distance <= current_distance:
                assistance['safe_waypoints'].append(waypoint)
        
        return assistance
    
    def build_trust(self, amount):
        self.trust_in_dek = min(100, self.trust_in_dek + amount)
        self.cooperation_level = self.trust_in_dek // 20
        
        if self.cooperation_level >= 4:
            self.malfunction_chance = max(0, self.malfunction_chance - 0.1)
    
    def lose_trust(self, amount):
        self.trust_in_dek = max(0, self.trust_in_dek - amount)
        self.cooperation_level = self.trust_in_dek // 20
        
        if self.cooperation_level <= 1:
            self.malfunction_chance += 0.05
    
    def decide_action(self):
        if not self.can_act() or not self.is_functional:
            return "shutdown"
        
        if self.scan_cooldown > 0:
            self.scan_cooldown -= 1
        
        if self.carried_by:
            return "assist_carrier"
        
        if not self.can_move_independently:
            return "wait_for_help"
        
        if self.battery_level < 30:
            return "conserve_power"
        
        return super().decide_action()
    
    def normal_operation(self):
        if self.carried_by:
            self.assist_movement()
        elif self.can_move_independently:
            self.independent_movement()
        else:
            self.wait_for_assistance()
    
    def assist_movement(self):
        if not self.carried_by:
            return
        
        if self.cooperation_level >= 3:
            scan_data = self.scan_area()
            hazards = [s for s in scan_data if s['type'] == 'hazard']
            
            if hazards and len(hazards) > 0:
                self.carried_by.restore_stamina(3)
                
            if self.cooperation_level >= 4:
                nav_assistance = self.provide_navigation_assistance(
                    self.carried_by.x, self.carried_by.y
                )
                if nav_assistance and len(nav_assistance['safe_waypoints']) > 0:
                    self.carried_by.restore_stamina(2)
    
    def independent_movement(self):
        if self.trust_in_dek > 50 and self.grid:
            valid_moves = self.get_valid_moves()
            if valid_moves:
                safe_moves = []
                for x, y in valid_moves:
                    cell = self.grid.get_cell(x, y)
                    if not cell.terrain.is_hazardous:
                        safe_moves.append((x, y))
                
                if safe_moves:
                    from actions import Direction
                    import random
                    target_x, target_y = random.choice(safe_moves)
                    if self.attempt_independent_movement(None):
                        self.move_to(target_x, target_y)
    
    def wait_for_assistance(self):
        self.recharge_battery(1)
        if self.damage_level > 0:
            self.repair_damage(0.5)


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