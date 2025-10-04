import pygame
import random
import math
import physics
from entities import CelestialBody
from nasa_data import get_asteroid as load_nasa_data
import json


# Screen dimensions
WIDTH, HEIGHT = 700, 700

# Game settings
MAX_SPEED = 3
NUM_ANTS = 5
STOMP_RADIUS = 30

# Convert real km/h to “pixels per frame” (tune this value to taste)
KMH_TO_PPF = 0.00003

def main():
    nasa_asteroids = load_nasa_data()
    #print(json.dumps(nasa_asteroids, indent=4))
    #print(f"Total asteroids found: {len(nasa_asteroids)}")
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
                # if event.key == pygame.K_UP:
                #     speed += 1
                # if event.key == pygame.K_DOWN:
                #     speed = max(1, speed - 1)
                # Fire an asteroid
                if event.key == pygame.K_SPACE:
                    vx = speed * math.cos(angle)
                    vy = -speed * math.sin(angle)
                    # asteroid = CelestialBody(launch_pos[0], launch_pos[1],
                    #                          vx=vx, vy=vy,
                    #                          mass=1, radius=5, color=(200, 200, 200))
                    asteroid =make_asteroid(launch_pos, angle, random.choice(nasa_asteroids))
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
        info_text = f"Angle: {math.degrees(angle):.0f}°"
        text_surf = font.render(info_text, True, (255, 255, 255))
        screen.blit(text_surf, (10, 10))

        if asteroids:
            asteroid_info = f"Asteroid name: {asteroids[-1].nasa_data['name']}"
            asteroid_info_surf = font.render(asteroid_info, True, (255, 255, 255))
            screen.blit(asteroid_info_surf, (10, 30))

            asteroid_speed = asteroids[-1].nasa_data.get('close_approach_data', [])
            if asteroid_speed:
                speed_info = f"Speed (km/h): {round(float(asteroid_speed[0]['relative_velocity']['kilometers_per_hour']), 2)}"
                speed_info_surf = font.render(speed_info, True, (255, 255, 255))
                screen.blit(speed_info_surf, (10, 50))

        pygame.display.flip()

    pygame.quit()

def make_asteroid(launch_pos, angle, nasa_asteroid_data):
    # Close-approach data can be missing; guard it

    ca_list = nasa_asteroid_data.get('close_approach_data', [])
    if not ca_list:
        speed_kmh = 20000.0  # fallback (km/h), choose anything reasonable
    else:
        rel_vel = ca_list[0].get('relative_velocity', {})
        # NASA gives strings here -> parse to float
        try:
            speed_kmh = float(rel_vel.get('kilometers_per_hour', 20000.0))
        except (TypeError, ValueError):
            speed_kmh = 20000.0

    # Scale real-world km/h to your game’s pixels-per-frame
    speed = speed_kmh * KMH_TO_PPF
    print(f"{nasa_asteroid_data['name']} is moving at {speed} pixels/frame")

    vx = speed * math.cos(angle)
    vy = -speed * math.sin(angle)

    return CelestialBody(
        x=launch_pos[0],
        y=launch_pos[1],
        vx=vx,
        vy=vy,
        mass=1,
        radius=5,
        color=(200, 200, 200),
        nasa_data=nasa_asteroid_data  # keep raw NASA dict
    )


if __name__ == "__main__":
    main()
