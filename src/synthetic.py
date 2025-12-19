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


class SyntheticScout(SyntheticAgent):
    
    def __init__(self, name="Scout-Alpha", x=0, y=0):
        super().__init__(name, "Advanced-Recon", x, y, max_health=90, max_stamina=220)
        self.scout_mode = True
        self.stealth_capability = True
        self.reconnaissance_range = 6
        self.collected_intel = {}
        self.mission_objective = "gather_intelligence"
        
    @property
    def symbol(self):
        return 'A'
    
    def activate_stealth(self):
        if self.battery_level >= 15:
            self.stealth_capability = True
            self.consume_battery(15)
            return True
        return False
    
    def perform_deep_scan(self):
        if not self.grid or self.battery_level < 25:
            return None
        
        self.consume_battery(25)
        
        scan_data = {
            'scan_type': 'deep_reconnaissance',
            'range': self.reconnaissance_range,
            'findings': {
                'agents': [],
                'terrain_features': [],
                'strategic_positions': []
            }
        }
        
        scan_cells = self.grid.get_cells_in_radius(
            self.x, self.y, self.reconnaissance_range
        )
        
        for cell in scan_cells:
            if cell.occupant and cell.occupant != self:
                agent_data = {
                    'name': cell.occupant.name,
                    'type': cell.occupant.__class__.__name__,
                    'position': cell.position,
                    'health_estimate': self.estimate_agent_health(cell.occupant),
                    'threat_level': self.assess_threat_level(cell.occupant)
                }
                scan_data['findings']['agents'].append(agent_data)
            
            if cell.terrain.terrain_type.name in ['TELEPORT', 'CANYON', 'HOSTILE']:
                terrain_data = {
                    'type': cell.terrain.terrain_type.name,
                    'position': cell.position,
                    'tactical_value': self.assess_tactical_value(cell)
                }
                scan_data['findings']['terrain_features'].append(terrain_data)
        
        self.collected_intel[f'scan_{len(self.collected_intel)}'] = scan_data
        return scan_data
    
    def estimate_agent_health(self, agent):
        if hasattr(agent, 'health_percentage'):
            return agent.health_percentage
        return "unknown"
    
    def assess_tactical_value(self, cell):
        if cell.terrain.terrain_type.name == 'TELEPORT':
            return "high_mobility"
        elif cell.terrain.terrain_type.name == 'CANYON':
            return "defensive_position"
        elif cell.terrain.terrain_type.name == 'HOSTILE':
            return "area_denial"
        return "standard"
    
    def share_intelligence(self, target_agent):
        from interaction_protocol import SyntheticInteractionManager, InteractionType
        
        if not self.collected_intel:
            return False
        
        manager = SyntheticInteractionManager()
        latest_intel = list(self.collected_intel.values())[-1]
        
        result = manager.initiate_interaction(
            self, target_agent, InteractionType.INFO_SHARE,
            {'key': 'reconnaissance_data', 'value': latest_intel}
        )
        
        return result.success
    
    def normal_operation(self):
        if self.mission_objective == "gather_intelligence":
            if len(self.collected_intel) < 3:
                self.perform_deep_scan()
            else:
                self.patrol_and_observe()
        elif self.mission_objective == "support_allies":
            self.seek_and_assist_allies()
    
    def patrol_and_observe(self):
        valid_moves = self.get_valid_moves()
        if valid_moves:
            import random
            self.move_to(*random.choice(valid_moves))
    
    def seek_and_assist_allies(self):
        if not self.grid:
            return
        
        nearby_agents = []
        nearby_cells = self.grid.get_cells_in_radius(self.x, self.y, 4)
        
        for cell in nearby_cells:
            if cell.occupant and cell.occupant != self:
                if hasattr(cell.occupant, 'name') and cell.occupant.name in ['Dek', 'Thia']:
                    nearby_agents.append(cell.occupant)
        
        if nearby_agents:
            target = nearby_agents[0]
            if self.distance_to(target) > 1:
                self.move_towards_target(target)
            else:
                self.share_intelligence(target)


