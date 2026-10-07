import pygame


class Player:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.width = 44
        self.height = 54
        self.speed = 7

        self.x = (screen_width // 2) - (self.width // 2)
        self.y = screen_height - self.height - 20

    def move_left(self):
        self.x -= self.speed

    def move_right(self):
        self.x += self.speed

    def update(self):
        # Task 1: Fix boundary bug
        if self.x < 0:
            self.x = 0

        if self.x > self.screen_width - self.width:
            self.x = self.screen_width - self.width

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def render(self, surface):
        torso_rect = pygame.Rect(int(self.x) + 6, int(self.y) + 18, 32, 36)
        pygame.draw.rect(surface, (50, 130, 220), torso_rect, border_radius=4)

        pygame.draw.circle(
            surface,
            (230, 200, 160),
            (int(self.x) + 22, int(self.y) + 12),
            12,
        )

        helmet_rect = pygame.Rect(int(self.x) + 8, int(self.y) - 2, 28, 12)
        pygame.draw.rect(surface, (180, 180, 190), helmet_rect, border_radius=4)