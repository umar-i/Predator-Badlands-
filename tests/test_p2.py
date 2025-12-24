import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from terrain import Terrain, TerrainType
from cell import Cell
from grid import Grid


class TestTerrainType(unittest.TestCase):
    
    def test_terrain_type_enum_values(self):
        self.assertEqual(TerrainType.EMPTY.value, 0)
        self.assertEqual(TerrainType.DESERT.value, 1)
        self.assertEqual(TerrainType.ROCKY.value, 2)
        self.assertEqual(TerrainType.CANYON.value, 3)
        self.assertEqual(TerrainType.HOSTILE.value, 4)
        self.assertEqual(TerrainType.TRAP.value, 5)
        self.assertEqual(TerrainType.TELEPORT.value, 6)
    
    def test_all_terrain_types_exist(self):
        terrain_types = [TerrainType.EMPTY, TerrainType.DESERT, TerrainType.ROCKY,
                        TerrainType.CANYON, TerrainType.HOSTILE, TerrainType.TRAP,
                        TerrainType.TELEPORT]
        self.assertEqual(len(terrain_types), 7)


class TestTerrain(unittest.TestCase):
    
    def test_default_terrain_creation(self):
        terrain = Terrain()
        self.assertEqual(terrain.terrain_type, TerrainType.EMPTY)
    
    def test_specific_terrain_creation(self):
        terrain = Terrain(TerrainType.DESERT)
        self.assertEqual(terrain.terrain_type, TerrainType.DESERT)
    
    def test_empty_terrain_properties(self):
        terrain = Terrain(TerrainType.EMPTY)
        self.assertEqual(terrain.movement_cost, 1)
        self.assertEqual(terrain.damage, 0)
        self.assertEqual(terrain.symbol, '.')
        self.assertTrue(terrain.is_passable)
        self.assertFalse(terrain.is_hazardous)
    
    def test_desert_terrain_properties(self):
        terrain = Terrain(TerrainType.DESERT)
        self.assertEqual(terrain.movement_cost, 2)
        self.assertEqual(terrain.damage, 0)
        self.assertEqual(terrain.symbol, '~')
        self.assertFalse(terrain.is_hazardous)
    
    def test_rocky_terrain_properties(self):
        terrain = Terrain(TerrainType.ROCKY)
        self.assertEqual(terrain.movement_cost, 3)
        self.assertEqual(terrain.damage, 0)
        self.assertEqual(terrain.symbol, '^')
    
    def test_canyon_terrain_properties(self):
        terrain = Terrain(TerrainType.CANYON)
        self.assertEqual(terrain.movement_cost, 2)
        self.assertEqual(terrain.damage, 0)
        self.assertEqual(terrain.symbol, '#')
    
    def test_hostile_terrain_properties(self):
        terrain = Terrain(TerrainType.HOSTILE)
        self.assertEqual(terrain.movement_cost, 4)
        self.assertEqual(terrain.damage, 5)
        self.assertEqual(terrain.symbol, '!')
        self.assertTrue(terrain.is_hazardous)
    
    def test_trap_terrain_properties(self):
        terrain = Terrain(TerrainType.TRAP)
        self.assertEqual(terrain.movement_cost, 5)
        self.assertEqual(terrain.damage, 15)
        self.assertEqual(terrain.symbol, 'X')
        self.assertTrue(terrain.is_hazardous)
    
    def test_teleport_terrain_properties(self):
        terrain = Terrain(TerrainType.TELEPORT)
        self.assertEqual(terrain.movement_cost, 1)
        self.assertEqual(terrain.damage, 0)
        self.assertEqual(terrain.symbol, 'O')
        self.assertFalse(terrain.is_hazardous)


