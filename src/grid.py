import random
from cell import Cell
from terrain import TerrainType


class Grid:
    
    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height
        self.cells = self._create_grid()
        self.teleport_pairs = []
    
    def _create_grid(self):
        grid = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(Cell(x, y))
            grid.append(row)
        return grid
    
    def wrap_coordinates(self, x, y):
        wrapped_x = x % self.width
        wrapped_y = y % self.height
        return (wrapped_x, wrapped_y)
    
    def get_cell(self, x, y):
        wrapped_x, wrapped_y = self.wrap_coordinates(x, y)
        return self.cells[wrapped_y][wrapped_x]
    
    def set_terrain(self, x, y, terrain_type):
        cell = self.get_cell(x, y)
        cell.terrain.terrain_type = terrain_type
    
    def get_adjacent_cells(self, x, y):
        directions = [
            (0, -1),
            (0, 1),
            (-1, 0),
            (1, 0),
            (-1, -1),
            (1, -1),
            (-1, 1),
            (1, 1)
        ]
        adjacent = []
        for dx, dy in directions:
            new_x, new_y = self.wrap_coordinates(x + dx, y + dy)
            adjacent.append(self.get_cell(new_x, new_y))
        return adjacent
    
    def get_cardinal_adjacent(self, x, y):
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        adjacent = []
        for dx, dy in directions:
            new_x, new_y = self.wrap_coordinates(x + dx, y + dy)
            adjacent.append(self.get_cell(new_x, new_y))
        return adjacent
    
    def find_empty_cell(self):
        attempts = 0
        max_attempts = self.width * self.height
        while attempts < max_attempts:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            cell = self.get_cell(x, y)
            if not cell.is_occupied and not cell.terrain.is_hazardous:
                return cell
            attempts += 1
        return None
    
    def find_random_cell_of_type(self, terrain_type):
        matching_cells = []
        for row in self.cells:
            for cell in row:
                if cell.terrain.terrain_type == terrain_type and not cell.is_occupied:
                    matching_cells.append(cell)
        if matching_cells:
            return random.choice(matching_cells)
        return None
    
    def place_agent(self, agent, x=None, y=None):
        if x is not None and y is not None:
            cell = self.get_cell(x, y)
        else:
            cell = self.find_empty_cell()
        
        if cell and cell.place_occupant(agent):
            agent.x = cell.x
            agent.y = cell.y
            return True
        return False
    
    def move_agent(self, agent, new_x, new_y):
        old_cell = self.get_cell(agent.x, agent.y)
        new_x, new_y = self.wrap_coordinates(new_x, new_y)
        new_cell = self.get_cell(new_x, new_y)
        
        if new_cell.is_occupied:
            return False
        
        old_cell.remove_occupant()
        new_cell.place_occupant(agent)
        agent.x = new_x
        agent.y = new_y
        
        if new_cell.terrain.terrain_type == TerrainType.TELEPORT:
            if new_cell.teleport_destination:
                dest_x, dest_y = new_cell.teleport_destination
                dest_cell = self.get_cell(dest_x, dest_y)
                if not dest_cell.is_occupied:
                    new_cell.remove_occupant()
                    dest_cell.place_occupant(agent)
                    agent.x = dest_x
                    agent.y = dest_y
        
        return True
    
    def calculate_distance(self, x1, y1, x2, y2):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        dx = min(dx, self.width - dx)
        dy = min(dy, self.height - dy)
        
        return max(dx, dy)
    
    def get_cells_in_radius(self, center_x, center_y, radius):
        cells_in_range = []
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue
                x, y = self.wrap_coordinates(center_x + dx, center_y + dy)
                if self.calculate_distance(center_x, center_y, x, y) <= radius:
                    cells_in_range.append(self.get_cell(x, y))
        return cells_in_range
    
    def generate_terrain(self, terrain_distribution=None):
        if terrain_distribution is None:
            terrain_distribution = {
                TerrainType.EMPTY: 0.50,
                TerrainType.DESERT: 0.20,
                TerrainType.ROCKY: 0.15,
                TerrainType.CANYON: 0.08,
                TerrainType.HOSTILE: 0.04,
                TerrainType.TRAP: 0.02,
                TerrainType.TELEPORT: 0.01
            }
        
        terrain_types = list(terrain_distribution.keys())
        weights = list(terrain_distribution.values())
        
        for row in self.cells:
            for cell in row:
                chosen_terrain = random.choices(terrain_types, weights=weights, k=1)[0]
                cell.terrain.terrain_type = chosen_terrain
    
    def create_teleport_pair(self, x1, y1, x2, y2):
        cell1 = self.get_cell(x1, y1)
        cell2 = self.get_cell(x2, y2)
        
        cell1.terrain.terrain_type = TerrainType.TELEPORT
        cell2.terrain.terrain_type = TerrainType.TELEPORT
        
        cell1.set_teleport_destination(x2, y2)
        cell2.set_teleport_destination(x1, y1)
        
        self.teleport_pairs.append(((x1, y1), (x2, y2)))
    
    def get_all_occupied_cells(self):
        occupied = []
        for row in self.cells:
            for cell in row:
                if cell.is_occupied:
                    occupied.append(cell)
        return occupied
    
    def clear_all_occupants(self):
        for row in self.cells:
            for cell in row:
                cell.occupant = None
                cell.items.clear()
