# 🔴 MarsBase v1.2.0

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://marsbase.streamlit.app)
[![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/marsbase?style=social)](https://github.com/YOUR_USERNAME/marsbase)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![NASA MRO Data](https://img.shields.io/badge/Data-NASA%20MRO-orange)](https://mars.nasa.gov/msl/)
[![Artemis Aligned](https://img.shields.io/badge/Mission-Mars%20Sample%20Return-red)](https://mars.nasa.gov/msr/)

> **🔴 Real NASA MRO data. 14 Martian sites. Zero excuses. Pick your Mars base before SpaceX does.**
> 
> Interactive Mars site selector with ice scoring, radiation math, rover tracking, and live solar tracking. Built with Streamlit + MRO.
<a href="https://www.buymeacoffee.com/stargazex" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" 
       alt="Buy Me A Coffee" 
       height="41" 
       width="174">
</a>
---

## 🚀 Live Demo

**Try it now:** [https://marsbase.streamlit.app]
<a href="https://buymeacoffee.com/stargazex" target="_blank"> <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" > </a>

---

## 🛰️ Features

### Core Analysis
- **Interactive NASA MRO Map** — Click anywhere on Mars to generate a custom site analysis instantly.
- **7-Criteria Weighted Scoring Engine** — Illumination (20%), Ice Access (20%), Subsurface Access (20%), Slope Safety (15%), Temperature (10%), Regolith (10%), Comms (5%).
- **14 NASA Candidate Sites** — Pre-loaded with real data for Jezero, Gale, Utopia Planitia, Arcadia Planitia, and more.
- **Seasonal Illumination Model** — Accounts for the 11-year Mars orbital cycle drift (2026–2036).

### Advanced Tooling
- **⚖️ Compare Mode** — Side-by-side comparison of up to 3 sites with a Plotly radar chart and automatic 🏆 winner selection.
- **🛰️ Real-Time Perseverance Rover Tracker** — Live position, mission sol, and great-circle distance to your site.
- **🌪️ Dust Storm Probability Calendar** — Full 12-month Ls chart showing HIGH (red) vs LOW (green) dust storm risk.
- **🕳️ Lava Tube Detection Map** — Probability of subsurface access near confirmed Mars skylights (Pavonis Mons, Arsia Mons).
- **⚡ Best Month to Land Recommender** — Calculates the optimal landing window based on solar illumination + dust storm penalty.
- **🌡️ Day/Night Temperature Swing** — Plotly chart showing the 24.6-hour diurnal cycle with water freezing lines.
- **🧂 Perchlorate Toxicity Warning** — Latitude-based toxicity levels with remediation actions.
- **🌅 Sun Position Animation** — Visualize sunlight changes across a full Martian sol.
- **🧬 Biosignature Probability Map** — CRISM + Perseverance organics data overlay.
- **🔬 InSight Mars Weather Feed** — Last recorded pressure, wind, and ground temperature from the InSight lander.
- **🌌 Night Sky from Mars** — Constellations visible from your site (with latitude-aware adjustments).
- **💎 Mineral Resource Map** — Site-specific mineral composition with mining value scores.
- **🧪 Simulation Lab** — What-if analysis for crew size, habitat mass, and power source (Solar/Hybrid/Nuclear).
- **💾 Persistent Memory** — SQLite-backed analysis history that survives page refreshes.
- **🛰️ Live Solar System Tracker** — Embedded NASA Eyes on the Solar System feed.

---

## 🧪 Data Sources

| Metric | Source |
|--------|--------|
| Illumination | MSL REMS (Curiosity rover) |
| Ice Confidence | MRO SHARAD |
| Slope | MOLA DEM |
| Temperature | Mars Climate Database |
| Regolith Depth | MRO CRISM |
| Subsurface Access | MRO HiRISE |
| Base Map | NASA Mars Trek MOLA Global Mosaic (463m) |
☕ Support the Project
If you find MarsBase useful or just want to support future space data projects:

<a href="https://buymeacoffee.com/stargazex" target="_blank"> <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" > </a>
---
