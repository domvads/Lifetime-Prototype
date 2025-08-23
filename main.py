import math
import pygame

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
        self.speed = 500

    def update(self, dt, keys):
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

    def draw(self, surface, camera):
        screen_pos = camera.world_to_screen(self.pos, surface.get_size())
        pygame.draw.circle(
            surface, self.color, (int(screen_pos.x), int(screen_pos.y)), self.radius
        )


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
            elif event.type == pygame.VIDEORESIZE and not self.fullscreen:
                self.window_size = [event.w, event.h]
                self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
            elif event.type == pygame.MOUSEWHEEL:
                self.handle_zoom(event.y)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.player.update(dt, keys)
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
        text = (
            f"Player: ({self.player.pos.x:.1f}, {self.player.pos.y:.1f})  "
            f"Zoom: {self.camera.zoom:.2f}  FPS: {self.clock.get_fps():.1f}"
        )
        surface = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(surface, (10, 10))

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.draw_grid()
        self.player.draw(self.screen, self.camera)
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
