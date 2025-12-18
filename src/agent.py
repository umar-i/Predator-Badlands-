from abc import ABC, abstractmethod
import random


class Agent(ABC):
    
    def __init__(self, name, x=0, y=0, max_health=100, max_stamina=100):
        self.name = name
        self.x = x
        self.y = y
        self.max_health = max_health
        self.health = max_health
        self.max_stamina = max_stamina
        self.stamina = max_stamina
        self.is_alive = True
        self.age = 0
        self.grid = None
    
    @property
    def position(self):
        return (self.x, self.y)
    
    @property
    def health_percentage(self):
        return (self.health / self.max_health) * 100
    
    @property
    def stamina_percentage(self):
        return (self.stamina / self.max_stamina) * 100
    
    @property
    def symbol(self):
        return '?'
    
    def set_grid(self, grid):
        self.grid = grid
    
    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.is_alive = False
    
    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
    
    def consume_stamina(self, amount):
        self.stamina = max(0, self.stamina - amount)
        return self.stamina > 0
    
    def restore_stamina(self, amount):
        self.stamina = min(self.max_stamina, self.stamina + amount)
    
    def can_move(self):
        return self.is_alive and self.stamina > 0
    
    def can_act(self):
        return self.is_alive
    
    def move_to(self, new_x, new_y):
        if not self.can_move() or not self.grid:
            return False
        
        if self.grid.move_agent(self, new_x, new_y):
            movement_cost = self.get_movement_cost(new_x, new_y)
            self.consume_stamina(movement_cost)
            self.handle_terrain_effects()
            return True
        return False
    
    def get_movement_cost(self, x, y):
        if not self.grid:
            return 1
        cell = self.grid.get_cell(x, y)
        return cell.movement_cost
    
    def handle_terrain_effects(self):
        if not self.grid:
            return
        
        cell = self.grid.get_cell(self.x, self.y)
        if cell.terrain_damage > 0:
            self.take_damage(cell.terrain_damage)
    
    def get_adjacent_positions(self):
        if not self.grid:
            return []
        
        positions = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = self.grid.wrap_coordinates(self.x + dx, self.y + dy)
                positions.append((new_x, new_y))
        return positions
    
    def get_valid_moves(self):
        valid_moves = []
        for x, y in self.get_adjacent_positions():
            cell = self.grid.get_cell(x, y)
            if not cell.is_occupied:
                valid_moves.append((x, y))
        return valid_moves
    
    def distance_to(self, other_agent):
        if not self.grid:
            return float('inf')
        return self.grid.calculate_distance(self.x, self.y, other_agent.x, other_agent.y)
    
    def distance_to_position(self, x, y):
        if not self.grid:
            return float('inf')
        return self.grid.calculate_distance(self.x, self.y, x, y)
    
    @abstractmethod
    def decide_action(self):
        pass
    
    @abstractmethod
    def update(self):
        pass
    
    def step(self):
        if not self.can_act():
            return
        
        self.age += 1
        self.update()
        
        if self.age % 10 == 0:
            self.restore_stamina(5)
    
    def __str__(self):
        return f"{self.name}({self.x},{self.y}) H:{self.health}/{self.max_health} S:{self.stamina}/{self.max_stamina}"
    
    def __repr__(self):
        return self.__str__()