class SyntheticMedic(SyntheticAgent):
    
    def __init__(self, name="Medic-Beta", x=0, y=0):
        super().__init__(name, "Medical-Support", x, y, max_health=70, max_stamina=180)
        self.healing_capability = True
        self.medical_supplies = 5
        self.repair_tools = 3
        self.priority_targets = ['Dek', 'Thia']
        
    @property
    def symbol(self):
        return 'M'
    
    def perform_medical_scan(self, target):
        if self.distance_to(target) > 1 or self.battery_level < 10:
            return None
        
        self.consume_battery(10)
        
        medical_data = {
            'target': target.name,
            'health_status': target.health if hasattr(target, 'health') else 'unknown',
            'max_health': target.max_health if hasattr(target, 'max_health') else 'unknown',
            'damage_level': getattr(target, 'damage_level', 0),
            'recommended_treatment': self.recommend_treatment(target)
        }
        
        return medical_data
    
    def recommend_treatment(self, target):
        if hasattr(target, 'health') and hasattr(target, 'max_health'):
            health_percentage = (target.health / target.max_health) * 100
            
            if health_percentage < 25:
                return "immediate_medical_attention"
            elif health_percentage < 50:
                return "medical_treatment_advised"
            elif health_percentage < 75:
                return "minor_treatment_suggested"
            else:
                return "good_health"
        
        if hasattr(target, 'damage_level'):
            if target.damage_level > 60:
                return "major_repairs_needed"
            elif target.damage_level > 30:
                return "maintenance_required"
        
        return "status_unknown"
    
    def provide_medical_assistance(self, target):
        if self.distance_to(target) > 1 or self.medical_supplies <= 0:
            return False
        
        if not hasattr(target, 'heal'):
            return False
        
        self.medical_supplies -= 1
        self.consume_battery(20)
        
        heal_amount = 25
        target.heal(heal_amount)
        
        return True
    
    def provide_repair_assistance(self, target):
        if self.distance_to(target) > 1 or self.repair_tools <= 0:
            return False
        
        if not hasattr(target, 'repair_damage'):
            return False
        
        self.repair_tools -= 1
        self.consume_battery(15)
        
        repair_amount = 20
        target.repair_damage(repair_amount)
        
        return True
    
    def find_patients(self):
        if not self.grid:
            return []
        
        patients = []
        nearby_cells = self.grid.get_cells_in_radius(self.x, self.y, 5)
        
        for cell in nearby_cells:
            if cell.occupant and cell.occupant != self:
                agent = cell.occupant
                
                needs_help = False
                if hasattr(agent, 'health') and hasattr(agent, 'max_health'):
                    if agent.health < agent.max_health * 0.7:
                        needs_help = True
                
                if hasattr(agent, 'damage_level') and agent.damage_level > 30:
                    needs_help = True
                
                if needs_help:
                    priority = 1 if agent.name in self.priority_targets else 2
                    patients.append((agent, priority))
        
        return sorted(patients, key=lambda x: x[1])
    
    def normal_operation(self):
        patients = self.find_patients()
        
        if patients:
            target_agent, priority = patients[0]
            
            if self.distance_to(target_agent) > 1:
                self.move_towards_target(target_agent)
            else:
                medical_scan = self.perform_medical_scan(target_agent)
                if medical_scan:
                    treatment = medical_scan['recommended_treatment']
                    
                    if 'medical' in treatment and self.medical_supplies > 0:
                        self.provide_medical_assistance(target_agent)
                    elif 'repair' in treatment and self.repair_tools > 0:
                        self.provide_repair_assistance(target_agent)
        else:
            self.patrol_movement()
    
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
            import random
            self.move_to(*random.choice(valid_moves))


class SyntheticEnemy(SyntheticAgent):
    
    def __init__(self, name, x=0, y=0):
        super().__init__(name, "Unknown-Corp", x, y, max_health=100, max_stamina=180)
        self.hostile = True
        self.target_priority = ["Thia", "Dek", "PredatorAgent"]
        self.combat_mode = "aggressive"
        
    @property
    def symbol(self):
        return 'E'
    
    def set_combat_mode(self, mode):
        valid_modes = ["aggressive", "defensive", "stalking"]
        if mode in valid_modes:
            self.combat_mode = mode
    
    def find_targets(self):
        if not self.grid:
            return []
        
        targets = []
        scan_range = 6 if self.combat_mode == "aggressive" else 4
        nearby_cells = self.grid.get_cells_in_radius(self.x, self.y, scan_range)
        
        for cell in nearby_cells:
            if cell.occupant and cell.occupant != self:
                agent = cell.occupant
                for priority_type in self.target_priority:
                    if priority_type.lower() in agent.__class__.__name__.lower() or agent.name == priority_type:
                        targets.append((agent, self.target_priority.index(priority_type)))
                        break
        
        return sorted(targets, key=lambda x: x[1])
    
    def normal_operation(self):
        targets = self.find_targets()
        if targets:
            primary_target = targets[0][0]
            
            if self.combat_mode == "stalking":
                self.stalk_target(primary_target)
            elif self.combat_mode == "defensive":
                self.defensive_approach(primary_target)
            else:
                self.aggressive_approach(primary_target)
        else:
            self.search_and_patrol()
    
    def aggressive_approach(self, target):
        if self.distance_to(target) == 1:
            self.attack_target(target)
        else:
            self.move_towards_target(target)
    
    def defensive_approach(self, target):
        distance = self.distance_to(target)
        if distance == 1:
            self.attack_target(target)
        elif distance == 2:
            pass
        elif distance > 3:
            self.move_towards_target(target)
    
    def stalk_target(self, target):
        distance = self.distance_to(target)
        if distance <= 3 and distance > 1:
            pass
        elif distance > 3:
            self.move_towards_target(target)
        elif distance == 1:
            self.attack_target(target)
    
    def attack_target(self, target):
        damage = 12 + (3 if self.combat_mode == "aggressive" else 0)
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
    
    def search_and_patrol(self):
        valid_moves = self.get_valid_moves()
        if valid_moves:
            import random
            self.move_to(*random.choice(valid_moves))