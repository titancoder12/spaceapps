import pygame
import random
import math
import physics
from entities import CelestialBody
from nasa_data import get_asteroid as load_nasa_data
import json
from screens import earth_collision
from config import M_PER_PX, SECONDS_PER_TICK, DEFAULT_DIAMETER_M, DEFAULT_DENSITY, \
                   DEFAULT_IMPACTOR_MASS, DEFAULT_IMPACTOR_SPEED, DEFAULT_BETA
from models.impact_effects import effects, mass_from_diam, kinetic_energy_j
from models.deflection import delta_v_kinetic, add_delta_v
from ui.overlays import draw_effects, info_lines
# (optional)
try:
    from data.neows import sample_neo
except Exception:
    sample_neo = None
from orbits import spawn_circular_orbit
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
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Asteroid Gravity Game")

    clock = pygame.time.Clock()

    # Create Earth (target) at center of screen
    earth = CelestialBody(400, 300, vx=0, vy=0,
                          mass=10000, radius=20, color=(0, 100, 255))

    # Tunable moon parameters (pixels and masses are in your game-units)
    MOON_DISTANCE_PX = 120          # distance from Earth center (try 100–160)
    MOON_MASS        = 100          # much smaller than Earth so Earth barely moves
    MOON_RADIUS_PX   = 8            # for visuals only

    moon = spawn_circular_orbit(
        anchor=earth,
        r_px=MOON_DISTANCE_PX,
        orbiter_mass=MOON_MASS,
        orbiter_radius_px=MOON_RADIUS_PX,
        color=(180, 180, 255),      # pale blue-gray
        G=0.1,                      # must match physics.G
        clockwise=True
    )

    # Keep a list of permanent bodies (Earth + Moon)
    primaries = [earth, moon]
    # List to hold all asteroids
    asteroids = []
    # Launch parameters: initial position and aim (angle/speed)
    launch_pos = (400, 580)       # bottom center
    angle = math.pi/2             # straight up
    speed = 5.0                   # initial launch speed

    # Launcher (cannon) state
    launcher_x, launcher_y = 400, 580         # start near bottom-center
    launcher_speed = 6                         # pixels per tick (tweak)
    angle = math.pi/2                          # you already have this
    speed = 5.0                                # you already have this
    use_mouse_aim = True                       # optional: aim toward mouse


    is_earth_collision = False
    running = True
    updated_asteroid_speed = 0

    # Active scenario (editable later via UI)
    scenario = {
        "diameter_m": DEFAULT_DIAMETER_M,
        "density": DEFAULT_DENSITY,
        "angle_deg": 90.0,
    }

    # Last computed effects (drawn every frame if present)
    last_effects = None
    effects_expire_ms = 0

    next_asteroid =  random.choice(nasa_asteroids)

    while running:
        clock.tick(60)  # Cap the frame rate

        # --- Handle events (input) ---
        for event in pygame.event.get():
            dx = dy = 0
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # Adjust launch angle/speed with arrow keys
                if event.key == pygame.K_a:
                    angle += math.radians(5)
                if event.key == pygame.K_d:
                    angle -= math.radians(5)
                if event.key == pygame.K_LEFT:
                    dx-=1
                if event.key == pygame.K_RIGHT:
                    dx+=1
                if event.key == pygame.K_UP:
                    dy-=1
                if event.key == pygame.K_DOWN:
                    dy+=1
                if dx or dy:
                    inv = 1.0 / math.hypot(dx, dy) if dx or dy else 0.0
                    launcher_x += int(launcher_speed * dx * inv)
                    launcher_y += int(launcher_speed * dy * inv)
                # Keep launcher on-screen
                launcher_x = max(0, min(width, launcher_x))
                launcher_y = max(0, min(height, launcher_y))
                if event.key == pygame.K_SPACE:
                    #asteroid = make_asteroid(launch_pos, angle, random.choice(nasa_asteroids))
                    asteroid = make_asteroid([launcher_x, launcher_y], angle, next_asteroid)
                    next_asteroid =  random.choice(nasa_asteroids)
                    print(json.dumps(next_asteroid, indent=4))
                    # attach physical params for consequence + deflection math
                    asteroid.diameter_m = scenario["diameter_m"]
                    asteroid.density = scenario["density"]
                    asteroids.append(asteroid)
                    print(f"Launched {asteroid.nasa_data['name']}...")
                    last_effects = None
                    effects_expire_ms = 0

                if event.key == pygame.K_d and asteroids:
                    target = asteroids[-1]  # last fired
                    print(f"Deflecting {target.nasa_data['name']}...")
                    # asteroid physical mass (from diameter & density)
                    d = getattr(target, "diameter_m", DEFAULT_DIAMETER_M)
                    rho = getattr(target, "density", DEFAULT_DENSITY)
                    m_ast = mass_from_diam(d, rho)

                    dv = delta_v_kinetic(
                        m_impactor=DEFAULT_IMPACTOR_MASS,
                        v_impactor_mps=DEFAULT_IMPACTOR_SPEED,
                        m_asteroid=m_ast,
                        beta=DEFAULT_BETA
                    )

                    # choose a direction: perpendicular to current velocity to maximize miss distance
                    dir_rad = math.atan2(target.vy, target.vx) + math.pi/2
                    # convert dv (m/s) to px/tick
                    dv_px_per_tick = dv / (M_PER_PX / SECONDS_PER_TICK)
                    target.vx, target.vy = add_delta_v(target.vx, target.vy, dv_px_per_tick, dir_rad)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_n and sample_neo:
                neo = sample_neo()
                scenario["diameter_m"] = neo["diameter_m"]
                scenario["density"] = neo["density_kgm3"]
                scenario["angle_deg"] = neo["angle_deg"]
                # also set your 'speed' (in px/tick) roughly from m/s:
                speed = (neo["speed_mps"] * SECONDS_PER_TICK) / M_PER_PX
    

        # --- Physics Update ---
        # Combine Earth and all asteroids into one list for gravity
        #bodies = [earth] + asteroids
        bodies = primaries + asteroids
        # Advance physics by one time unit
        physics.update_bodies(bodies, dt=1)

        # --- Collision and Escape Handling ---
        # Check for asteroid-Earth collisions
        # --- Collision and Escape Handling ---
        for asteroid in asteroids[:]:
            dx = asteroid.x - earth.x
            dy = asteroid.y - earth.y
            dist = math.hypot(dx, dy)
            if dist < earth.radius + asteroid.radius:
                # Convert game velocity (px/tick) -> m/s
                v_px_per_tick = math.hypot(asteroid.vx, asteroid.vy)
                v_mps = (v_px_per_tick * M_PER_PX) / SECONDS_PER_TICK

                # Compute consequences
                last_effects = effects(
                    diameter_m=getattr(asteroid, "diameter_m", DEFAULT_DIAMETER_M),
                    density=getattr(asteroid, "density", DEFAULT_DENSITY),
                    v_mps=v_mps,
                    angle_deg=scenario["angle_deg"]
                )
                effects_expire_ms = pygame.time.get_ticks() + 2500  # show for 2.5s

                asteroids.remove(asteroid)
                # (Optional: trigger an explosion anim here)
                continue
            
            # asteroid–Moon
            dxm = asteroid.x - moon.x
            dym = asteroid.y - moon.y
            if (dxm*dxm + dym*dym) ** 0.5 < moon.radius + asteroid.radius:
                # Option A: treat as a hit and remove it
                # Option B (fun): ricochet or fragment. For now, remove.
                asteroids.remove(asteroid)
                # (Optional) Start a small impact animation on the Moon here.
                continue
            


        # Remove asteroids that have escaped off-screen
        asteroids = [ast for ast in asteroids if 0 <= ast.x <= width and 0 <= ast.y <= height]

        # --- Drawing ---
        # --- Drawing ---
        screen.fill((0, 0, 0))
        #earth.draw(screen)
        for body in primaries:
            body.draw(screen)
        for asteroid in asteroids:
            asteroid.draw(screen)

        # Draw UI text for angle and speed (existing)
        font = pygame.font.SysFont(None, 24)
        next_astroid_name = next_asteroid['name']
        info_text = f"Angle: {math.degrees(angle):.0f}°"
        screen.blit(font.render(info_text, True, (255, 255, 255)), (10, 50))
        screen.blit(font.render("Next Asteroid: "+next_astroid_name, True, (255, 255, 255)), (10, 10))