class TestCell(unittest.TestCase):
    
    def test_cell_creation(self):
        cell = Cell(5, 10)
        self.assertEqual(cell.x, 5)
        self.assertEqual(cell.y, 10)
        self.assertEqual(cell.terrain.terrain_type, TerrainType.EMPTY)
    
    def test_cell_with_terrain_type(self):
        cell = Cell(0, 0, TerrainType.DESERT)
        self.assertEqual(cell.terrain.terrain_type, TerrainType.DESERT)
    
    def test_cell_position_property(self):
        cell = Cell(7, 12)
        self.assertEqual(cell.position, (7, 12))
    
    def test_cell_initial_state(self):
        cell = Cell(0, 0)
        self.assertIsNone(cell.occupant)
        self.assertEqual(cell.items, [])
        self.assertIsNone(cell.teleport_destination)
    
    def test_cell_is_occupied(self):
        cell = Cell(0, 0)
        self.assertFalse(cell.is_occupied)
        
        cell.occupant = "test_agent"
        self.assertTrue(cell.is_occupied)
    
    def test_cell_is_empty(self):
        cell = Cell(0, 0)
        self.assertTrue(cell.is_empty)
        
        cell.items.append("item")
        self.assertFalse(cell.is_empty)
    
    def test_cell_movement_cost(self):
        cell = Cell(0, 0, TerrainType.ROCKY)
        self.assertEqual(cell.movement_cost, 3)
    
    def test_cell_terrain_damage(self):
        cell = Cell(0, 0, TerrainType.HOSTILE)
        self.assertEqual(cell.terrain_damage, 5)
    
    def test_place_occupant_success(self):
        cell = Cell(0, 0)
        result = cell.place_occupant("agent")
        self.assertTrue(result)
        self.assertEqual(cell.occupant, "agent")
    
    def test_place_occupant_fail_already_occupied(self):
        cell = Cell(0, 0)
        cell.place_occupant("agent1")
        result = cell.place_occupant("agent2")
        self.assertFalse(result)
        self.assertEqual(cell.occupant, "agent1")
    
    def test_remove_occupant(self):
        cell = Cell(0, 0)
        cell.place_occupant("agent")
        removed = cell.remove_occupant()
        self.assertEqual(removed, "agent")
        self.assertIsNone(cell.occupant)
    
    def test_add_item(self):
        cell = Cell(0, 0)
        cell.add_item("medkit")
        self.assertIn("medkit", cell.items)
    
    def test_remove_item_success(self):
        cell = Cell(0, 0)
        cell.add_item("medkit")
        removed = cell.remove_item("medkit")
        self.assertEqual(removed, "medkit")
        self.assertNotIn("medkit", cell.items)
    
    def test_remove_item_not_found(self):
        cell = Cell(0, 0)
        removed = cell.remove_item("nonexistent")
        self.assertIsNone(removed)
    
    def test_set_teleport_destination(self):
        cell = Cell(0, 0)
        cell.set_teleport_destination(10, 15)
        self.assertEqual(cell.teleport_destination, (10, 15))
    
    def test_get_display_symbol_empty(self):
        cell = Cell(0, 0)
        self.assertEqual(cell.get_display_symbol(), '.')
    
    def test_get_display_symbol_with_item(self):
        cell = Cell(0, 0)
        cell.add_item("item")
        self.assertEqual(cell.get_display_symbol(), '*')
    
    def test_get_display_symbol_with_occupant(self):
        class MockAgent:
            symbol = 'P'
        
        cell = Cell(0, 0)
        cell.add_item("item")
        cell.place_occupant(MockAgent())
        self.assertEqual(cell.get_display_symbol(), 'P')


