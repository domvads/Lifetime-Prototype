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

