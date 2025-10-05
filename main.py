import math
import json
import random
import pygame

import physics
from entities import CelestialBody
from data.nasa_data import get_asteroid as load_nasa_data
from screens import earth_collision  # (currently unused but kept for future)
from config import (
    M_PER_PX,
    SECONDS_PER_TICK,
    DEFAULT_DIAMETER_M,
    DEFAULT_DENSITY,
    DEFAULT_IMPACTOR_MASS,
    DEFAULT_IMPACTOR_SPEED,
    DEFAULT_BETA,
)
from models.impact_effects import effects, mass_from_diam
from models.deflection import delta_v_kinetic, add_delta_v
from ui.overlays import draw_effects, info_lines

# (optional)
try:
    from data.neows import sample_neo
except Exception:
    sample_neo = None

from orbits import spawn_circular_orbit

# =============================================================================
# Constants / Config
# =============================================================================

# Window
WIDTH, HEIGHT = 800, 600
FPS = 60

# Controls
KEY_TURN_LEFT = pygame.K_a
KEY_TURN_RIGHT = pygame.K_d
KEY_MOVE_LEFT = pygame.K_LEFT
KEY_MOVE_RIGHT = pygame.K_RIGHT
KEY_MOVE_UP = pygame.K_UP
KEY_MOVE_DOWN = pygame.K_DOWN
KEY_LAUNCH = pygame.K_SPACE
KEY_DEFLECT = pygame.K_f          # moved from K_d to avoid conflict with aiming
KEY_LOAD_RANDOM_NEO = pygame.K_n  # only active if sample_neo is available

# Launcher
LAUNCHER_INIT_X, LAUNCHER_INIT_Y = 400, 580
LAUNCHER_SPEED = 6               # px per frame
BARREL_LENGTH = 40

# World / Primary bodies
EARTH_POS = (400, 300)
EARTH_MASS = 10000
EARTH_RADIUS = 20
EARTH_COLOR = (0, 100, 255)

MOON_DISTANCE_PX = 120
MOON_MASS = 100
MOON_RADIUS_PX = 8
MOON_COLOR = (180, 180, 255)
PHYS_G = 0.1                     # must match physics.G in your engine

# Asteroid gameplay scaling
KMH_TO_PPF = 0.00003             # real km/h -> pixels per frame (tunable)

# HUD
HUD_MARGIN = 10
HUD_LINE_HEIGHT = 18
HUD_COLOR = (255, 255, 255)
HUD_ALT_COLOR = (200, 220, 255)

# Effects overlay
EFFECTS_DURATION_MS = 2500


# =============================================================================
# Helpers
# =============================================================================

def render_text(surface: pygame.Surface, text: str, pos: tuple[int, int], font: pygame.font.Font,
                color: tuple[int, int, int] = HUD_COLOR, antialias: bool = True) -> None:
    """Blit a single line of text at pos."""
    surface.blit(font.render(text, antialias, color), pos)


def make_asteroid(launch_pos, angle_rad, nasa_asteroid_data) -> CelestialBody:
    """
    Create an asteroid CelestialBody from NASA data.
    Converts NASA km/h to your game's px/frame via KMH_TO_PPF.
    """
    ca_list = nasa_asteroid_data.get('close_approach_data', [])
    if not ca_list:
        speed_kmh = 20000.0  # fallback km/h
    else:
        rel_vel = ca_list[0].get('relative_velocity', {})
        try:
            speed_kmh = float(rel_vel.get('kilometers_per_hour', 20000.0))
        except (TypeError, ValueError):
            speed_kmh = 20000.0

    speed_ppf = speed_kmh * KMH_TO_PPF
    print(f"{nasa_asteroid_data['name']} is moving at {speed_ppf:.4f} px/frame")

    vx = speed_ppf * math.cos(angle_rad)
    vy = -speed_ppf * math.sin(angle_rad)

    return CelestialBody(
        x=launch_pos[0],
        y=launch_pos[1],
        vx=vx,
        vy=vy,
        mass=2,
        radius=5,
        color=(200, 200, 200),
        nasa_data=nasa_asteroid_data
    )


# =============================================================================
# Game
# =============================================================================

