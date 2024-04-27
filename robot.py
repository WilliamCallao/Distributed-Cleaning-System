import pygame
import random
import math

class Robot(pygame.sprite.Sprite):
    def __init__(self, ambiente, width, height, controlador):
        super().__init__()
        self.image = pygame.image.load('robot_image.png')
        self.image = pygame.transform.scale(self.image, (50, 60))
        # self.rect = self.image.get_rect(center=(20, 20))
        self.rect = self.image.get_rect(center=(random.randint(0, width), random.randint(0, height)))
        self.ambiente = ambiente
        self.width = width
        self.height = height
        self.controlador = controlador
        self.velocity = [random.choice([-1, 1]), random.choice([-4, 4])]
        self.target_position = None
        self.id = f"Robot({self.rect.centerx}, {self.rect.centery})"  # Identificador único basado en la posición inicial
        self.assigned_dirt = None
    
    def remove(self):
        # Libera cualquier tarea asignada cuando el robot es eliminado
        if self.assigned_dirt:
            self.controlador.release_dirt(self.assigned_dirt)
            print(f"{self.id} ha liberado la suciedad asignada en {self.assigned_dirt} antes de ser eliminado.")


    def update(self):
        self.detect_and_mark_dirt()
        if self.target_position:
            self.move_to_target()
        else:
            self.random_movement()
            self.report_dirt_info()


    def move_to_target(self):
        target_x, target_y = self.target_position
        dx, dy = target_x - self.rect.centerx, target_y - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 20:  # Aumentamos el umbral a 20 para una mayor tolerancia
            self.reassess_target()
            speed = min(4, distance / 10)  # Ajustar la velocidad basada en la distancia
            norm_dx, norm_dy = dx / distance, dy / distance
            self.rect.x += int(norm_dx * speed)
            self.rect.y += int(norm_dy * speed)
        else:
            print(f"{self.id} reached the target at ({target_x}, {target_y})")
            # Convertir la posición de píxeles a índices de grilla
            grid_x = target_x // self.ambiente.SQUARE_SIZE
            grid_y = target_y // self.ambiente.SQUARE_SIZE
            self.ambiente.clean_cell((target_x, target_y))  # Limpia la celda en la grilla
            self.controlador.remove_dirt((grid_x, grid_y))  # Elimina la celda de la lista de celdas sucias
            self.target_position = None

    def random_movement(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if self.rect.left <= 0 or self.rect.right >= self.width or self.rect.top <= 0 or self.rect.bottom >= self.height:
            self.adjust_direction()

    def adjust_direction(self):
        # Verifica colisión con el borde izquierdo o derecho
        if self.rect.left <= 0 or self.rect.right >= self.width:
            self.velocity[0] = -self.velocity[0]  # Invierte la velocidad horizontal
            self.velocity[1] = random.choice([-1, 1]) * random.uniform(0.5, 4)  # Cambio aleatorio en la dirección vertical

        # Verifica colisión con el borde superior o inferior
        if self.rect.top <= 0 or self.rect.bottom >= self.height:
            self.velocity[1] = -self.velocity[1]  # Invierte la velocidad vertical
            self.velocity[0] = random.choice([-1, 1]) * random.uniform(0.5, 4)  # Cambio aleatorio en la dirección horizontal

        # Asegurarse de que el robot no quede parcialmente fuera de los límites
        self.rect.x = max(0, min(self.rect.x, self.width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, self.height - self.rect.height))

        # Normalizar la velocidad para mantener la velocidad constante y asegurarse de que el movimiento sea fluido
        speed = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
        norm_vx, norm_vy = self.velocity[0] / speed, self.velocity[1] / speed
        self.velocity[0] = norm_vx * speed
        self.velocity[1] = norm_vy * speed
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
        grid_x = x // self.ambiente.SQUARE_SIZE
        grid_y = y // self.ambiente.SQUARE_SIZE
        self.assigned_dirt = (grid_x, grid_y)  # Guarda la tarea actual asignada
        print(f"{self.id} set target to ({x}, {y})")



    def report_dirt_info(self):
        cell_centers = self.ambiente.get_cell_centers()
        closest_dirt = self.controlador.find_closest_dirt(self.rect.centerx, self.rect.centery, cell_centers)
        dirt_count = len(self.controlador.detected_dirt_cells) + len(self.controlador.reserved_dirt_cells)  # Considera también las reservadas

        if closest_dirt:
            closest_pos = cell_centers[closest_dirt[1]][closest_dirt[0]]
            if self.controlador.reserve_dirt(closest_dirt):
                self.set_target_position(closest_pos[0], closest_pos[1])
                print(f"{self.id}: {dirt_count} sucias. La más cercana {closest_pos}.")
            else:
                print(f"{self.id}: Buscando nueva celda...")
        else:
            print(f"{self.id}: No hay celdas sucias detectadas o disponibles.")

    def reassess_target(self):
        current_target_grid_x = self.target_position[0] // self.ambiente.SQUARE_SIZE
        current_target_grid_y = self.target_position[1] // self.ambiente.SQUARE_SIZE
        current_target_pos = (self.target_position[0], self.target_position[1])

        cell_centers = self.ambiente.get_cell_centers()
        closest_dirt = self.controlador.find_closest_dirt(self.rect.centerx, self.rect.centery, cell_centers)

        if closest_dirt:
            closest_dirt_pos = cell_centers[closest_dirt[1]][closest_dirt[0]]
            distance_to_current_target = math.sqrt((current_target_pos[0] - self.rect.centerx)**2 + (current_target_pos[1] - self.rect.centery)**2)
            distance_to_new_target = math.sqrt((closest_dirt_pos[0] - self.rect.centerx)**2 + (closest_dirt_pos[1] - self.rect.centery)**2)

            # Solo reasignar si el nuevo objetivo está al menos a mitad de camino hacia el objetivo actual
            if distance_to_new_target < distance_to_current_target / 2:
                if self.controlador.reserve_dirt(closest_dirt):
                    self.controlador.release_dirt((current_target_grid_x, current_target_grid_y))
                    self.set_target_position(closest_dirt_pos[0], closest_dirt_pos[1])
                    print(f"{self.id}: Cambiado el objetivo a {closest_dirt_pos} por estar significativamente más cerca.")
                    