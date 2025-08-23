import math
import random
import pygame

from input_handler import InputHandler
from weapons import ChargeAttack, MeleeWeapon, RangedWeapon
from enemies import Enemy
from effects import SlashEffect, CircleSlashEffect

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
CELL_SIZE = 200
BG_COLOR = (23, 26, 32)
GRID_COLOR = (58, 63, 75)
AXIS_COLOR_X = (255, 0, 0)  # x-axis (y=0)
AXIS_COLOR_Y = (0, 255, 0)  # y-axis (x=0)
ORIGIN_COLOR = (255, 255, 255)
MIN_ZOOM = 0.25
MAX_ZOOM = 4.0
ZOOM_STEP = 1.1

PLAYER_SPEED = 500
PLAYER_MAX_HP = 100
DASH_SPEED = 1600
DASH_TIME = 0.25
DASH_COOLDOWN = 1.0
DASH_IFRAMES = 0.18

ENEMY_SPAWN_INTERVAL = 2.5


class Camera:
    def __init__(self, pos=(0, 0), zoom=1.0):
        self.pos = pygame.Vector2(pos)
        self.zoom = zoom

    def center_on(self, target):
        self.pos.update(target)

    def world_to_screen(self, world_pos, screen_size):
        center = pygame.Vector2(screen_size) / 2
        return (pygame.Vector2(world_pos) - self.pos) * self.zoom + center

    def screen_to_world(self, screen_pos, screen_size):
        center = pygame.Vector2(screen_size) / 2
        return (pygame.Vector2(screen_pos) - center) / self.zoom + self.pos


class Player:
    def __init__(self, pos=(0, 0), radius=20, color=(0, 0, 255)):
        self.pos = pygame.Vector2(pos)
        self.radius = radius
        self.color = color
        self.speed = PLAYER_SPEED
        self.hp = PLAYER_MAX_HP
        self.dash_time_left = 0
        self.dash_cooldown_left = 0
        self.iframes_left = 0
        self.dash_dir = pygame.Vector2(1, 0)
        self.last_move_dir = pygame.Vector2(1, 0)

    def update(self, dt, keys):
        self.dash_cooldown_left = max(0, self.dash_cooldown_left - dt)
        self.iframes_left = max(0, self.iframes_left - dt)

        if self.dash_time_left > 0:
            self.pos += self.dash_dir * DASH_SPEED * dt
            self.dash_time_left -= dt
            if self.dash_time_left <= 0:
                self.dash_time_left = 0
                self.dash_cooldown_left = DASH_COOLDOWN
        else:
            vel = pygame.Vector2(0, 0)
            if keys[pygame.K_w]:
                vel.y -= 1
            if keys[pygame.K_s]:
                vel.y += 1
            if keys[pygame.K_a]:
                vel.x -= 1
            if keys[pygame.K_d]:
                vel.x += 1
            if vel.length_squared() > 0:
                vel = vel.normalize()
                self.pos += vel * self.speed * dt
                self.last_move_dir = vel

    def draw(self, surface, camera):
        screen_pos = camera.world_to_screen(self.pos, surface.get_size())
        color = self.color if self.iframes_left <= 0 else (100, 100, 255)
        pygame.draw.circle(surface, color, (int(screen_pos.x), int(screen_pos.y)), self.radius)

    def take_damage(self, dmg):
        if self.iframes_left > 0 or self.dash_time_left > 0:
            return
        self.hp = max(0, self.hp - dmg)

    def try_dash(self):
        if self.dash_cooldown_left > 0 or self.dash_time_left > 0:
            return False
        keys = pygame.key.get_pressed()
        move_dir = pygame.Vector2(0, 0)
        if keys[pygame.K_w]:
            move_dir.y -= 1
        if keys[pygame.K_s]:
            move_dir.y += 1
        if keys[pygame.K_a]:
            move_dir.x -= 1
        if keys[pygame.K_d]:
            move_dir.x += 1
        if move_dir.length_squared() == 0:
            move_dir = self.last_move_dir
        if move_dir.length_squared() == 0:
            move_dir = pygame.Vector2(1, 0)
        self.dash_dir = move_dir.normalize()
        self.dash_time_left = DASH_TIME
        self.iframes_left = DASH_IFRAMES
        return True

    def is_dashing(self):
        return self.dash_time_left > 0


