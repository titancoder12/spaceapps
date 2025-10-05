# orbits.py
import math
from entities import CelestialBody

def spawn_circular_orbit(anchor, r_px, orbiter_mass, orbiter_radius_px, color, G=0.1, clockwise=True):
    """
    Create a CelestialBody 'orbiter' in a circular orbit around 'anchor'.
    Uses v = sqrt(G * M_anchor / r) with your physics G and masses.
    Positions are in pixels; velocities are in your px/tick units.
    """
    # place the moon to the right of Earth by r (you can pick any angle)
    x = anchor.x + r_px
    y = anchor.y

    # speed for circular orbit
    v = math.sqrt(G * anchor.mass / r_px)

    # direction: perpendicular to the radius vector
    # if anchored at (cx,cy) and moon at (cx+r,cy), velocity is ±y direction
    vx = 0.0
    vy = -v if clockwise else v

    moon = CelestialBody(x, y, vx, vy, mass=orbiter_mass, radius=orbiter_radius_px, color=color)
    return moon