class TestGrid(unittest.TestCase):
    
    def test_grid_creation_default(self):
        grid = Grid()
        self.assertEqual(grid.width, 20)
        self.assertEqual(grid.height, 20)
    
    def test_grid_creation_custom_size(self):
        grid = Grid(30, 25)
        self.assertEqual(grid.width, 30)
        self.assertEqual(grid.height, 25)
    
    def test_grid_cells_created(self):
        grid = Grid(10, 10)
        self.assertEqual(len(grid.cells), 10)
        self.assertEqual(len(grid.cells[0]), 10)
    
    def test_wrap_coordinates_no_wrap_needed(self):
        grid = Grid(20, 20)
        x, y = grid.wrap_coordinates(5, 10)
        self.assertEqual((x, y), (5, 10))
    
    def test_wrap_coordinates_positive_overflow(self):
        grid = Grid(20, 20)
        x, y = grid.wrap_coordinates(25, 22)
        self.assertEqual((x, y), (5, 2))
    
    def test_wrap_coordinates_negative(self):
        grid = Grid(20, 20)
        x, y = grid.wrap_coordinates(-3, -5)
        self.assertEqual((x, y), (17, 15))
    
    def test_get_cell(self):
        grid = Grid(20, 20)
        cell = grid.get_cell(5, 10)
        self.assertEqual(cell.x, 5)
        self.assertEqual(cell.y, 10)
    
    def test_get_cell_with_wrapping(self):
        grid = Grid(20, 20)
        cell = grid.get_cell(25, 22)
        self.assertEqual(cell.x, 5)
        self.assertEqual(cell.y, 2)
    
    def test_set_terrain(self):
        grid = Grid(20, 20)
        grid.set_terrain(5, 5, TerrainType.HOSTILE)
        cell = grid.get_cell(5, 5)
        self.assertEqual(cell.terrain.terrain_type, TerrainType.HOSTILE)
    
    def test_get_adjacent_cells(self):
        grid = Grid(20, 20)
        adjacent = grid.get_adjacent_cells(5, 5)
        self.assertEqual(len(adjacent), 8)
    
    def test_get_cardinal_adjacent(self):
        grid = Grid(20, 20)
        cardinal = grid.get_cardinal_adjacent(5, 5)
        self.assertEqual(len(cardinal), 4)
    
    def test_find_empty_cell(self):
        grid = Grid(20, 20)
        cell = grid.find_empty_cell()
        self.assertIsNotNone(cell)
        self.assertFalse(cell.is_occupied)
    
    def test_find_random_cell_of_type(self):
        grid = Grid(20, 20)
        grid.set_terrain(5, 5, TerrainType.DESERT)
        cell = grid.find_random_cell_of_type(TerrainType.DESERT)
        self.assertIsNotNone(cell)
        self.assertEqual(cell.terrain.terrain_type, TerrainType.DESERT)
    
    def test_calculate_distance_same_point(self):
        grid = Grid(20, 20)
        distance = grid.calculate_distance(5, 5, 5, 5)
        self.assertEqual(distance, 0)
    
    def test_calculate_distance_adjacent(self):
        grid = Grid(20, 20)
        distance = grid.calculate_distance(5, 5, 6, 5)
        self.assertEqual(distance, 1)
    
    def test_calculate_distance_diagonal(self):
        grid = Grid(20, 20)
        distance = grid.calculate_distance(5, 5, 7, 7)
        self.assertEqual(distance, 2)
    
    def test_calculate_distance_wrap_around(self):
        grid = Grid(20, 20)
        distance = grid.calculate_distance(0, 0, 19, 0)
        self.assertEqual(distance, 1)
    
    def test_get_cells_in_radius(self):
        grid = Grid(20, 20)
        cells = grid.get_cells_in_radius(10, 10, 2)
        self.assertGreater(len(cells), 0)
    
    def test_generate_terrain(self):
        grid = Grid(20, 20)
        grid.generate_terrain()
        terrain_types_found = set()
        for row in grid.cells:
            for cell in row:
                terrain_types_found.add(cell.terrain.terrain_type)
        self.assertGreater(len(terrain_types_found), 1)
    
    def test_create_teleport_pair(self):
        grid = Grid(20, 20)
        grid.create_teleport_pair(0, 0, 19, 19)
        cell1 = grid.get_cell(0, 0)
        cell2 = grid.get_cell(19, 19)
        self.assertEqual(cell1.terrain.terrain_type, TerrainType.TELEPORT)
        self.assertEqual(cell2.terrain.terrain_type, TerrainType.TELEPORT)
        self.assertEqual(cell1.teleport_destination, (19, 19))
        self.assertEqual(cell2.teleport_destination, (0, 0))
    
    def test_get_all_occupied_cells(self):
        grid = Grid(20, 20)
        cell = grid.get_cell(5, 5)
        cell.place_occupant("agent")
        occupied = grid.get_all_occupied_cells()
        self.assertEqual(len(occupied), 1)
        self.assertEqual(occupied[0].position, (5, 5))
    
    def test_clear_all_occupants(self):
        grid = Grid(20, 20)
        cell = grid.get_cell(5, 5)
        cell.place_occupant("agent")
        cell.add_item("item")
        grid.clear_all_occupants()
        self.assertIsNone(cell.occupant)
        self.assertEqual(cell.items, [])


