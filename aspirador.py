import pygame
import random

class Aspirador(pygame.sprite.Sprite):
    def __init__(self, environment):
        super().__init__()
        self.image = pygame.Surface((40, 40))  # Tamaño igual al de la cuadrícula
        self.image.fill((255, 0, 0))  # Color inicial rojo
        self.rect = self.image.get_rect()
        self.environment = environment
        self.velocity = [random.choice([-4, 4]), random.choice([-4, 4])]

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        if self.rect.left <= 0 or self.rect.right >= self.environment.WIDTH:
            self.velocity[0] = -self.velocity[0]
        if self.rect.top <= 0 or self.rect.bottom >= self.environment.HEIGHT:
            self.velocity[1] = -self.velocity[1]

        # Detect and clean dirt
        dirty_cells = self.environment.detect_dirt_within_radius((self.rect.centerx, self.rect.centery))
        for cell in dirty_cells:
            self.environment.change_cell_color_to_blue(*cell)
