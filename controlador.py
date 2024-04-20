class Controlador:
    def __init__(self):
        self.detected_dirt_cells = set()

    def add_detected_dirt(self, cell):
        if cell not in self.detected_dirt_cells:
            self.detected_dirt_cells.add(cell)
            print(f"Nueva celda sucia detectada y añadida: {cell}")
            return True
        return False

    def check_dirt(self, cell):
        return cell in self.detected_dirt_cells

    def find_closest_dirt(self, x, y, cell_centers):
        if self.detected_dirt_cells:
            # Convertir cada coordenada de celda a su centro usando la matriz de centros de celdas
            cell_positions = [(cell_centers[cy][cx][0], cell_centers[cy][cx][1]) for cx, cy in self.detected_dirt_cells]
            closest_dirt = min(self.detected_dirt_cells, key=lambda cell: (cell_centers[cell[1]][cell[0]][0] - x)**2 + (cell_centers[cell[1]][cell[0]][1] - y)**2)
            return closest_dirt
        return None
