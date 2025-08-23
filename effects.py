import math
import pygame


class SlashEffect:
    def __init__(self, pos, direction, arc, radius, duration=0.3, charge_factor=0.0):
        self.pos = pygame.Vector2(pos)
        self.dir = pygame.Vector2(direction)
        if self.dir.length_squared() == 0:
            self.dir = pygame.Vector2(1, 0)
        else:
            self.dir = self.dir.normalize()
        self.arc = arc
        self.radius = radius
        self.time_left = duration
        self.duration = duration
        self.charge = charge_factor

    def update(self, dt):
        self.time_left -= dt

    def is_done(self):
        return self.time_left <= 0

    def draw(self, surface, camera):
        if self.time_left <= 0:
            return
        screen_pos = camera.world_to_screen(self.pos, surface.get_size())
        size = int(self.radius * 2)
        arc_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = pygame.Vector2(self.radius, self.radius)
        start_angle = math.atan2(self.dir.y, self.dir.x) - self.arc / 2
        steps = 20
        points = [center]
        for i in range(steps + 1):
            ang = start_angle + self.arc * i / steps
            p = center + pygame.Vector2(math.cos(ang), math.sin(ang)) * self.radius
            points.append(p)
        alpha = max(0, int(180 * (1 + self.charge) * (self.time_left / self.duration)))
        if alpha > 255:
            alpha = 255
        color = (255, 255, 255, alpha)
        pygame.draw.polygon(arc_surface, color, points)
        surface.blit(arc_surface, (screen_pos.x - self.radius, screen_pos.y - self.radius))


class CircleSlashEffect:
    def __init__(self, pos, radius, duration=0.3, charge_factor=0.0):
        self.pos = pygame.Vector2(pos)
        self.radius = radius
        self.time_left = duration
        self.duration = duration
        self.charge = charge_factor

    def update(self, dt):
        self.time_left -= dt

    def is_done(self):
        return self.time_left <= 0

    def draw(self, surface, camera):
        if self.time_left <= 0:
            return
        screen_pos = camera.world_to_screen(self.pos, surface.get_size())
        size = int(self.radius * 2)
        circle_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        alpha = max(0, int(150 * (1 + self.charge) * (self.time_left / self.duration)))
        if alpha > 255:
            alpha = 255
        color = (255, 255, 255, alpha)
        center = (int(self.radius), int(self.radius))
        pygame.draw.circle(circle_surface, color, center, int(self.radius))
        surface.blit(circle_surface, (screen_pos.x - self.radius, screen_pos.y - self.radius))
