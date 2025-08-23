import pygame

ENEMY_HP = 40
ENEMY_SPEED = 200
ENEMY_DAMAGE = 10
ENEMY_ATTACK_RANGE = 40
ENEMY_WINDUP = 0.3
ENEMY_COOLDOWN = 1.0


class Enemy:
    def __init__(self, pos, radius=20, color=(200, 50, 50)):
        self.pos = pygame.Vector2(pos)
        self.radius = radius
        self.color = color
        self.hp = ENEMY_HP
        self.speed = ENEMY_SPEED
        self.damage = ENEMY_DAMAGE
        self.attack_range = ENEMY_ATTACK_RANGE
        self.windup = ENEMY_WINDUP
        self.cooldown = ENEMY_COOLDOWN
        self.attack_timer = 0
        self.windup_timer = 0

    def take_damage(self, damage):
        self.hp -= damage

    def is_dead(self):
        return self.hp <= 0

    def update(self, dt, player):
        if self.hp <= 0:
            return
        to_player = player.pos - self.pos
        dist = to_player.length()
        direction = to_player.normalize() if dist > 0 else pygame.Vector2()
        self.attack_timer = max(0, self.attack_timer - dt)
        if self.windup_timer > 0:
            self.windup_timer -= dt
            if self.windup_timer <= 0 and dist <= self.attack_range:
                player.take_damage(self.damage)
                self.attack_timer = self.cooldown
        elif dist <= self.attack_range and self.attack_timer <= 0:
            self.windup_timer = self.windup
        else:
            self.pos += direction * self.speed * dt

    def draw(self, surface, camera):
        screen_pos = camera.world_to_screen(self.pos, surface.get_size())
        pygame.draw.circle(
            surface, self.color, (int(screen_pos.x), int(screen_pos.y)), self.radius
        )
