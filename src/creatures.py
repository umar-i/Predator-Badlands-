from agent import Agent
import random


class WildlifeAgent(Agent):
    
    def __init__(self, name, species, x=0, y=0, max_health=50, max_stamina=80):
        super().__init__(name, x, y, max_health, max_stamina)
        self.species = species
        self.aggression_level = 0.2
        self.territory_size = 3
        self.pack_members = []
        self.is_prey = True
        
    @property
    def symbol(self):
        return 'W'
    
    def set_aggression(self, level):
        self.aggression_level = max(0.0, min(1.0, level))
    
    def add_pack_member(self, member):
        self.pack_members.append(member)
        member.pack_members.append(self)
    
    def detect_threats(self):
        if not self.grid:
            return []
        
        threats = []
        nearby_cells = self.grid.get_cells_in_radius(self.x, self.y, 2)
        
        for cell in nearby_cells:
            if cell.occupant and cell.occupant != self:
                agent = cell.occupant
                if hasattr(agent, 'weapons') or 'predator' in agent.__class__.__name__.lower():
                    threats.append(agent)
        
        return threats
    
    def decide_action(self):
        if not self.can_act():
            return "rest"
        
        threats = self.detect_threats()
        
        if threats:
            if random.random() < self.aggression_level:
                return "fight"
            else:
                return "flee"
        
        if self.stamina < 20:
            return "rest"
        
        return "forage"
    
    def flee_behavior(self):
        threats = self.detect_threats()
        if not threats:
            return
        
        nearest_threat = min(threats, key=lambda t: self.distance_to(t))
        
        best_escape = None
        best_distance = 0
        
        for x, y in self.get_valid_moves():
            distance = self.distance_to_position(x, y)
            if distance > best_distance:
                best_distance = distance
                best_escape = (x, y)
        
        if best_escape:
            self.move_to(best_escape[0], best_escape[1])
    
    def fight_behavior(self):
        threats = self.detect_threats()
        if threats:
            target = min(threats, key=lambda t: self.distance_to(t))
            if self.distance_to(target) == 1:
                damage = random.randint(5, 15)
                target.take_damage(damage)
                if hasattr(target, 'consume_stamina') and random.random() < 0.4:
                    target.consume_stamina(random.randint(5, 12))
            else:
                self.move_towards(target)
    
    def forage_behavior(self):
        valid_moves = self.get_valid_moves()
        if valid_moves:
            preferred_terrain = []
            for x, y in valid_moves:
                cell = self.grid.get_cell(x, y)
                if not cell.terrain.is_hazardous:
                    preferred_terrain.append((x, y))
            
            if preferred_terrain:
                self.move_to(*random.choice(preferred_terrain))
            else:
                self.move_to(*random.choice(valid_moves))
    
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
    
    def update(self):
        action = self.decide_action()
        
        if action == "rest":
            self.restore_stamina(8)
        elif action == "flee":
            self.flee_behavior()
        elif action == "fight":
            self.fight_behavior()
        elif action == "forage":
            self.forage_behavior()


