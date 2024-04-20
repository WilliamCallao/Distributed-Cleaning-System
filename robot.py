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
        self.target_position = None
        self.id = f"Robot({self.rect.centerx}, {self.rect.centery})"  # Identificador único basado en la posición inicial

    def update(self):
        if self.target_position:
            self.move_to_target()
        else:
            self.random_movement()
        self.detect_and_mark_dirt()

    def move_to_target(self):
        target_x, target_y = self.target_position
        dx, dy = target_x - self.rect.centerx, target_y - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 20:  # Aumentamos el umbral a 10 para una mayor tolerancia
            speed = min(4, distance / 10)  # Ajustar la velocidad basada en la distancia
            norm_dx, norm_dy = dx / distance, dy / distance
            self.rect.x += int(norm_dx * speed)
            self.rect.y += int(norm_dy * speed)
        else:
            print(f"{self.id} reached the target at ({target_x}, {target_y})")
            self.target_position = None  # Resetear la posición objetivo al llegar

    def random_movement(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if self.rect.left <= 0 or self.rect.right >= self.width or self.rect.top <= 0 or self.rect.bottom >= self.height:
            self.adjust_direction()

    def adjust_direction(self):
        # Verifica colisión con el borde izquierdo o derecho
        if self.rect.left <= 0 or self.rect.right >= self.width:
            self.velocity[0] = -self.velocity[0]  # Invierte la velocidad horizontal
        # Verifica colisión con el borde superior o inferior
        if self.rect.top <= 0 or self.rect.bottom >= self.height:
            self.velocity[1] = -self.velocity[1]  # Invierte la velocidad vertical

        # Asegurarse de que el robot no quede parcialmente fuera de los límites
        self.rect.x = max(0, min(self.rect.x, self.width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, self.height - self.rect.height))

        # Normalizar la velocidad para mantener la velocidad constante
        speed = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
        norm_vx, norm_vy = self.velocity[0] / speed, self.velocity[1] / speed
        self.velocity[0] = norm_vx * speed
        self.velocity[1] = norm_vy * speed


    def detect_and_mark_dirt(self):
        dirty_cells = self.ambiente.get_dirty_cells_within_radius(
            self.rect.centerx, self.rect.centery, 80)
        for cell_x, cell_y in dirty_cells:
            if self.ambiente.controlador.add_detected_dirt((cell_x, cell_y)):
                self.ambiente.mark_cell_as_detected(cell_x, cell_y)

    def set_target_position(self, x, y):
        self.target_position = (x, y)
        print(f"{self.id} set target to ({x}, {y})")
