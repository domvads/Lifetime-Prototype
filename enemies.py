import pygame


class Enemy:
    def __init__(self, pos, radius=20, color=(200, 50, 50)):
        self.pos = pygame.Vector2(pos)
        self.radius = radius
        self.color = color
        self.hp = 100

    def take_damage(self, damage):
        self.hp -= damage

    def is_dead(self):
        return self.hp <= 0

    def draw(self, surface, camera):
        screen_pos = camera.world_to_screen(self.pos, surface.get_size())
        pygame.draw.circle(
            surface, self.color, (int(screen_pos.x), int(screen_pos.y)), self.radius
        )
