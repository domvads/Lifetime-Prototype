import pygame


class Projectile:
    def __init__(self, pos, velocity, damage, radius=5, color=(255, 255, 0)):
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(velocity)
        self.damage = damage
        self.radius = radius
        self.color = color
        self.alive = True

    def update(self, dt, enemies):
        self.pos += self.velocity * dt
        for enemy in enemies:
            if (enemy.pos - self.pos).length() <= self.radius + enemy.radius:
                enemy.take_damage(self.damage)
                self.alive = False
                break

    def draw(self, surface, camera):
        screen_pos = camera.world_to_screen(self.pos, surface.get_size())
        pygame.draw.circle(
            surface, self.color, (int(screen_pos.x), int(screen_pos.y)), self.radius
        )
