import random
import pygame


class Anvil:
    def __init__(self, screen_width, difficulty=1):
        self.screen_width = screen_width

        self.width = 40
        self.height = 32

        self.x = random.randint(20, screen_width - self.width - 20)
        self.y = -self.height

        # Task 2: Dynamic difficulty
        self.speed = random.uniform(
            4.5 + difficulty * 0.3,
            7.0 + difficulty * 0.5
        )

    def update(self):
        self.y += self.speed

    def is_off_screen(self, screen_height):
        return self.y > screen_height + 10

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x),
            int(self.y),
            self.width,
            self.height
        )

    # Task 3: Speed-based colors
    def get_color(self):
        if self.speed < 6:
            return (120, 120, 130)

        elif self.speed < 8:
            return (255, 180, 0)

        elif self.speed < 10:
            return (255, 90, 0)

        return (255, 40, 40)

    def render(self, surface):
        color = self.get_color()

        top_rect = pygame.Rect(
            int(self.x) + 4,
            int(self.y),
            self.width - 8,
            14
        )

        pygame.draw.rect(
            surface,
            color,
            top_rect,
            border_radius=2
        )

        base_rect = pygame.Rect(
            int(self.x),
            int(self.y) + 14,
            self.width,
            18
        )

        dark_color = (
            max(color[0] - 40, 0),
            max(color[1] - 40, 0),
            max(color[2] - 40, 0)
        )

        pygame.draw.rect(
            surface,
            dark_color,
            base_rect,
            border_radius=3
        )

        pygame.draw.rect(
            surface,
            (220, 220, 220),
            base_rect,
            width=1,
            border_radius=3
        )