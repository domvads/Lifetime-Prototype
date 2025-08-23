import pygame


class ButtonState:
    """Track press/hold/release timing for a single button."""
    def __init__(self):
        self.is_down = False
        self.time = 0.0
        self.just_pressed = False
        self.just_released = False

    def press(self):
        if not self.is_down:
            self.is_down = True
            self.time = 0.0
            self.just_pressed = True

    def release(self):
        if self.is_down:
            self.is_down = False
            self.just_released = True

    def update(self, dt: float):
        if self.is_down:
            self.time += dt

    def clear_transitions(self):
        self.just_pressed = False
        self.just_released = False
        if not self.is_down:
            self.time = 0.0


class InputHandler:
    """Handles mouse button state transitions."""
    def __init__(self):
        self.left = ButtonState()
        self.right = ButtonState()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.left.press()
            elif event.button == 3:
                self.right.press()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.left.release()
            elif event.button == 3:
                self.right.release()

    def update(self, dt: float):
        self.left.update(dt)
        self.right.update(dt)

    def clear_transitions(self):
        self.left.clear_transitions()
        self.right.clear_transitions()
