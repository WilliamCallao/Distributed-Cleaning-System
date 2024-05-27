import pygame
import random
import math

class Robot(pygame.sprite.Sprite):
    def __init__(self, ambiente, width, height, controlador):
        # Inicialización del robot y sus atributos básicos.
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load('robot_image.png'), (50, 60))
        self.rect = self.image.get_rect(center=(random.randint(0, width), random.randint(0, height)))
        self.ambiente = ambiente
        self.width = width
        self.height = height
        self.controlador = controlador
        self.velocity = [random.choice([-1, 1]), random.choice([-4, 4])]
        self.target_position = None
        self.id = f"Robot({self.rect.centerx}, {self.rect.centery})"
        self.assigned_dirt = None

    def update(self):
        # Actualiza el estado del robot en cada frame.
        self.detect_and_mark_dirt()
        if self.target_position:
            self.move_to_target()
        else:
            self.random_movement()
            self.report_dirt_info()
        self.avoid_collisions()

    def detect_and_mark_dirt(self):
        # Detecta y marca la suciedad dentro de un radio específico.
        dirty_cells = self.ambiente.get_dirty_cells_within_radius(self.rect.centerx, self.rect.centery, 100)
        for cell_x, cell_y in dirty_cells:
            if self.ambiente.controlador.add_detected_dirt((cell_x, cell_y)):
                self.ambiente.mark_cell_as_detected(cell_x, cell_y)

    def move_to_target(self):
        # Mueve el robot hacia la posición objetivo si la tiene asignada.
        target_x, target_y = self.target_position
        dx, dy = target_x - self.rect.centerx, target_y - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 20:
            self.reassess_target()
            speed = min(4, distance / 10)
            norm_dx, norm_dy = dx / distance, dy / distance
            self.rect.x += int(norm_dx * speed)
            self.rect.y += int(norm_dy * speed)
        else:
            self.ambiente.clean_cell((target_x, target_y))
            grid_x = target_x // self.ambiente.SQUARE_SIZE
            grid_y = target_y // self.ambiente.SQUARE_SIZE
            self.controlador.remove_dirt((grid_x, grid_y))
            self.target_position = None
            print(f"{self.id} reached the target at ({target_x}, {target_y})")

    def reassess_target(self):
        # Evalúa si sigue siendo óptimo perseguir el objetivo actual o si debe cambiarlo.
        current_target_grid_x, current_target_grid_y = self.target_position[0] // self.ambiente.SQUARE_SIZE, self.target_position[1] // self.ambiente.SQUARE_SIZE
        current_target_pos = self.target_position
        cell_centers = self.ambiente.get_cell_centers()
        closest_dirt = self.controlador.find_closest_dirt(self.rect.centerx, self.rect.centery, cell_centers)
        if closest_dirt:
            closest_dirt_pos = cell_centers[closest_dirt[1]][closest_dirt[0]]
            distance_to_current_target = math.sqrt((current_target_pos[0] - self.rect.centerx)**2 + (current_target_pos[1] - self.rect.centery)**2)
            distance_to_new_target = math.sqrt((closest_dirt_pos[0] - self.rect.centerx)**2 + (closest_dirt_pos[1] - self.rect.centery)**2)
            if distance_to_new_target < distance_to_current_target / 2:
                if self.controlador.reserve_dirt(closest_dirt):
                    self.controlador.release_dirt((current_target_grid_x, current_target_grid_y))
                    self.set_target_position(closest_dirt_pos[0], closest_dirt_pos[1])
                    print(f"{self.id}: Cambiado el objetivo a {closest_dirt_pos} por estar significativamente más cerca.")

    def random_movement(self):
        # Mueve el robot de forma aleatoria si no tiene un objetivo específico.
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if self.rect.left <= 0 or self.rect.right >= self.width or self.rect.top <= 0 or self.rect.bottom >= self.height:
            self.adjust_direction()

    def adjust_direction(self):
        # Ajusta la dirección del movimiento si el robot alcanza los límites del área.
        if self.rect.left <= 0 or self.rect.right >= self.width or self.rect.top <= 0 or self.rect.bottom >= self.height:
            angle = math.atan2(self.velocity[1], self.velocity[0])
            random_angle = random.uniform(-math.pi, math.pi)
            speed = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
            self.velocity[0] = speed * math.cos(angle + random_angle)
            self.velocity[1] = speed * math.sin(angle + random_angle)
        self.rect.x = max(0, min(self.rect.x, self.width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, self.height - self.rect.height))

    def avoid_collisions(self):
        # Lógica de evasión de colisiones para evitar que los robots se queden atascados.
        separation_distance = 30
        for robot in self.ambiente.robots:
            if robot != self:
                distance = math.sqrt((self.rect.centerx - robot.rect.centerx)**2 + (self.rect.centery - robot.rect.centery)**2)
                if distance < separation_distance:
                    angle = math.atan2(self.rect.centery - robot.rect.centery, self.rect.centerx - robot.rect.centerx)
                    self.rect.x += math.cos(angle) * 2
                    self.rect.y += math.sin(angle) * 2
                    # Movimiento adicional hacia la derecha para evitar trabarse
                    self.rect.x += math.sin(angle) * 1

    def set_target_position(self, x, y):
        # Establece una nueva posición objetivo para el robot.
        self.target_position = (x, y)
        grid_x = x // self.ambiente.SQUARE_SIZE
        grid_y = y // self.ambiente.SQUARE_SIZE
        self.assigned_dirt = (grid_x, grid_y)
        print(f"{self.id} set target to ({x}, {y})")

    def report_dirt_info(self):
        # Informa sobre la situación de la suciedad detectada y disponible.
        cell_centers = self.ambiente.get_cell_centers()
        closest_dirt = self.controlador.find_closest_dirt(self.rect.centerx, self.rect.centery, cell_centers)
        dirt_count = len(self.controlador.detected_dirt_cells) + len(self.controlador.reserved_dirt_cells)
        if closest_dirt:
            closest_pos = cell_centers[closest_dirt[1]][closest_dirt[0]]
            if self.controlador.reserve_dirt(closest_dirt):
                self.set_target_position(closest_pos[0], closest_pos[1])
                print(f"{self.id}: {dirt_count} sucias. La más cercana {closest_pos}.")
            else:
                print(f"{self.id}: Buscando nueva celda...")
        else:
            print(f"{self.id}: No hay celdas sucias detectadas o disponibles.")

    def remove(self):
        # Elimina el robot y libera la suciedad que tenía asignada.
        if self.assigned_dirt:
            self.controlador.release_dirt(self.assigned_dirt)
            print(f"{self.id} ha liberado la suciedad asignada en {self.assigned_dirt} antes de ser eliminado.")
