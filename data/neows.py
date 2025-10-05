# data/neows.py
def sample_neo():
    """
    Returns a minimal 'realistic' preset. Replace with live NeoWs later.
    """
    return {
        "name": "2002 QY6 (demo)",
        "diameter_m": 350.0,     # within published range for many NEOs
        "density_kgm3": 3000.0,
        "speed_mps": 17000.0,    # 17 km/s approach
        "angle_deg": 45.0,
    }
