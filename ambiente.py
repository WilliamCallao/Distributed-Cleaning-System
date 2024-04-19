import pygame
import numpy as np
import random
import time
import math
from robot import Robot
from controlador import Controlador

class Ambiente:
    def __init__(self):
        """
        Constructor que inicializa el ambiente con dimensiones específicas y 
        configuraciones predeterminadas para la simulación. Establece el 
        tamaño de la ventana, el número de columnas y filas, el tamaño de 
        las cuadrículas, y los colores usados.
        """
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 600
        self.COLS, self.ROWS = 20, 15
        self.SQUARE_SIZE = 40
        self.WHITE = (255, 255, 255)
        self.GRAY = (200, 200, 200)
        self.RED = (255, 0, 0)
        self.DIRT_COLOR = (139, 69, 19)
        self.DETECTED_DIRT_COLOR = (128, 0, 128)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Simulación de Ambiente de Limpieza")
        self.grid = np.zeros((self.ROWS, self.COLS))
        self.centers = np.array([[(x * self.SQUARE_SIZE + self.SQUARE_SIZE // 2,
                                y * self.SQUARE_SIZE + self.SQUARE_SIZE // 2) for x in range(self.COLS)]
                                for y in range(self.ROWS)])
        self.last_dirt_time = time.time()
        self.controlador = Controlador()
        self.robots = [
            Robot(self, self.WIDTH, self.HEIGHT, self.controlador),  # Primer robot
            Robot(self, self.WIDTH, self.HEIGHT, self.controlador)   # Segundo robot
        ]

    def detect_dirt_around(self, pos_x, pos_y, radius=800):
        """
        Detecta y marca las celdas sucias dentro de un radio dado alrededor de una posición específica.

        Args:
            pos_x (int): Coordenada X del centro.
            pos_y (int): Coordenada Y del centro.
            radius (int): Radio de detección.

        Returns:
            list: Lista de coordenadas del centro de las celdas sucias detectadas.
        """
        dirty_cells = []
        print(f"Detección de suciedad iniciada desde la posición ({pos_x}, {pos_y})")
        for y in range(self.ROWS):
            for x in range(self.COLS):
                center_x, center_y = self.centers[y, x]
                if math.sqrt((center_x - pos_x) ** 2 + (center_y - pos_y) ** 2) <= radius and self.grid[y, x] == 1:
                    dirty_cells.append((x, y))
                    self.mark_cell_as_detected(x, y)
                    print(f"Suciedad detectada y marcada en ({center_x}, {center_y})")
        return dirty_cells

    def handle_click(self, pos):
        """
        Maneja los eventos de clic del mouse para detectar suciedad alrededor del punto clickeado.
        """
        x, y = pos
        self.detect_dirt_around(x, y, 80)
        
    def add_dirt(self):
        """
        Añade suciedad en una posición aleatoria dentro de la grilla que esté
        actualmente limpia.
        """
        empty = np.where(self.grid == 0)
        if empty[0].size > 0:
            idx = random.choice(range(len(empty[0])))
            self.grid[empty[0][idx], empty[1][idx]] = 1

    def draw_grid(self):
        """
        Dibuja la grilla en la ventana de Pygame. Cada cuadrícula es delineada y
        un punto rojo es colocado en su centro.
        """
        for x in range(self.COLS):
            for y in range(self.ROWS):
                rect = pygame.Rect(x * self.SQUARE_SIZE, y * self.SQUARE_SIZE,
                                self.SQUARE_SIZE, self.SQUARE_SIZE)
                pygame.draw.rect(self.screen, self.GRAY, rect, 1)
                center_x, center_y = self.centers[y, x]
                pygame.draw.circle(self.screen, self.RED, (center_x, center_y), 2)

    def draw_dirt(self):
        """
        Visualiza las cuadrículas sucias en la ventana de Pygame, cambiando el
        color de las cuadrículas de acuerdo con su estado de suciedad.
        """
        for x in range(self.COLS):
            for y in range(self.ROWS):
                color = self.DIRT_COLOR if self.grid[y, x] == 1 else (self.DETECTED_DIRT_COLOR if self.grid[y, x] == 2 else self.WHITE)
                if self.grid[y, x] > 0:
                    dirt_rect = pygame.Rect(x * self.SQUARE_SIZE, y * self.SQUARE_SIZE,
                                            self.SQUARE_SIZE, self.SQUARE_SIZE)
                    pygame.draw.rect(self.screen, color, dirt_rect)

    def get_dirty_cells_within_radius(self, pos_x, pos_y, radius=80):
        """
        Devuelve una lista de celdas sucias dentro de un radio especificado
        alrededor de un punto dado.

        Args:
            pos_x (int): Coordenada x del punto central.
            pos_y (int): Coordenada y del punto central.
            radius (int): Radio alrededor del punto central para buscar celdas sucias.

        Returns:
            list of tuple: Lista de coordenadas (x, y) de celdas sucias.
        """
        dirty_cells = []
        for y in range(self.ROWS):
            for x in range(self.COLS):
                center_x, center_y = self.centers[y, x]
                if math.sqrt((center_x - pos_x) ** 2 + (center_y - pos_y) ** 2) <= radius and self.grid[y, x] == 1:
                    dirty_cells.append((x, y))
        return dirty_cells

    def mark_cell_as_detected(self, x, y):
        """
        Cambia el estado de una celda de sucia a detectada, modificando su color a morado.

        Args:
            x (int): Coordenada x de la celda en la grilla.
            y (int): Coordenada y de la celda en la grilla.
        """
        if 0 <= x < self.COLS and 0 <= y < self.ROWS and self.grid[y, x] == 1:
            self.grid[y, x] = 2  # Mark as detected dirt with a different color

    def update(self):
        """
        Actualiza el estado del ambiente, añadiendo suciedad aleatoriamente
        cada medio segundo.
        """
        # if time.time() - self.last_dirt_time > 0.01:
        self.add_dirt()
        self.last_dirt_time = time.time()

    def run(self):
        """
        Ejecuta el bucle principal de la aplicación, gestionando eventos de
        Pygame y actualizando la visualización.
        """
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
            
            for robot in self.robots:
                robot.update()

            self.update()
            self.screen.fill(self.WHITE)
            self.draw_grid()
            self.draw_dirt()
            
            # self.screen.blit(self.robot.image, self.robot.rect)
            # Dibuja cada robot
            for robot in self.robots:
                self.screen.blit(robot.image, robot.rect)
        
            pygame.display.flip()
            pygame.time.wait(100)

        pygame.quit()


