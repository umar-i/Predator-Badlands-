from terrain import TerrainType


class GridRenderer:
    
    TERRAIN_COLORS = {
        TerrainType.EMPTY: '\033[0m',
        TerrainType.DESERT: '\033[93m',
        TerrainType.ROCKY: '\033[90m',
        TerrainType.CANYON: '\033[91m',
        TerrainType.HOSTILE: '\033[31m',
        TerrainType.TRAP: '\033[35m',
        TerrainType.TELEPORT: '\033[96m'
    }
    
    RESET = '\033[0m'
    
    def __init__(self, grid):
        self.grid = grid
    
    def render_to_string(self, use_colors=True):
        lines = []
        
        header = '   '
        for x in range(self.grid.width):
            header += f'{x % 10}'
        lines.append(header)
        
        lines.append('  +' + '-' * self.grid.width + '+')
        
        for y in range(self.grid.height):
            row_str = f'{y:2d}|'
            for x in range(self.grid.width):
                cell = self.grid.get_cell(x, y)
                symbol = cell.get_display_symbol()
                
                if use_colors:
                    color = self.TERRAIN_COLORS.get(cell.terrain.terrain_type, self.RESET)
                    row_str += f'{color}{symbol}{self.RESET}'
                else:
                    row_str += symbol
            
            row_str += '|'
            lines.append(row_str)
        
        lines.append('  +' + '-' * self.grid.width + '+')
        
        return '\n'.join(lines)
    
    def render(self, use_colors=True):
        print(self.render_to_string(use_colors))
    
    def render_legend(self):
        print("\nTerrain Legend:")
        print("  . = Empty ground")
        print("  ~ = Desert")
        print("  ^ = Rocky terrain")
        print("  # = Canyon")
        print("  ! = Hostile zone")
        print("  X = Trap")
        print("  O = Teleport pad")
        print("  * = Item on ground")
    
    def render_cell_info(self, x, y):
        cell = self.grid.get_cell(x, y)
        print(f"\nCell ({x}, {y}):")
        print(f"  Terrain: {cell.terrain.terrain_type.name}")
        print(f"  Movement Cost: {cell.movement_cost}")
        print(f"  Terrain Damage: {cell.terrain_damage}")
        print(f"  Occupied: {cell.is_occupied}")
        if cell.occupant:
            print(f"  Occupant: {cell.occupant}")
        if cell.items:
            print(f"  Items: {len(cell.items)}")
        if cell.teleport_destination:
            print(f"  Teleports to: {cell.teleport_destination}")
    
    def render_statistics(self):
        terrain_counts = {t: 0 for t in TerrainType}
        occupied_count = 0
        item_count = 0
        
        for row in self.grid.cells:
            for cell in row:
                terrain_counts[cell.terrain.terrain_type] += 1
                if cell.is_occupied:
                    occupied_count += 1
                item_count += len(cell.items)
        
        print(f"\nGrid Statistics ({self.grid.width}x{self.grid.height}):")
        print(f"  Total Cells: {self.grid.width * self.grid.height}")
        print(f"  Occupied Cells: {occupied_count}")
        print(f"  Items on Ground: {item_count}")
        print("\n  Terrain Distribution:")
        for terrain_type, count in terrain_counts.items():
            percentage = (count / (self.grid.width * self.grid.height)) * 100
            print(f"    {terrain_type.name}: {count} ({percentage:.1f}%)")