class BossAdversary(Agent):
    
    def __init__(self, name="Ultimate Adversary", x=10, y=10):
        super().__init__(name, x, y, max_health=150, max_stamina=300)
        self.size = 3
        self.attack_range = 2
        self.special_abilities = ["earthquake", "energy_blast", "regeneration"]
        self.rage_level = 0
        self.phase = 1
        self.last_attacker = None
        self.territory_center = (x, y)
        self.territory_radius = 7
        self.focus_target = None
        
    @property
    def symbol(self):
        return 'B'
    
    @property
    def is_enraged(self):
        return self.rage_level >= 50
    
    def take_damage(self, amount):
        super().take_damage(amount)
        self.rage_level += amount * 0.5
        
        if self.health < self.max_health * 0.5 and self.phase == 1:
            self.phase = 2
            self.rage_level += 25
    
    def detect_enemies(self):
        if not self.grid:
            return []
        
        enemies = []
        # Much larger scan radius - Boss can see whole battlefield
        scan_radius = 20 if self.is_enraged else 15
        nearby_cells = self.grid.get_cells_in_radius(self.x, self.y, scan_radius)
        
        for cell in nearby_cells:
            if cell.occupant and cell.occupant != self:
                # Only target Dek and Thia (allies)
                if hasattr(cell.occupant, 'is_exiled') or hasattr(cell.occupant, 'battery_level'):
                    enemies.append(cell.occupant)
        
        return enemies
    
    def decide_action(self):
        if not self.can_act():
            return "rest"
        
        enemies = self.detect_enemies()
        
        if not enemies:
            return "patrol"
        
        if self.health < self.max_health * 0.3:
            return "regenerate"
        
        if self.is_enraged and random.random() < 0.5:
            return "special_attack"
        
        return "attack"
    
    def special_attack(self):
        ability = random.choice(self.special_abilities)
        
        if ability == "earthquake":
            self.earthquake_attack()
        elif ability == "energy_blast":
            self.energy_blast_attack()
        elif ability == "regeneration":
            self.regenerate_health()
    
    def earthquake_attack(self):
        if not self.grid:
            return
        
        affected_cells = self.grid.get_cells_in_radius(self.x, self.y, 4 if self.phase == 1 else 6)
        
        for cell in affected_cells:
            if cell.occupant and cell.occupant != self:
                damage = random.randint(15, 25) if self.phase == 1 else random.randint(25, 40)
                cell.occupant.take_damage(damage)
    
    def energy_blast_attack(self):
        enemies = self.detect_enemies()
        if enemies:
            target = random.choice(enemies)
            damage = random.randint(35, 55) if self.phase == 1 else random.randint(45, 70)
            target.take_damage(damage)
    
    def regenerate_health(self):
        heal_amount = min(50, self.max_health - self.health)
        self.heal(heal_amount)
        self.rage_level = max(0, self.rage_level - 20)
    
    def basic_attack(self):
        enemies = self.detect_enemies()
        if not enemies:
            return
        
        targets_in_range = [e for e in enemies if self.distance_to(e) <= self.attack_range]
        
        if targets_in_range:
            target = random.choice(targets_in_range)
            damage = random.randint(18, 30) if self.phase == 1 else random.randint(28, 45)
            if self.is_enraged:
                damage = int(damage * 1.3)
            target.take_damage(damage)
            self.last_attacker = target
        else:
            nearest_enemy = min(enemies, key=lambda e: self.distance_to(e))
            self.move_towards_enemy(nearest_enemy)
    
    def move_towards_enemy(self, enemy):
        best_move = None
        best_distance = float('inf')
        
        for x, y in self.get_valid_moves():
            # Calculate distance from NEW position to enemy
            if self.grid:
                distance = self.grid.calculate_distance(x, y, enemy.x, enemy.y)
            else:
                distance = abs(x - enemy.x) + abs(y - enemy.y)
            if distance < best_distance:
                best_distance = distance
                best_move = (x, y)
        
        if best_move:
            self.move_to(best_move[0], best_move[1])
    
    def patrol_behavior(self):
        valid_moves = self.get_valid_moves()
        if not valid_moves:
            return
        tx, ty = self.territory_center
        best_move = None
        best_distance = float('inf')
        for x, y in valid_moves:
            d = self.grid.calculate_distance(x, y, tx, ty) if self.grid else 0
            if d <= self.territory_radius and d < best_distance:
                best_distance = d
                best_move = (x, y)
        if best_move:
            self.move_to(*best_move)
        else:
            self.move_to(*random.choice(valid_moves))
    
    def update(self):
        action = self.decide_action()
        
        if action == "rest":
            self.restore_stamina(15)
        elif action == "patrol":
            # Instead of patrolling, actively hunt for enemies
            enemies = self.detect_enemies()
            if enemies:
                nearest = min(enemies, key=lambda e: self.distance_to(e))
                self.move_towards_enemy(nearest)
            else:
                self.patrol_behavior()
        elif action == "regenerate":
            self.regenerate_health()
        elif action == "special_attack":
            self.special_attack()
        elif action == "attack":
            self.basic_attack()
        
        if self.rage_level > 0:
            self.rage_level = max(0, self.rage_level - 1)