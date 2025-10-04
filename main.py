import pygame
import random
import math
import physics
from entities import CelestialBody

# Screen dimensions
WIDTH, HEIGHT = 700, 700

# Game settings
MAX_SPEED = 3
NUM_ANTS = 5
STOMP_RADIUS = 30

def main():
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Asteroid Gravity Game")

    clock = pygame.time.Clock()

    # Create Earth (target) at center of screen
    earth = CelestialBody(400, 300, vx=0, vy=0,
                          mass=10000, radius=20, color=(0, 100, 255))

    # List to hold all asteroids
    asteroids = []
    # Launch parameters: initial position and aim (angle/speed)
    launch_pos = (400, 580)       # bottom center
    angle = math.pi/2             # straight up
    speed = 5.0                   # initial launch speed

    running = True
    while running:
        clock.tick(60)  # Cap the frame rate

        # --- Handle events (input) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # Adjust launch angle/speed with arrow keys
                if event.key == pygame.K_LEFT:
                    angle += math.radians(5)
                if event.key == pygame.K_RIGHT:
                    angle -= math.radians(5)
                if event.key == pygame.K_UP:
                    speed += 1
                if event.key == pygame.K_DOWN:
                    speed = max(1, speed - 1)
                # Fire an asteroid
                if event.key == pygame.K_SPACE:
                    vx = speed * math.cos(angle)
                    vy = -speed * math.sin(angle)
                    asteroid = CelestialBody(launch_pos[0], launch_pos[1],
                                             vx=vx, vy=vy,
                                             mass=1, radius=5, color=(200, 200, 200))
                    asteroids.append(asteroid)

        # --- Physics Update ---
        # Combine Earth and all asteroids into one list for gravity
        bodies = [earth] + asteroids
        # Advance physics by one time unit
        physics.update_bodies(bodies, dt=1)

        # --- Collision and Escape Handling ---
        # Check for asteroid-Earth collisions
        for asteroid in asteroids[:]:
            dx = asteroid.x - earth.x
            dy = asteroid.y - earth.y
            dist = math.hypot(dx, dy)
            if dist < earth.radius + asteroid.radius:
                asteroids.remove(asteroid)
                # (Optional: trigger impact animation here)

        # Remove asteroids that have escaped off-screen
        asteroids = [ast for ast in asteroids if 0 <= ast.x <= width and 0 <= ast.y <= height]

        # --- Drawing ---
        screen.fill((0, 0, 0))
        earth.draw(screen)
        for asteroid in asteroids:
            asteroid.draw(screen)
        # Draw UI text for angle and speed
        font = pygame.font.SysFont(None, 24)
        info_text = f"Angle: {math.degrees(angle):.0f}°, Speed: {speed}"
        text_surf = font.render(info_text, True, (255, 255, 255))
        screen.blit(text_surf, (10, 10))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
