# Asteroid Launcher: Newtonian Gravity Sandbox

> “Know thyself and know thy enemy.” — Sun Tzu
> In this game, we take on the role of Earth’s adversary to understand the forces that threaten our world — so that we can learn how to save it.

---

## Overview

Asteroid Launcher is an interactive 2D gravity sandbox and planetary defense simulator built with Python + PyGame for the NASA Space Apps Challenge 2025.

Players launch asteroids toward Earth and observe their realistic motion under Newtonian gravity, influenced by both the Earth and a moving Moon. Missed asteroids remain in orbit, forming an evolving, chaotic multi-body gravitational system.

When an asteroid impacts Earth, the game calculates kinetic energy, crater size, and blast radii. Players can also apply kinetic deflection— inspired by NASA’s DART mission— to alter an asteroid’s path and prevent catastrophe.

🎮 Play the live version here: https://titancoder.itch.io/meteor-madness
---

## Challenge Theme

This project addresses the Space Apps challenge:
**“Explore asteroid impact scenarios, predict consequences, and evaluate mitigation strategies using real NASA and USGS datasets.”**

Our solution transforms scientific data and planetary-defense physics into an engaging, playable simulation.

---

## Features

* Realistic orbital mechanics — Newtonian gravity with semi-implicit Euler integration.
* Multi-body system — Earth, Moon, and all launched asteroids interact gravitationally.
* Persistent orbits — every missed shot remains in play and affects future trajectories.
* Impact modeling — calculates crater and blast zones from kinetic energy.
* Kinetic deflection — press a key to simulate a DART-style impactor and nudge an asteroid off course.
* Real NASA data — uses the [NASA NeoWs API](https://api.nasa.gov/) for near-Earth object parameters.
* Hackathon-friendly modular design — clean separation between physics, entities, models, UI, and data.

---

## Controls

| Action               | Key        | Description                                     |
| -------------------- | ---------- | ----------------------------------------------- |
| Move launcher        | Arrow keys | Move the cannon around the screen               |
| Adjust angle         | A / D      | Rotate the cannon counter-clockwise / clockwise |
| Launch asteroid      | Space      | Fire an asteroid (resets previous blast rings)  |
| Deflect asteroid     | F          | Apply a DART-style Δv to the latest asteroid    |
| Load real NEO sample | N          | Load a random asteroid from NASA data           |
| Quit game            | Esc        | Exit the simulation                             |

---

## Installation

### Prerequisites

* Python ≥ 3.10
* pip (Python package manager)

### Clone and run locally

```bash
git clone https://github.com/titancoder12/spaceapps.git
cd spaceapps
pip install -r requirements.txt
python main.py
```

### Run in browser (PyGBag build)

If you package with [pygbag](https://pygame-web.github.io/):

```bash
pygbag --build .
```

Then open the generated `/build/web/index.html` in a browser.

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
│   └── neows.py                # Offline / sample asteroid data
├── ui/
│   └── overlays.py             # On-screen HUD and orbit trail rendering
├── config.py                   # Gameplay and physical constants
└── screens.py                  # (reserved for future menus)
```

---

## Gameplay Example

1. Launch an asteroid toward Earth and watch its curved path under gravity.
2. If it hits Earth, crater and blast rings appear (1 psi / 5 psi / 10 psi).
3. Try pressing **F** to deflect the asteroid mid-flight.
4. The Moon continuously orbits Earth, adding dynamic gravitational interference.

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
* Asyncio / PyGBag — web compatibility
* Git + GitHub — version control
* Google Slides / Canva — visuals for presentation

---

## Use of Artificial Intelligence

OpenAI’s ChatGPT (GPT-5) was used to:

* Assist with documentation, code organization, and explanatory text.
* Draft and refine the README, presentation slides, and challenge submissions.

All gameplay code, physics equations, and data integrations were implemented, tested, and validated by the team.
No AI-generated images, videos, or NASA branding elements are included.

---

## Team Nova Formosa

**Members:**
Christopher T. Lin, Eugene Lin

**Location:** Greater Vancouver, Canada

**Event:** NASA Space Apps Challenge 2025

---

## License

This project is open-source under the **MIT License**.
See the `LICENSE` file for details.

---

## Acknowledgments

* [NASA Near-Earth Object Web Service (NeoWs)](https://api.nasa.gov/) for asteroid data
* NASA DART Mission for real-world kinetic-deflection inspiration
* PyGame and PyGBag open-source communities
* NASA Space Apps Challenge organizers and mentors
