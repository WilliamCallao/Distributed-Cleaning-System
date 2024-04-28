import pygame
import numpy as np
import random
import time
import math
from robot import Robot
from controlador import Controlador

class Ambiente:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 600
        self.COLS, self.ROWS = 40, 30
        self.SQUARE_SIZE = 20
        self.BUTTON_COLOR = (30, 30, 30)
        self.BUTTON_HOVER_COLOR = (140, 140, 255)
        self.BUTTON_CLICK_COLOR = (80, 80, 220) 
        self.BUTTON_TEXT_COLOR = (255, 255, 255)
        self.WHITE = (255, 255, 255)
        self.GRAY = (200, 200, 200)
        self.RED = (255, 0, 0)
        self.DIRT_COLOR = (215, 171, 136)
        self.DETECTED_DIRT_COLOR = (90, 127, 184)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Simulación de Ambiente de Limpieza")
        self.grid = np.zeros((self.ROWS, self.COLS))
        self.centers = np.array([[(x * self.SQUARE_SIZE + self.SQUARE_SIZE // 2,
                                y * self.SQUARE_SIZE + self.SQUARE_SIZE // 2) for x in range(self.COLS)]
                                for y in range(self.ROWS)])
        self.last_dirt_time = time.time()
        self.dirt_delay = 0.5
        self.controlador = Controlador()
        self.robots = [Robot(self, self.WIDTH, self.HEIGHT, self.controlador) for _ in range(1)]
        self.font = pygame.font.Font(None, 24)
        self.setup_buttons()
        
        self.mouse_down = False
        
    def setup_buttons(self):
        self.buttons = {
            "robot_plus": {"rect": pygame.Rect(10, 10, 80, 30), "label": "+Robots"},
            "robot_minus": {"rect": pygame.Rect(100, 10, 80, 30), "label": "-Robots"},
            "dirt_plus": {"rect": pygame.Rect(190, 10, 80, 30), "label": "+Dirt"},
            "dirt_minus": {"rect": pygame.Rect(280, 10, 80, 30), "label": "-Dirt"},
            "dirt_stop": {"rect": pygame.Rect(370, 10, 150, 30), "label": "Stop/Start Dirt"}
        }
        
    def add_robot(self):
        if len(self.robots) < 10:
            self.robots.append(Robot(self, self.WIDTH, self.HEIGHT, self.controlador))

    def remove_robot(self):
        if self.robots:
            robot = self.robots.pop()
            robot.remove() 
            print(f"Robot eliminado: {robot.id}")

    def adjust_dirt_delay(self, increment):
        if increment:
            self.dirt_delay = max(0.1, self.dirt_delay - 0.1) 
        else:
            self.dirt_delay += 0.1 

    def toggle_dirt(self):
        if self.dirt_delay == float('inf'):
            self.dirt_delay = 0.5
        else:
            self.dirt_delay = float('inf')


    def draw_buttons(self):
        mouse_pos = pygame.mouse.get_pos()
        for key, button in self.buttons.items():
            if button["rect"].collidepoint(mouse_pos):
                if self.mouse_down:
                    color = self.BUTTON_CLICK_COLOR
                else:
                    color = self.BUTTON_HOVER_COLOR
            else:
                color = self.BUTTON_COLOR
            pygame.draw.rect(self.screen, color, button["rect"])
            label = self.font.render(button["label"], True, self.BUTTON_TEXT_COLOR)
            label_pos = label.get_rect(center=button["rect"].center)
            self.screen.blit(label, label_pos)
            
    def handle_click(self, pos):
        for key, button in self.buttons.items():
            if button["rect"].collidepoint(pos):
                getattr(self, key)()
                return
        
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
        for key, button in self.buttons.items():
            if button["rect"].collidepoint(pos):
                if key == "robot_plus":
                    self.add_robot()
                elif key == "robot_minus":
                    self.remove_robot()
                elif key == "dirt_plus":
                    self.adjust_dirt_delay(True)
                elif key == "dirt_minus":
                    self.adjust_dirt_delay(False)
                elif key == "dirt_stop":
                    self.toggle_dirt()
                return
        print("Clic fuera de los botones: Ignorado")
    
    def get_cell_centers(self):
        return self.centers

    def get_grid(self):
        return self.grid
    
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
        # for x in range(self.COLS):
        #     for y in range(self.ROWS):
        #         rect = pygame.Rect(x * self.SQUARE_SIZE, y * self.SQUARE_SIZE,
        #                         self.SQUARE_SIZE, self.SQUARE_SIZE)
        #         pygame.draw.rect(self.screen, self.GRAY, rect, 1)
        #         center_x, center_y = self.centers[y, x]
        #         pygame.draw.circle(self.screen, self.RED, (center_x, center_y), 2)

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
            self.grid[y, x] = 2

    def update(self):
        current_time = time.time()
        if self.dirt_delay != float('inf') and current_time - self.last_dirt_time > self.dirt_delay:
            self.add_dirt()
            self.last_dirt_time = current_time

    def clean_cell(self, pos):
        """
        Limpia una celda específica en la grilla basándose en la posición del clic del mouse,
        cambiando su estado a limpio.

        Args:
            pos (tuple): Posición (x, y) del clic del mouse en píxeles.
        """
        x, y = pos
        grid_x = x // self.SQUARE_SIZE 
        grid_y = y // self.SQUARE_SIZE

        if 0 <= grid_x < self.COLS and 0 <= grid_y < self.ROWS:
            self.grid[grid_y, grid_x] = 0
            print(f"Celda limpiada en posición ({grid_x}, {grid_y}).")

    def run(self):
        running = True
        while running:
            self.mouse_down = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.mouse_down = True
                        self.handle_click(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.mouse_down = False
            
            for robot in self.robots:
                robot.update()

            self.update()
            self.screen.fill(self.WHITE)
            self.draw_grid()
            self.draw_dirt()
            self.draw_buttons()
            
            for robot in self.robots:
                self.screen.blit(robot.image, robot.rect)
        
            pygame.display.flip()
            pygame.time.wait(100)

        pygame.quit()


