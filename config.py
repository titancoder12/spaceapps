# config.py
# --- Display / physics scale (tweak for your feel) ---
M_PER_PX = 1_000.0          # 1 pixel ~ 1 km for converting game speed (px/tick) to m/s
SECONDS_PER_TICK = 1.0      # your main loop dt
KM_PER_PX = M_PER_PX / 1000 # convenience for overlays

# --- Defaults for a "typical stony asteroid" ---
DEFAULT_DIAMETER_M = 150.0     # 150 m
DEFAULT_DENSITY = 3000.0       # kg/m^3 (stony)
DEFAULT_IMPACTOR_MASS = 1_000_000.0   # 1000-ton spacecraft (for deflection demo)
DEFAULT_IMPACTOR_SPEED = 10_000.0     # m/s (10 km/s)
DEFAULT_BETA = 3.0                   # momentum enhancement (DART-like, demo)
