import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from grid import Grid
from renderer import GridRenderer


def test_grid_system():
    print("=" * 50)
    print("PREDATOR: BADLANDS SIMULATION")
    print("Grid System Test")
    print("=" * 50)
    
    grid = Grid(20, 20)
    grid.generate_terrain()
    
    grid.create_teleport_pair(2, 2, 17, 17)
    grid.create_teleport_pair(5, 15, 15, 5)
    
    renderer = GridRenderer(grid)
    
    print("\nGenerated World Map:")
    renderer.render(use_colors=True)
    renderer.render_legend()
    renderer.render_statistics()
    
    print("\n" + "=" * 50)
    print("Testing Wrap-Around Movement")
    print("=" * 50)
    
    test_positions = [
        (0, 0, -1, 0),
        (19, 10, 1, 0),
        (10, 0, 0, -1),
        (10, 19, 0, 1)
    ]
    
    for start_x, start_y, dx, dy in test_positions:
        new_x, new_y = grid.wrap_coordinates(start_x + dx, start_y + dy)
        print(f"  From ({start_x}, {start_y}) + ({dx}, {dy}) = ({new_x}, {new_y})")
    
    print("\n" + "=" * 50)
    print("Testing Distance Calculation (Toroidal)")
    print("=" * 50)
    
    distance_tests = [
        (0, 0, 19, 19),
        (0, 0, 10, 10),
        (5, 5, 15, 15)
    ]
    
    for x1, y1, x2, y2 in distance_tests:
        dist = grid.calculate_distance(x1, y1, x2, y2)
        print(f"  Distance from ({x1}, {y1}) to ({x2}, {y2}): {dist}")
    
    print("\n" + "=" * 50)
    print("Grid System Test Complete")
    print("=" * 50)


if __name__ == "__main__":
    test_grid_system()
