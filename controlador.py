class Controlador:
    def __init__(self):
        self.detected_dirt_cells = {}  # Usamos un diccionario para manejar asignaciones

    def add_detected_dirt(self, cell):
        if cell not in self.detected_dirt_cells:
            self.detected_dirt_cells[cell] = None  # Ningún robot asignado aún
            print(f"Nueva celda sucia detectada y añadida: {cell}")
            return True
        return False

    def assign_task_to_robot(self, cell, robot_id):
        if cell in self.detected_dirt_cells and self.detected_dirt_cells[cell] is None:
            self.detected_dirt_cells[cell] = robot_id
            return True
        return False

    def task_completed(self, cell, robot_id):
        if cell in self.detected_dirt_cells and self.detected_dirt_cells[cell] == robot_id:
            del self.detected_dirt_cells[cell]
            print(f"Robot {robot_id} ha completado la limpieza de la celda {cell}.")
