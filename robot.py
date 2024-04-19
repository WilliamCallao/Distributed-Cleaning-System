import pygame
import random
import math

class Robot(pygame.sprite.Sprite):
    def __init__(self, ambiente, width, height, controlador):
        super().__init__()
        # Cargar la imagen PNG
        self.image = pygame.image.load('robot_image.png')  # Asegúrate de que 'robot_image.png' sea el nombre correcto de tu archivo.
        self.image = pygame.transform.scale(self.image, (50, 60))  # Ajustar el tamaño de la imagen a 20x20 píxeles

        # Posición inicial aleatoria dentro de los límites de la ventana
        x = random.randint(0, width)
        y = random.randint(0, height)
        self.rect = self.image.get_rect(center=(x, y))
        self.ambiente = ambiente
        self.width = width
        self.height = height
        self.controlador = controlador
        # Velocidad y dirección iniciales aleatorias
        self.velocity = [random.choice([-1, 1]), random.choice([-4, 4])]
        
    def update(self):
        # Mover el robot
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        # Comprobar colisión con los bordes y ajustar la dirección
        if self.rect.left <= 0 or self.rect.right >= self.width or self.rect.top <= 0 or self.rect.bottom >= self.height:
            self.adjust_direction()

        # Detectar y marcar suciedad a su paso
        self.detect_and_mark_dirt()

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
        # Detecta suciedad dentro de un radio de 80 píxeles
        dirty_cells = self.ambiente.get_dirty_cells_within_radius(
            self.rect.centerx, self.rect.centery, 80)
        
        for cell_x, cell_y in dirty_cells:
            # Verifica si la celda ya ha sido detectada usando el controlador
            if self.ambiente.controlador.add_detected_dirt((cell_x, cell_y)):
                self.ambiente.mark_cell_as_detected(cell_x, cell_y)