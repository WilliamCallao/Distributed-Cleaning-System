class Controlador:
    def __init__(self):
        self.detected_dirt_cells = set()  # Usamos un conjunto para evitar duplicados

    def add_detected_dirt(self, cell):
        """
        Añade una celda a la lista de celdas sucias detectadas si aún no ha sido detectada.
        """
        if cell not in self.detected_dirt_cells:
            self.detected_dirt_cells.add(cell)
            print(f"Nueva celda sucia detectada y añadida: {cell}")
            return True
        return False

    def check_dirt(self, cell):
        """
        Verifica si una celda específica ya ha sido marcada como sucia.
        """
        return cell in self.detected_dirt_cells
