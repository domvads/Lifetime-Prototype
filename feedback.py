import math
import random
import pygame

class Hitstop:
    def __init__(self, max_time=0.18):
        self.max_time = max_time
        self.time_left = 0.0
        self.enabled = True

    def add(self, duration: float):
        if not self.enabled:
            return
        self.time_left = min(self.time_left + duration, self.max_time)

    def update(self, dt: float):
        self.time_left = max(0.0, self.time_left - dt)

    def active(self) -> bool:
        return self.time_left > 0.0

class ScreenShake:
    def __init__(self, max_amplitude=30.0):
        self.max_amplitude = max_amplitude
        self.time_left = 0.0
        self.duration = 0.0
        self.amplitude = 0.0
        self.offset = pygame.Vector2(0, 0)
        self.current_amplitude = 0.0
        self.enabled = True

    def add(self, amplitude: float, duration: float):
        if not self.enabled:
            return
        self.amplitude = min(self.amplitude + amplitude, self.max_amplitude)
        self.duration = max(self.duration, duration)
        self.time_left = self.duration

    def update(self, dt: float):
        if self.time_left > 0:
            self.time_left = max(0.0, self.time_left - dt)
            if self.duration > 0:
                decay = self.time_left / self.duration
            else:
                decay = 0.0
            self.current_amplitude = self.amplitude * decay
            angle = random.uniform(0, 2 * math.pi)
            self.offset.x = math.cos(angle) * self.current_amplitude
            self.offset.y = math.sin(angle) * self.current_amplitude
        else:
            self.offset.update(0, 0)
            self.current_amplitude = 0.0