class Game:
    def __init__(self):
        pygame.init()
        self.window_size = [WINDOW_WIDTH, WINDOW_HEIGHT]
        self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
        pygame.display.set_caption("Top-Down Grid Prototype")

        self.clock = pygame.time.Clock()
        self.camera = Camera()
        self.player = Player()

        self.running = True
        self.fullscreen = False
        self.last_window_size = self.window_size[:]

        self.font = pygame.font.SysFont("consolas", 16)

        self.input = InputHandler()
        self.projectiles = []
        self.enemies = []
        self.slashes = []
        self.spawn_timer = ENEMY_SPAWN_INTERVAL
        self.total_spawned = 0
        self.elapsed_time = 0
        self.melee = MeleeWeapon(self.player, ChargeAttack(1.0))
        self.ranged = RangedWeapon(self.player, ChargeAttack(1.0))

    def toggle_fullscreen(self):
        if self.fullscreen:
            self.screen = pygame.display.set_mode(self.last_window_size, pygame.RESIZABLE)
            self.fullscreen = False
        else:
            self.last_window_size = self.screen.get_size()
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.SCALED)
            self.fullscreen = True

    def handle_zoom(self, direction):
        if direction > 0:
            self.camera.zoom = min(self.camera.zoom * ZOOM_STEP, MAX_ZOOM)
        else:
            self.camera.zoom = max(self.camera.zoom / ZOOM_STEP, MIN_ZOOM)
        self.camera.center_on(self.player.pos)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_F11 or (
                    event.key == pygame.K_RETURN and event.mod & pygame.KMOD_ALT
                ):
                    self.toggle_fullscreen()
                elif event.key == pygame.K_SPACE:
                    if self.player.try_dash():
                        self.input.cancel_all()
            elif event.type == pygame.VIDEORESIZE and not self.fullscreen:
                self.window_size = [event.w, event.h]
                self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
            elif event.type == pygame.MOUSEWHEEL:
                self.handle_zoom(event.y)
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                if not self.player.is_dashing():
                    self.input.handle_event(event)

    def spawn_enemy(self):
        angle = random.uniform(0, 2 * math.pi)
        distance = 600
        pos = self.player.pos + pygame.Vector2(math.cos(angle), math.sin(angle)) * distance
        self.enemies.append(Enemy(pos))

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.player.update(dt, keys)
        self.input.update(dt)
        self.ranged.update(dt)

        self.elapsed_time += dt
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_enemy()
            self.spawn_timer = ENEMY_SPAWN_INTERVAL
            self.total_spawned += 1

        mouse_world = self.camera.screen_to_world(
            pygame.mouse.get_pos(), self.screen.get_size()
        )
        aim_dir = mouse_world - self.player.pos
        if aim_dir.length_squared() == 0:
            aim_dir = self.player.last_move_dir
        else:
            aim_dir = aim_dir.normalize()

        if self.input.left.just_released and not self.player.is_dashing():
            _, attack_range, arc, charged = self.melee.attack(
                self.enemies, self.input.left.time, aim_dir
            )
            cf = 1.0 if charged else 0.0
            duration = 0.2 + 0.2 * cf
            if charged:
                self.slashes.append(
                    CircleSlashEffect(
                        self.player.pos,
                        attack_range,
                        duration,
                        cf,
                    )
                )
            else:
                self.slashes.append(
                    SlashEffect(
                        self.player.pos,
                        aim_dir,
                        arc,
                        attack_range,
                        duration,
                        cf,
                    )
                )
        if self.input.right.just_released and not self.player.is_dashing():
            self.ranged.attack(
                self.projectiles, self.input.right.time, aim_dir
            )

        self.input.clear_transitions()

        for projectile in list(self.projectiles):
            projectile.update(dt, self.enemies)
            if not projectile.alive:
                self.projectiles.remove(projectile)

        for enemy in list(self.enemies):
            enemy.update(dt, self.player)
            if enemy.is_dead():
                self.enemies.remove(enemy)

        for slash in list(self.slashes):
            slash.update(dt)
            if slash.is_done():
                self.slashes.remove(slash)

        if self.player.hp <= 0:
            self.running = False

        self.camera.center_on(self.player.pos)

    def draw_grid(self):
        width, height = self.screen.get_size()
        top_left = self.camera.screen_to_world((0, 0), (width, height))
        bottom_right = self.camera.screen_to_world((width, height), (width, height))

        start_x = math.floor(top_left.x / CELL_SIZE) * CELL_SIZE
        end_x = math.ceil(bottom_right.x / CELL_SIZE) * CELL_SIZE
        start_y = math.floor(top_left.y / CELL_SIZE) * CELL_SIZE
        end_y = math.ceil(bottom_right.y / CELL_SIZE) * CELL_SIZE

        for x in range(start_x, end_x + 1, CELL_SIZE):
            screen_x = int(round(self.camera.world_to_screen((x, 0), (width, height)).x))
            color = AXIS_COLOR_Y if x == 0 else GRID_COLOR
            pygame.draw.line(self.screen, color, (screen_x, 0), (screen_x, height), 1)

        for y in range(start_y, end_y + 1, CELL_SIZE):
            screen_y = int(round(self.camera.world_to_screen((0, y), (width, height)).y))
            color = AXIS_COLOR_X if y == 0 else GRID_COLOR
            pygame.draw.line(self.screen, color, (0, screen_y), (width, screen_y), 1)

        origin_screen = self.camera.world_to_screen((0, 0), (width, height))
        ox, oy = int(round(origin_screen.x)), int(round(origin_screen.y))
        pygame.draw.line(self.screen, ORIGIN_COLOR, (ox - 5, oy), (ox + 5, oy), 1)
        pygame.draw.line(self.screen, ORIGIN_COLOR, (ox, oy - 5), (ox, oy + 5), 1)

    def draw_overlay(self):
        melee_radius = self.melee.base_range
        text = (
            f"Radius: {melee_radius:.0f}  "
            f"Enemies: {len(self.enemies)}  "
            f"FPS: {self.clock.get_fps():.0f}"
        )
        blink_info = "  ".join(
            f"E{i}:{e.blink_time_left*1000:.0f}ms" for i, e in enumerate(self.enemies)
        )
        if blink_info:
            text += "  " + blink_info
        surface = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(surface, (10, 10))

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.draw_grid()
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera)
        for projectile in self.projectiles:
            projectile.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)
        for slash in self.slashes:
            slash.draw(self.screen, self.camera)
        self.draw_overlay()
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(144) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()


if __name__ == "__main__":
    Game().run()
