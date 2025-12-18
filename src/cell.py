from terrain import Terrain, TerrainType


class Cell:
    
    def __init__(self, x, y, terrain_type=TerrainType.EMPTY):
        self.x = x
        self.y = y
        self.terrain = Terrain(terrain_type)
        self.occupant = None
        self.items = []
        self.teleport_destination = None
    
    @property
    def position(self):
        return (self.x, self.y)
    
    @property
    def is_occupied(self):
        return self.occupant is not None
    
    @property
    def is_empty(self):
        return self.occupant is None and len(self.items) == 0
    
    @property
    def movement_cost(self):
        return self.terrain.movement_cost
    
    @property
    def terrain_damage(self):
        return self.terrain.damage
    
    def place_occupant(self, agent):
        if self.occupant is not None:
            return False
        self.occupant = agent
        return True
    
    def remove_occupant(self):
        occupant = self.occupant
        self.occupant = None
        return occupant
    
    def add_item(self, item):
        self.items.append(item)
    
    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
            return item
        return None
    
    def set_teleport_destination(self, dest_x, dest_y):
        self.teleport_destination = (dest_x, dest_y)
    
    def get_display_symbol(self):
        if self.occupant is not None:
            return self.occupant.symbol
        if len(self.items) > 0:
            return '*'
        return self.terrain.symbol
