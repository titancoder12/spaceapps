# physics.py

import math

G = 0.1  # Gravitational constant (scaled for game)

def compute_gravitational_force(body1, body2):
    dx = body2.x - body1.x
    dy = body2.y - body1.y
    distance_sq = dx*dx + dy*dy
    # Avoid division by zero if positions coincide
    if distance_sq == 0:
        return 0, 0
    # Newton's law of gravitation
    force = G * body1.mass * body2.mass / distance_sq
    distance = math.sqrt(distance_sq)
    # Decompose force into x/y
    fx = force * dx / distance
    fy = force * dy / distance
    return fx, fy

def update_bodies(bodies, dt):
    # First compute net force on each body
    forces = [ (0, 0) for _ in bodies ]
    for i, body in enumerate(bodies):
        fx_total = 0.0
        fy_total = 0.0
        for j, other in enumerate(bodies):
            if i == j: 
                continue
            fx, fy = compute_gravitational_force(body, other)
            fx_total += fx
            fy_total += fy
        forces[i] = (fx_total, fy_total)

    # Then update velocities and positions using F=ma
    for i, body in enumerate(bodies):
        fx, fy = forces[i]
        ax = fx / body.mass  # acceleration = force / mass
        ay = fy / body.mass
        # Update velocity
        body.vx += ax * dt
        body.vy += ay * dt
        # Update position
        body.x += body.vx * dt
        body.y += body.vy * dt
        # Record the new position for the orbit trail
        body.orbit.append((body.x, body.y))
