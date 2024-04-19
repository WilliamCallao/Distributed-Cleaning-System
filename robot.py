import pygame
import random
import math

class Robot(pygame.sprite.Sprite):
    def __init__(self, ambiente, width, height, controlador):
        super().__init__()
        self.image = pygame.image.load('robot_image.png')
        self.image = pygame.transform.scale(self.image, (50, 60))
        self.rect = self.image.get_rect(center=(random.randint(0, width), random.randint(0, height)))
        self.ambiente = ambiente
        self.width = width
        self.height = height
        self.controlador = controlador
        self.velocity = [random.choice([-1, 1]), random.choice([-4, 4])]
        self.current_task = None
        
    def update(self):
        if not self.current_task:
            self.find_task()
        self.move()
        self.detect_and_mark_dirt()

    def find_task(self):
        # Intenta obtener una tarea de limpieza si no tiene ninguna
        for cell in self.ambiente.controlador.detected_dirt_cells:
            if self.ambiente.controlador.assign_task_to_robot(cell, id(self)):
                self.current_task = cell
                print(f"Robot {id(self)} ha sido asignado a la celda {cell}.")
                break


    def move(self):
        if self.current_task:
            # Moverse hacia la celda asignada
            target_pos = self.ambiente.centers[self.current_task[1]][self.current_task[0]]
            self.rect.center = target_pos  # Simplificación del movimiento
            # Limpiar la celda y notificar al controlador
            self.ambiente.grid[self.current_task[1]][self.current_task[0]] = 0
            self.controlador.task_completed(self.current_task, id(self))
            self.current_task = None
        else:
            # Movimiento aleatorio como antes
            self.rect.x += self.velocity[0]
            self.rect.y += self.velocity[1]
            self.adjust_direction()
            
    def adjust_direction(self):
        # Calcular un nuevo ángulo aleatorio para el movimiento
        angle = random.uniform(0, 2 * math.pi)
        speed = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
        self.velocity[0] = speed * math.cos(angle)
        self.velocity[1] = speed * math.sin(angle)
        # Ajustar la posición para evitar quedarse atascado en los bordes
        self.rect.x = max(0, min(self.rect.x, self.width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, self.height - self.rect.height))

    def detect_and_mark_dirt(self):
            dirty_cells = self.ambiente.get_dirty_cells_within_radius(self.rect.centerx, self.rect.centery, 80)
            for cell_x, cell_y in dirty_cells:
                self.ambiente.controlador.add_detected_dirt((cell_x, cell_y))