import pygame


class Projectile:
    def __init__(
        self,
        pos,
        velocity,
        damage,
        charge_factor=0.0,
        radius=5,
        color=(255, 255, 0),
        on_hit=None,
        pierce=False,
        delay=0.0,
        life_time=2.0,
    ):
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(velocity)
        self.damage = damage
        self.charge_factor = charge_factor
        self.radius = radius
        self.color = color
        self.alive = True
        self.on_hit = on_hit
        self.pierce = pierce
        self.delay = delay
        self.life_time = life_time
        self.hit_enemies = set()

    def update(self, dt, enemies):
        if self.delay > 0:
            self.delay -= dt
            return
        if not self.alive:
            return
        self.life_time -= dt
        if self.life_time <= 0:
            self.alive = False
            return
        self.pos += self.velocity * dt
        for enemy in enemies:
            if enemy in self.hit_enemies:
                continue
            if (enemy.pos - self.pos).length() <= self.radius + enemy.radius:
                enemy.take_damage(self.damage)
                self.hit_enemies.add(enemy)
                if self.on_hit:
                    self.on_hit(self.charge_factor)
                if not self.pierce:
                    self.alive = False
                    break

    def draw(self, surface, camera):
        if self.delay > 0 or not self.alive:
            return
        screen_pos = camera.world_to_screen(self.pos, surface.get_size())
        pygame.draw.circle(
            surface, self.color, (int(screen_pos.x), int(screen_pos.y)), self.radius
        )
