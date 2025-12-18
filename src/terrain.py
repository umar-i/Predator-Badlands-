from enum import Enum


class TerrainType(Enum):
    EMPTY = 0
    DESERT = 1
    ROCKY = 2
    CANYON = 3
    HOSTILE = 4
    TRAP = 5
    TELEPORT = 6


class Terrain:
    
    MOVEMENT_COSTS = {
        TerrainType.EMPTY: 1,
        TerrainType.DESERT: 2,
        TerrainType.ROCKY: 3,
        TerrainType.CANYON: 2,
        TerrainType.HOSTILE: 4,
        TerrainType.TRAP: 5,
        TerrainType.TELEPORT: 1
    }
    
    DAMAGE_VALUES = {
        TerrainType.EMPTY: 0,
        TerrainType.DESERT: 0,
        TerrainType.ROCKY: 0,
        TerrainType.CANYON: 0,
        TerrainType.HOSTILE: 5,
        TerrainType.TRAP: 15,
        TerrainType.TELEPORT: 0
    }
    
    SYMBOLS = {
        TerrainType.EMPTY: '.',
        TerrainType.DESERT: '~',
        TerrainType.ROCKY: '^',
        TerrainType.CANYON: '#',
        TerrainType.HOSTILE: '!',
        TerrainType.TRAP: 'X',
        TerrainType.TELEPORT: 'O'
    }
    
    def __init__(self, terrain_type=TerrainType.EMPTY):
        self.terrain_type = terrain_type
    
    @property
    def movement_cost(self):
        return self.MOVEMENT_COSTS[self.terrain_type]
    
    @property
    def damage(self):
        return self.DAMAGE_VALUES[self.terrain_type]
    
    @property
    def symbol(self):
        return self.SYMBOLS[self.terrain_type]
    
    @property
    def is_passable(self):
        return True
    
    @property
    def is_hazardous(self):
        return self.terrain_type in (TerrainType.HOSTILE, TerrainType.TRAP)
