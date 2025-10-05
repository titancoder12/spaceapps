# ui/overlays.py
import pygame
from typing import Tuple, Dict, List
from config import KM_PER_PX

WHITE = (255, 255, 255)
RING = (255, 200, 0)
CRATER = (255, 80, 80)

def _draw_label(screen, text, pos_xy):
    font = pygame.font.SysFont(None, 18)
    screen.blit(font.render(text, True, WHITE), pos_xy)

def draw_effects(screen: pygame.Surface, center_px: Tuple[int, int], eff: Dict):
    """
    Draw crater and blast rings around Earth's center.
    `eff` is the dict from models.impact_effects.effects(...)
    """
    cx, cy = int(center_px[0]), int(center_px[1])

    # Crater (diameter)
    crater_rad_px = max(1, int((eff["crater_diam_km"] / 2.0) / KM_PER_PX))
    pygame.draw.circle(screen, CRATER, (cx, cy), crater_rad_px, width=2)
    _draw_label(screen, f"Crater ~{eff['crater_diam_km']:.1f} km", (cx + crater_rad_px + 6, cy))

    # Blast rings
    y_off = 16
    for psi, radius_km in eff["blast_rings"]:
        r_px = max(1, int(radius_km / KM_PER_PX))
        pygame.draw.circle(screen, RING, (cx, cy), r_px, width=1)
        _draw_label(screen, f"{psi:g} psi ~{radius_km:.1f} km", (cx + r_px + 6, cy + y_off))
        y_off += 16

def info_lines(eff: Dict) -> List[str]:
    return [
        f"Mass ~ {eff['mass_kg']:.3e} kg",
        f"KE   ~ {eff['ke_j']:.3e} J",
        f"Yield ~ {eff['yield_kt']:.1f} kt TNT",
        f"Crater ~ {eff['crater_diam_km']:.2f} km",
    ]
