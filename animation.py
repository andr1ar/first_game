import pygame

def ease_out(t):
    return 1 - (1 - t) ** 3

class Animation:
    def __init__(self, start, end, duration, easing=ease_out):
        self.start = start
        self.end = end
        self.duration = duration
        self.easing= easing
        self.elapsed = 0.0
    def update(self, dt):
        self.elapsed = min(self.elapsed + dt, self.duration)

    @property
    def progress(self):
        return self.elapsed / self.duration

    @property
    def value(self):
        return self.start + (self.end - self.start) * self.easing(self.progress)

    @property
    def finished(self):
        return self.elapsed >= self.duration

class popeffect:
    def __init__(self, row, col, cell, color, duration=0.3):
        self.row = row
        self.col = col
        self.cell =  cell
        self.color = color
        self.duration = duration
        self.anim = Animation(1.0, 0.0, duration)
    def update(self, dt):
        self.anim.update(dt)

    @property
    def finished(self):
        return self.anim.finished

    def draw(self, screen):
        scale = self.anim.value
        full = self.cell - 2
        size = max(1, int(full * scale))
        offset = (full - size) // 2
        x = self.col *self.cell + 1 + offset
        y = self.row * self.cell + 1 + offset

        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        surf.fill((*self.color, int(255 * scale)))
        screen.blit(surf, (x, y))