class TestGridAgentPlacement(unittest.TestCase):
    
    def setUp(self):
        self.grid = Grid(20, 20)
        
        class MockAgent:
            def __init__(self):
                self.x = 0
                self.y = 0
        
        self.MockAgent = MockAgent
    
    def test_place_agent_specific_position(self):
        agent = self.MockAgent()
        result = self.grid.place_agent(agent, 5, 10)
        self.assertTrue(result)
        self.assertEqual(agent.x, 5)
        self.assertEqual(agent.y, 10)
    
    def test_place_agent_random_position(self):
        agent = self.MockAgent()
        result = self.grid.place_agent(agent)
        self.assertTrue(result)
        cell = self.grid.get_cell(agent.x, agent.y)
        self.assertEqual(cell.occupant, agent)
    
    def test_move_agent(self):
        agent = self.MockAgent()
        self.grid.place_agent(agent, 5, 5)
        result = self.grid.move_agent(agent, 6, 6)
        self.assertTrue(result)
        self.assertEqual(agent.x, 6)
        self.assertEqual(agent.y, 6)
        
        old_cell = self.grid.get_cell(5, 5)
        new_cell = self.grid.get_cell(6, 6)
        self.assertIsNone(old_cell.occupant)
        self.assertEqual(new_cell.occupant, agent)
    
    def test_move_agent_blocked(self):
        agent1 = self.MockAgent()
        agent2 = self.MockAgent()
        
        self.grid.place_agent(agent1, 5, 5)
        self.grid.place_agent(agent2, 6, 6)
        
        result = self.grid.move_agent(agent1, 6, 6)
        self.assertFalse(result)
        self.assertEqual(agent1.x, 5)
        self.assertEqual(agent1.y, 5)
    
    def test_move_agent_wrapping(self):
        agent = self.MockAgent()
        self.grid.place_agent(agent, 19, 19)
        result = self.grid.move_agent(agent, 20, 20)
        self.assertTrue(result)
        self.assertEqual(agent.x, 0)
        self.assertEqual(agent.y, 0)


class TestGridTeleportation(unittest.TestCase):
    
    def setUp(self):
        self.grid = Grid(20, 20)
        self.grid.create_teleport_pair(0, 0, 10, 10)
        
        class MockAgent:
            def __init__(self):
                self.x = 0
                self.y = 0
        
        self.MockAgent = MockAgent
    
    def test_teleport_on_move(self):
        agent = self.MockAgent()
        self.grid.place_agent(agent, 1, 0)
        self.grid.move_agent(agent, 0, 0)
        self.assertEqual(agent.x, 10)
        self.assertEqual(agent.y, 10)
    
    def test_teleport_destination_occupied(self):
        agent1 = self.MockAgent()
        agent2 = self.MockAgent()
        
        self.grid.place_agent(agent2, 10, 10)
        self.grid.place_agent(agent1, 1, 0)
        
        self.grid.move_agent(agent1, 0, 0)
        self.assertEqual(agent1.x, 0)
        self.assertEqual(agent1.y, 0)


if __name__ == '__main__':
    unittest.main()