#
        # NEW: if we have last_effects, draw them centered on Earth
        now = pygame.time.get_ticks()
        if last_effects and now < effects_expire_ms:
            draw_effects(screen, (earth.x, earth.y), last_effects)
            # side info
            y = 34
            for line in info_lines(last_effects):
                screen.blit(font.render(line, True, (200, 220, 255)), (10, y)); y += 18
        else:
            last_effects = None
        pygame.display.flip()

        # Draw UI text for angle and speed
        #font = pygame.font.SysFont(None, 24)
        #info_text = f"Angle: {math.degrees(angle):.0f}°"
        #text_surf = font.render(info_text, True, (255, 255, 255))
        #screen.blit(text_surf, (10, 10))

        if is_earth_collision:
            #earth_collision(screen, asteroid.mass * 1000, updated_asteroid_speed)
            #pygame.display.flip()
            #pygame.time.delay(2000)
            #is_earth_collision = False
            pass

        updated_asteroid_speed = 0
        if asteroids:
            # Get speed in m/s (convert from pixels/frame to km/h, then to m/s)
            last_asteroid = asteroids[-1]
            # First, get the NASA km/h value if available
            ca_list = last_asteroid.nasa_data.get('close_approach_data', [])
            if ca_list:
                try:
                    speed_kmh = float(ca_list[0]['relative_velocity']['kilometers_per_hour'])
                except (KeyError, ValueError, TypeError):
                    speed_kmh = 0
                else:
                    updated_asteroid_speed = speed_kmh * 1000 / 3600  # km/h to m/s
            else:
                speed_kmh = 0
                updated_asteroid_speed = speed_kmh * 1000 / 3600  # km/h to m/s
            asteroid_info = f"Asteroid name: {last_asteroid.nasa_data['name']}"
            asteroid_info_surf = font.render(asteroid_info, True, (255, 255, 255))
            # Place asteroid info on the right side of the screen
            text_width = asteroid_info_surf.get_width()
            screen.blit(asteroid_info_surf, (width - text_width - 10, 100))

            asteroid_speed = asteroids[-1].nasa_data.get('close_approach_data', [])
            if asteroid_speed:
                
                speed_info = f"Speed (km/h): {round(float(asteroid_speed[0]['relative_velocity']['kilometers_per_hour']), 2)}"
                speed_info_surf = font.render(speed_info, True, (255, 255, 255))
                # Place below asteroid name, aligned right
                screen.blit(speed_info_surf, (width - speed_info_surf.get_width() - 10, 100 + asteroid_info_surf.get_height() + 5))

        # --- Draw launcher ---
        # base
        pygame.draw.circle(screen, (180,180,180), (int(launcher_x), int(launcher_y)), 8)

        # barrel line
        barrel_len = 40
        tip_x = int(launcher_x + barrel_len * math.cos(angle))
        tip_y = int(launcher_y - barrel_len * math.sin(angle))
        pygame.draw.line(screen, (255,255,255), (int(launcher_x), int(launcher_y)), (tip_x, tip_y), 2)


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
        mass=2,
        radius=5,
        color=(200, 200, 200),
        nasa_data=nasa_asteroid_data  # keep raw NASA dict
    )





if __name__ == "__main__":
    main()