class Game:
    """
    Asteroid Gravity Game
    Controls:
      - Move launcher: Arrow keys
      - Aim: A (ccw), D (cw)
      - Launch asteroid: Space
      - Deflect last-fired asteroid: F
      - Load random NEO sample (if available): N
    """

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Asteroid Gravity Game")
        self.clock = pygame.time.Clock()

        # Fonts (create once)
        self.font_sm = pygame.font.SysFont(None, 20)
        self.font = pygame.font.SysFont(None, 24)

        # Data
        self.nasa_asteroids = load_nasa_data(live=False) # set live=True to fetch from NASA API
        self.next_asteroid = random.choice(self.nasa_asteroids)

        # Primary bodies
        self.earth = CelestialBody(
            EARTH_POS[0], EARTH_POS[1], vx=0, vy=0,
            mass=EARTH_MASS, radius=EARTH_RADIUS, color=EARTH_COLOR
        )
        self.moon = spawn_circular_orbit(
            anchor=self.earth,
            r_px=MOON_DISTANCE_PX,
            orbiter_mass=MOON_MASS,
            orbiter_radius_px=MOON_RADIUS_PX,
            color=MOON_COLOR,
            G=PHYS_G,
            clockwise=True
        )
        self.primaries: list[CelestialBody] = [self.earth, self.moon]

        # Dynamic bodies
        self.asteroids: list[CelestialBody] = []

        # Launcher state
        self.launcher_x = LAUNCHER_INIT_X
        self.launcher_y = LAUNCHER_INIT_Y
        self.launch_angle = math.pi / 2  # straight up
        self.use_mouse_aim = True        # currently unused in code path; reserved for future

        # Scenario (physical parameters for impact calculations)
        self.scenario = {
            "diameter_m": DEFAULT_DIAMETER_M,
            "density": DEFAULT_DENSITY,
            "angle_deg": 90.0,            # entry angle for effects model
        }

        # Effects HUD
        self.last_effects = None
        self.effects_expire_ms = 0

        # Running flag
        self.running = True

    # -------------------------------------------------------------------------
    # Input
    # -------------------------------------------------------------------------
    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)

    def _handle_keydown(self, key: int) -> None:
        dx = dy = 0

        # Aim
        if key == KEY_TURN_LEFT:
            self.launch_angle += math.radians(5)
        if key == KEY_TURN_RIGHT:
            self.launch_angle -= math.radians(5)

        # Move launcher
        if key == KEY_MOVE_LEFT:
            dx -= 1
        if key == KEY_MOVE_RIGHT:
            dx += 1
        if key == KEY_MOVE_UP:
            dy -= 1
        if key == KEY_MOVE_DOWN:
            dy += 1

        if dx or dy:
            inv = 1.0 / math.hypot(dx, dy) if (dx or dy) else 0.0
            self.launcher_x += int(LAUNCHER_SPEED * dx * inv)
            self.launcher_y += int(LAUNCHER_SPEED * dy * inv)
            # Keep launcher inside screen
            self.launcher_x = max(0, min(WIDTH, self.launcher_x))
            self.launcher_y = max(0, min(HEIGHT, self.launcher_y))

        # Launch
        if key == KEY_LAUNCH:
            self.launch_next_asteroid()

        # Deflect last asteroid
        if key == KEY_DEFLECT:
            self.deflect_last_asteroid()

        # Load random NEO sample
        if key == KEY_LOAD_RANDOM_NEO and sample_neo:
            neo = sample_neo()
            self.scenario["diameter_m"] = neo["diameter_m"]
            self.scenario["density"] = neo["density_kgm3"]
            self.scenario["angle_deg"] = neo["angle_deg"]
            # Optionally, adjust any in-game speed scalar if desired:
            # (neo["speed_mps"] * SECONDS_PER_TICK) / M_PER_PX  # px/tick

    # -------------------------------------------------------------------------
    # Simulation
    # -------------------------------------------------------------------------
    def update_physics(self) -> None:
        bodies = self.primaries + self.asteroids
        physics.update_bodies(bodies, dt=1)

    def handle_collisions_and_culling(self) -> None:
        # Asteroid vs Earth / Moon, Off-screen culling
        for asteroid in self.asteroids[:]:
            # Earth collision
            if self._circle_overlap(asteroid, self.earth):
                self._compute_impact_effects(asteroid)
                self.asteroids.remove(asteroid)
                continue

            # Moon collision
            if self._circle_overlap(asteroid, self.moon):
                self.asteroids.remove(asteroid)
                continue

        # Off-screen culling
        self.asteroids = [
            a for a in self.asteroids
            if 0 <= a.x <= WIDTH and 0 <= a.y <= HEIGHT
        ]

    @staticmethod
    def _circle_overlap(a: CelestialBody, b: CelestialBody) -> bool:
        dx, dy = a.x - b.x, a.y - b.y
        return (dx * dx + dy * dy) ** 0.5 < (a.radius + b.radius)

    def _compute_impact_effects(self, asteroid: CelestialBody) -> None:
        # Convert px/tick -> m/s
        v_px_per_tick = math.hypot(asteroid.vx, asteroid.vy)
        v_mps = (v_px_per_tick * M_PER_PX) / SECONDS_PER_TICK

        self.last_effects = effects(
            diameter_m=getattr(asteroid, "diameter_m", DEFAULT_DIAMETER_M),
            density=getattr(asteroid, "density", DEFAULT_DENSITY),
            v_mps=v_mps,
            angle_deg=self.scenario["angle_deg"],
        )
        self.effects_expire_ms = pygame.time.get_ticks() + EFFECTS_DURATION_MS

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def launch_next_asteroid(self) -> None:
        """Launches the preselected 'next_asteroid', then picks a new one."""
        asteroid = make_asteroid(
            (self.launcher_x, self.launcher_y),
            self.launch_angle,
            self.next_asteroid
        )
        # attach physical params for consequence + deflection math
        asteroid.diameter_m = self.scenario["diameter_m"]
        asteroid.density = self.scenario["density"]
        self.asteroids.append(asteroid)

        print(json.dumps(self.next_asteroid, indent=4))
        print(f"Launched {asteroid.nasa_data['name']}...")

        # reset effects panel until a new collision happens
        self.last_effects = None
        self.effects_expire_ms = 0

        # choose a new upcoming asteroid
        self.next_asteroid = random.choice(self.nasa_asteroids)

    def deflect_last_asteroid(self) -> None:
        """Apply a kinetic-impactor-style Δv to the most-recent asteroid."""
        if not self.asteroids:
            return

        target = self.asteroids[-1]
        print(f"Deflecting {target.nasa_data['name']}...")

        d = getattr(target, "diameter_m", DEFAULT_DIAMETER_M)
        rho = getattr(target, "density", DEFAULT_DENSITY)
        m_ast = mass_from_diam(d, rho)

        dv_mps = delta_v_kinetic(
            m_impactor=DEFAULT_IMPACTOR_MASS,
            v_impactor_mps=DEFAULT_IMPACTOR_SPEED,
            m_asteroid=m_ast,
            beta=DEFAULT_BETA,
        )

        # Apply Δv perpendicular to current velocity to maximize miss distance
        dir_rad = math.atan2(target.vy, target.vx) + math.pi / 2
        # convert dv (m/s) -> px/tick
        dv_px_per_tick = dv_mps / (M_PER_PX / SECONDS_PER_TICK)
        target.vx, target.vy = add_delta_v(target.vx, target.vy, dv_px_per_tick, dir_rad)

    # -------------------------------------------------------------------------
    # Drawing
    # -------------------------------------------------------------------------
    def draw(self) -> None:
        self.screen.fill((0, 0, 0))

        # Primaries
        for body in self.primaries:
            body.draw(self.screen)

        # Asteroids
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)

        # HUD: left side
        self._draw_hud_left()

        # HUD: right side (info for the last asteroid)
        self._draw_hud_right()

        # Effects overlay near Earth (if active)
        now = pygame.time.get_ticks()
        if self.last_effects and now < self.effects_expire_ms:
            draw_effects(self.screen, (self.earth.x, self.earth.y), self.last_effects)
            # textual side info
            y = 84
            for line in info_lines(self.last_effects):
                render_text(self.screen, line, (HUD_MARGIN, y), self.font, HUD_ALT_COLOR)
                y += HUD_LINE_HEIGHT
        else:
            self.last_effects = None  # expire

        # Launcher (base + barrel)
        self._draw_launcher()

        pygame.display.flip()

    def _draw_hud_left(self) -> None:
        y = HUD_MARGIN
        next_name = self.next_asteroid.get('name', 'Unknown')
        render_text(self.screen, f"Next Asteroid: {next_name}", (HUD_MARGIN, y), self.font)
        y += HUD_LINE_HEIGHT * 2

        angle_deg = math.degrees(self.launch_angle)
        render_text(self.screen, f"Angle: {angle_deg:.0f}°", (HUD_MARGIN, y), self.font)

    def _draw_hud_right(self) -> None:
        if not self.asteroids:
            return

        last = self.asteroids[-1]
        ca_list = last.nasa_data.get('close_approach_data', [])
        if ca_list:
            try:
                kmh = float(ca_list[0]['relative_velocity']['kilometers_per_hour'])
            except (KeyError, ValueError, TypeError):
                kmh = 0.0
        else:
            kmh = 0.0

        # Right-aligned block at ~x = WIDTH - margin
        name_text = f"Asteroid name: {last.nasa_data.get('name', 'Unknown')}"
        speed_text = f"Speed (km/h): {kmh:.2f}"

        name_surf = self.font.render(name_text, True, HUD_COLOR)
        speed_surf = self.font.render(speed_text, True, HUD_COLOR)

        x_name = WIDTH - name_surf.get_width() - HUD_MARGIN
        x_speed = WIDTH - speed_surf.get_width() - HUD_MARGIN
        y_base = 100

        self.screen.blit(name_surf, (x_name, y_base))
        self.screen.blit(speed_surf, (x_speed, y_base + name_surf.get_height() + 5))

    def _draw_launcher(self) -> None:
        # base
        pygame.draw.circle(
            self.screen, (180, 180, 180),
            (int(self.launcher_x), int(self.launcher_y)), 8
        )
        # barrel
        tip_x = int(self.launcher_x + BARREL_LENGTH * math.cos(self.launch_angle))
        tip_y = int(self.launcher_y - BARREL_LENGTH * math.sin(self.launch_angle))
        pygame.draw.line(
            self.screen, (255, 255, 255),
            (int(self.launcher_x), int(self.launcher_y)),
            (tip_x, tip_y), 2
        )

    # -------------------------------------------------------------------------
    # Main loop
    # -------------------------------------------------------------------------
    def run(self) -> None:
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update_physics()
            self.handle_collisions_and_culling()
            self.draw()

        pygame.quit()


# =============================================================================
# Entrypoint
# =============================================================================

if __name__ == "__main__":
    Game().run()
