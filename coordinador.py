import numpy as np

class Coordinador:
    def __init__(self, rows, cols):
        self.grid = np.zeros((rows, cols))  # Matriz de cuadrantes

    def request_cleaning(self, x, y):
        """Un robot solicita limpiar en (x, y)."""
        if self.grid[x, y] == 0:
            self.grid[x, y] = 2  # Programar para limpieza
            return True
        return False

    def mark_cleaned(self, x, y):
        """Marca el cuadrante (x, y) como limpiado."""
        self.grid[x, y] = 1

    def update(self):
        """Reduce el estado de limpieza con el tiempo."""
        self.grid[self.grid > 0] -= 0.1  # Decrementa para simular 'envejecimiento' de la limpieza
