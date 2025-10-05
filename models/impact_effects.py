# models/impact_effects.py
import math

TNT_J_PER_TON = 4.184e9  # joules in a ton of TNT

def mass_from_diam(d_m: float, density_kgm3: float) -> float:
    """m = π/6 * ρ * D^3"""
    return (math.pi / 6.0) * density_kgm3 * (d_m ** 3)

def kinetic_energy_j(mass_kg: float, v_mps: float) -> float:
    return 0.5 * mass_kg * v_mps * v_mps

def tnt_equiv_kilotons(E_j: float) -> float:
    return (E_j / TNT_J_PER_TON) / 1_000.0

def crater_diameter_km(kt: float) -> float:
    """
    Super-simplified demo scaling:
    D_crater ~ 1.3 km at 1 Mt, scaling with yield^(1/3)
    """
    return 1.3 * ((kt / 1000.0) ** (1.0 / 3.0))

def blast_radii_km(kt: float):
    """
    Very rough 'nuke-style' cube-root scaling for overpressure rings.
    Baseline at 1 Mt: ~3 km (10 psi), ~5 km (5 psi), ~12 km (1 psi).
    """
    scale = (kt / 1000.0) ** (1.0 / 3.0) if kt > 0 else 0.0
    return [
        (10.0, 3.0 * scale),   # (psi, radius_km)
        (5.0,  5.0 * scale),
        (1.0, 12.0 * scale),
    ]

def effects(diameter_m: float, density: float, v_mps: float, angle_deg: float = 90.0) -> dict:
    """
    Return a dict with crater and blast isopleths for visualization.
    NOTE: These are 'toy' formulas for a compelling demo, not peer-reviewed science.
    """
    m = mass_from_diam(diameter_m, density)
    # Very naive 'impact velocity' = entry velocity (angle ignored in this slice)
    E = kinetic_energy_j(m, v_mps)
    kt = tnt_equiv_kilotons(E)

    crater_km = crater_diameter_km(kt)
    rings = blast_radii_km(kt)

    return {
        "mass_kg": m,
        "ke_j": E,
        "yield_kt": kt,
        "crater_diam_km": crater_km,
        "blast_rings": rings,  # list of (psi, radius_km)
    }
