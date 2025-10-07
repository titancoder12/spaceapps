# Asteroid Launcher: Newtonian Gravity Sandbox

> “Know thyself and know thy enemy.” — *Sun Tzu*
> In this game, we take on the role of Earth’s adversary to understand the forces that threaten our world — so that we can learn how to save it.

---

## Overview

Asteroid Launcher is an interactive 2D gravity sandbox and planetary-defense simulator built with Python + PyGame for the NASA Space Apps Challenge 2025.

Players launch asteroids toward Earth and observe their realistic motion under Newtonian gravity, influenced by both Earth and the Moon. Missed asteroids remain in orbit, forming an evolving, chaotic multi-body gravitational system.

When an asteroid impacts Earth, the game calculates kinetic energy, crater size, and blast radii. Players can also simulate kinetic deflection—inspired by NASA’s DART mission—to alter an asteroid’s trajectory.

Play the live version: [https://titancoder.itch.io/meteor-madness](https://titancoder.itch.io/meteor-madness)

---

## Challenge Theme

This project addresses the NASA Space Apps Challenge prompt:

> **“Explore asteroid impact scenarios, predict consequences, and evaluate mitigation strategies using real NASA and USGS datasets.”**

Our solution transforms scientific datasets and planetary-defense physics into an engaging, playable simulation.

---

## Features

* Realistic orbital mechanics — Newtonian gravity using semi-implicit Euler integration
* Multi-body gravity — Earth, Moon, and asteroids all interact gravitationally
* Persistent orbits — missed asteroids remain in play indefinitely
* Impact modeling — calculates crater and blast zones from kinetic energy
* Kinetic deflection — press a key to simulate a DART-style Δv nudge
* Real NASA data — integrates [NASA NeoWs API](https://api.nasa.gov/) asteroid parameters
* Hackathon-friendly modular design — physics, entities, models, and UI are cleanly separated

---

## Controls

| Action               | Key        | Description                           |
| -------------------- | ---------- | ------------------------------------- |
| Move launcher        | Arrow keys | Move the cannon around the screen     |
| Adjust angle         | A / D      | Rotate the cannon                     |
| Launch asteroid      | Space      | Fire an asteroid                      |
| Deflect asteroid     | F          | Apply a DART-style Δv                 |
| Load real NEO sample | N          | Load a random asteroid from NASA data |
| Quit game            | Esc        | Exit the simulation                   |

---

## Installation and Setup

You can run the game locally using either pip or conda.

### 1. Clone the repository

```bash
git clone https://github.com/titancoder12/spaceapps.git
cd spaceapps
```

---

### 2A. Setup using Conda (recommended)

Conda provides better isolation and ensures pygame dependencies install cleanly.

```bash
# Create a new environment (Python 3.12 recommended)
conda create -n asteroid_env python=3.12

# Activate it
conda activate asteroid_env

# Install core dependencies
conda install pip
pip install -r requirements.txt
```



---

### 2B. Setup using pip only

If you prefer plain pip (no conda):

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
# OR
venv\Scripts\activate           # Windows

pip install --upgrade pip
pip install -r requirements.txt
```

---

### 3. Run the simulation

```bash
python main.py
```

---

### 4. Run in your browser with PyGBag

To run in a borwser:
```
pygbag .
```
Then open you browser and go to http://localhost:8000/

To build a web version:

```bash
pip install pygbag
pygbag --build .
```

Then open the generated file:

```
/build/web/index.html
```

Your browser version will now run locally using WebAssembly (Pyodide).

---

### (Optional) NASA API Key Setup

If you want to fetch real asteroid data:

1. Visit [https://api.nasa.gov/](https://api.nasa.gov/)
2. Generate a free API key
3. Replace the placeholder DEMO_KEY in `data/nasa_data.py` with your key.

Example:

```python
API_KEY = "YOUR_PERSONAL_KEY"
```

---

## Project Structure

```
spaceapps/
│
├── main.py                     # Game entry point (PyGame + async for PyGBag)
├── physics.py                  # Newtonian gravity integration
├── entities.py                 # CelestialBody class (Earth, Moon, asteroids)
├── orbits.py                   # Orbit setup (Moon around Earth)
├── models/
│   ├── impact_effects.py       # Crater & blast-radius calculations
│   └── deflection.py           # Kinetic-impactor Δv model
├── data/
│   ├── nasa_data.py            # Fetches real asteroid data from NASA NeoWs API
│   └── neows.py                # Offline/sample asteroid data
├── ui/
│   └── overlays.py             # On-screen HUD and orbit trail rendering
├── config.py                   # Gameplay and physical constants
└── screens.py                  # (reserved for future menus)
```

---

## Scientific Basis

* **Gravity:** Newton’s Law of Universal Gravitation
  ( F = G \frac{m_1 m_2}{r^2} )
* **Integrator:** Semi-implicit Euler (stable for orbital motion)
* **Impact Energy:** ( E_k = \frac{1}{2} m v^2 )
* **Crater Scaling:** simplified power-law relation to TNT yield
* **Deflection Model:** ( \Delta v = \beta \frac{m_{impactor}}{m_{asteroid}} v_{impactor} )

---

## Tools and Libraries

* Python 3.12
* PyGame — graphics and event loop
* Requests — NASA API access
* Asyncio / PyGBag — for browser builds
* Git + GitHub — version control
* Google Slides / Canva — presentation visuals

---

## Use of Artificial Intelligence

OpenAI’s ChatGPT (GPT-5) was used to:

* Refine documentation and architecture explanations
* Draft and structure the README and setup guide
* Assist with code readability and modularization

All gameplay logic, physics modeling, and data integration were manually implemented and validated by the team.
No AI-generated images or NASA branding are included.

---

## Team Nova Formosa

**Members:** Christopher T. Lin, Eugene Lin
**Location:** Greater Vancouver, Canada
**Event:** NASA Space Apps Challenge 2025

---

## License

Open-source under the MIT License.
See the `LICENSE` file for details.

---

## Acknowledgments

* [NASA Near-Earth Object Web Service (NeoWs)](https://api.nasa.gov/)
* NASA DART Mission for kinetic-deflection research
* The PyGame and PyGBag open-source communities
* NASA Space Apps Challenge organizers and mentors

