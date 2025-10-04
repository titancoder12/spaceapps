import pygame

class CelestialBody:
    def __init__(self, x, y, vx, vy, mass, radius, color, nasa_data = None):
        # Position, velocity, mass, visual radius, and color
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.mass = mass
        self.radius = radius
        self.color = color
        # Store past positions for drawing an orbit trail
        self.orbit = []
        self.nasa_data = nasa_data  # Store original NASA data if provided

    def draw(self, screen):
        # Draw the orbit trail as a line (if enough points)
        if len(self.orbit) > 1:
            # Convert orbit points to integers for pygame.draw
            points = [(int(px), int(py)) for px, py in self.orbit]
            pygame.draw.lines(screen, self.color, False, points, 1)
        # Draw the body as a filled circle
        pygame.draw.circle(screen, self.color,
                           (int(self.x), int(self.y)), self.radius)