# models/deflection.py
import math

def delta_v_kinetic(m_impactor: float, v_impactor_mps: float, m_asteroid: float, beta: float = 3.0) -> float:
    """
    Very simple momentum-transfer estimate:
    Δv ≈ β * (m_impactor / m_asteroid) * v_impactor
    """
    if m_asteroid <= 0:
        return 0.0
    return beta * (m_impactor / m_asteroid) * v_impactor_mps

def add_delta_v(vx: float, vy: float, dv: float, direction_rad: float):
    """Return (vx, vy) after adding Δv in a chosen direction (radians)."""
    return vx + dv * math.cos(direction_rad), vy + dv * math.sin(direction_rad)
