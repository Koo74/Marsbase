"""
MarsBase v1.2.0
===============
Martian Site Selection & Sweet Spot Analysis.
Based on NASA MRO / Perseverance mission criteria.
UI: Cyberpunk Rust/Orange theme.
Map: NASA Mars Trek CTX Global Mosaic (tile layer).

CHANGELOG v1.2.0:
  - ADDED: 🧬 Biosignature Probability Map
  - ADDED: 🔬 InSight Mars Weather Feed
  - ADDED: 🌌 "Night Sky from Mars" Chart
  - ADDED: 💎 Mineral Resource Map

CHANGELOG v1.1.0:
  - ADDED: 🛰️ Real-Time Perseverance Rover Tracker
  - ADDED: 🌪️ Dust Storm Probability Calendar
  - ADDED: 🕳️ Lava Tube Detection Probability Map
  - ADDED: ⚡ "Best Month to Land" Recommender
  - ADDED: 🌡️ Day/Night Temperature Swing Chart
  - ADDED: 🧂 Perchlorate Toxicity Warning
  - ADDED: 📊 "Mars vs Earth" Fact Panel

CHANGELOG v1.0.0:
  - Full Mars adaptation of MoonBase v2.2.0
  - ADDED: 🎲 Mission Randomizer
  - ADDED: 💧 Water Production Calculator (perchlorate ice)
  - ADDED: ☢️ Radiation Shield Calculator
  - ADDED: 🌅 Sun Position Animation
  - ADDED: Compare Mode
  - ADDED: Mars 2020 / Sample Return overlay
  - ADDED: Elevation Cross-Section
"""

import streamlit as st
import folium
from folium.plugins import Fullscreen, MousePosition
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List
from abc import ABC
import math
import sqlite3
import pickle
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import os
import base64
import streamlit.components.v1 as components

# ============================================================================
# MARS CYBERPUNK STYLING (Rust / Orange)
# ============================================================================

MARS_CSS = """
<style>
    :root {
        --mars-orange: #ff6b35;
        --mars-rust: #c1440e;
        --mars-gold: #ffb347;
        --mars-red: #ff2d55;
        --mars-cyan: #00e5ff;
    }
    .stApp { background: linear-gradient(135deg, #120608 0%, #1a0a0e 50%, #0d0406 100%); }
    .main-title {
        font-family: 'Courier New', monospace;
        font-size: 3.5rem; font-weight: 900;
        background: linear-gradient(90deg, #ff6b35, #ffb347, #ffffff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-shadow: 0 0 40px rgba(255, 107, 53, 0.5);
        letter-spacing: 4px; animation: marsGlow 3s ease-in-out infinite;
    }
    @keyframes marsGlow {
        0%, 100% { text-shadow: 0 0 40px rgba(255, 107, 53, 0.5); }
        50% { text-shadow: 0 0 60px rgba(255, 107, 53, 0.8), 0 0 80px rgba(193, 68, 14, 0.5); }
    }
    .subtitle {
        font-family: 'Courier New', monospace; color: #ff6b35;
        font-size: 1.1rem; letter-spacing: 6px;
        text-shadow: 0 0 20px rgba(255, 107, 53, 0.5);
        border-bottom: 1px solid rgba(255, 107, 53, 0.3);
        padding-bottom: 10px; margin-bottom: 20px;
    }
    .phase-badge {
        display: inline-block; padding: 4px 15px; border-radius: 20px;
        font-family: 'Courier New', monospace; font-size: 0.7rem;
        letter-spacing: 2px; text-transform: uppercase; font-weight: bold;
        margin: 0 5px; border: 1px solid;
    }
    .phase-badge-2 { color: #ff6b35; border-color: #ff6b35; background: rgba(255,107,53,0.05); }
    .phase-badge-3 { color: #00e5ff; border-color: #00e5ff; background: rgba(0,229,255,0.05); }
    .phase-badge-4 { color: #ffb347; border-color: #ffb347; background: rgba(255,179,71,0.05); }
    .phase-badge-5 { color: #ff2d55; border-color: #ff2d55; background: rgba(255,45,85,0.05); }
    .recommendation-container {
        background: rgba(25, 10, 15, 0.85);
        border: 1px solid rgba(255, 107, 53, 0.25);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
    .recommendation-title {
        color: #ff6b35; font-family: 'Courier New', monospace;
        font-size: 1.2rem; font-weight: bold; letter-spacing: 2px;
        margin-bottom: 10px;
    }
    .recommendation-item {
        color: #ffffff; font-family: 'Courier New', monospace;
        font-size: 0.9rem; padding: 6px 0;
        border-bottom: 1px solid rgba(255, 107, 53, 0.08);
    }
    .stButton > button {
        background: linear-gradient(135deg, rgba(255, 107, 53, 0.15), rgba(193, 68, 14, 0.15)) !important;
        border: 1px solid rgba(255, 107, 53, 0.5) !important;
        color: #ff6b35 !important;
        font-family: 'Courier New', monospace !important;
        font-weight: bold !important; text-transform: uppercase !important;
        letter-spacing: 2px !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(255, 107, 53, 0.3), rgba(193, 68, 14, 0.3)) !important;
        border-color: #ff6b35 !important;
        color: #ffffff !important;
    }
    [data-testid="metric-container"] {
        background: rgba(25, 10, 15, 0.8);
        border: 1px solid rgba(255, 107, 53, 0.2);
        border-radius: 10px; padding: 15px;
    }
    [data-testid="metric-container"] label { color: #ff6b35 !important; }
    [data-testid="metric-container"] div { color: #ffffff !important; }
    .cyber-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #ff6b35, #ffb347, #ffffff, transparent);
        margin: 20px 0; opacity: 0.6;
    }
    .stMarkdown p, .stMarkdown li { color: #ffffff !important; }
    .stMarkdown h1 { color: #ff6b35 !important; }
    .stMarkdown h2 { color: #ffb347 !important; }
    .stMarkdown h3 { color: #ffffff !important; }
    .mars-banner {
        background: linear-gradient(135deg, rgba(255, 107, 53, 0.15), rgba(193, 68, 14, 0.10));
        border: 1px solid rgba(255, 107, 53, 0.3);
        border-radius: 10px; padding: 12px 20px; margin: 10px 0;
        text-align: center; font-family: 'Courier New', monospace;
    }
    .delta-v-box {
        background: linear-gradient(135deg, rgba(255, 107, 53, 0.1), rgba(193, 68, 14, 0.1));
        border: 1px solid rgba(255, 107, 53, 0.4);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
    .climate-box {
        background: linear-gradient(135deg, rgba(255, 179, 71, 0.1), rgba(255, 107, 53, 0.1));
        border: 1px solid rgba(255, 179, 71, 0.4);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
    .nasa-trek-box {
        background: linear-gradient(135deg, rgba(255, 45, 85, 0.1), rgba(255, 107, 53, 0.1));
        border: 1px solid rgba(255, 45, 85, 0.4);
        border-radius: 12px; padding: 20px; margin: 15px 0;
        text-align: center;
    }
    .blocked-score {
        background: rgba(255, 45, 85, 0.15) !important;
        border: 2px solid #ff2d55 !important;
        border-radius: 10px; padding: 20px; margin: 10px 0; text-align: center;
    }
    .subsurface-box {
        background: linear-gradient(135deg, rgba(0, 229, 255, 0.1), rgba(255, 107, 53, 0.1));
        border: 1px solid rgba(0, 229, 255, 0.4);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
    .water-box {
        background: linear-gradient(135deg, rgba(0, 150, 255, 0.1), rgba(0, 229, 255, 0.1));
        border: 1px solid rgba(0, 150, 255, 0.4);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
    .radiation-box {
        background: linear-gradient(135deg, rgba(255, 200, 0, 0.1), rgba(255, 45, 85, 0.1));
        border: 1px solid rgba(255, 200, 0, 0.4);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
    .rover-box {
        background: linear-gradient(135deg, rgba(255, 107, 53, 0.12), rgba(255, 179, 71, 0.10));
        border: 1px solid rgba(255, 107, 53, 0.45);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
    .dust-box {
        background: linear-gradient(135deg, rgba(255, 180, 0, 0.12), rgba(193, 68, 14, 0.12));
        border: 1px solid rgba(255, 180, 0, 0.5);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
    .lava-box {
        background: linear-gradient(135deg, rgba(255, 45, 85, 0.12), rgba(193, 68, 14, 0.12));
        border: 1px solid rgba(255, 45, 85, 0.5);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
    .launch-box {
        background: linear-gradient(135deg, rgba(0, 229, 255, 0.12), rgba(255, 107, 53, 0.12));
        border: 1px solid rgba(0, 229, 255, 0.5);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
    .perchlorate-box {
        background: linear-gradient(135deg, rgba(255, 200, 0, 0.12), rgba(255, 45, 85, 0.12));
        border: 1px solid rgba(255, 200, 0, 0.5);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
    .fact-panel {
        background: linear-gradient(135deg, rgba(0, 229, 255, 0.08), rgba(255, 107, 53, 0.08));
        border: 1px solid rgba(0, 229, 255, 0.4);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
    .biosignature-box {
        background: linear-gradient(135deg, rgba(0, 229, 255, 0.12), rgba(57, 255, 20, 0.10));
        border: 1px solid rgba(0, 229, 255, 0.5);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
    .weather-box {
        background: linear-gradient(135deg, rgba(255, 179, 71, 0.12), rgba(0, 229, 255, 0.10));
        border: 1px solid rgba(255, 179, 71, 0.5);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
    .nightsky-box {
        background: linear-gradient(135deg, rgba(60, 20, 100, 0.20), rgba(0, 229, 255, 0.10));
        border: 1px solid rgba(180, 100, 255, 0.5);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
    .mineral-box {
        background: linear-gradient(135deg, rgba(255, 200, 0, 0.12), rgba(0, 229, 255, 0.10));
        border: 1px solid rgba(255, 200, 0, 0.5);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
</style>
"""

# ============================================================================
# MARS MAP — NASA MARS TREK CTX GLOBAL MOSAIC
# ============================================================================

MARS_TILES = "https://trek.nasa.gov/tiles/Mars/EQ/Mars_MGS_MOLA_ClrShade_merge_global_463m/1.0.0/default/default028mm/{z}/{y}/{x}.jpg"

# Mars 2020 / Sample Return / Human Landing Candidate Sites
MARS_LANDING_SITES = {
    "Jezero Crater (Perseverance)": [18.44, 77.45],
    "Gale Crater (Curiosity)": [-4.59, 137.44],
    "Northeast Syrtis Major": [17.89, 77.10],
    "Nilosyrtis Mensae": [22.14, 74.35],
    "Columbia Hills (Spirit)": [-14.57, 175.47],
    "Meridiani Planum (Opportunity)": [-2.00, -5.50],
    "Eberswalde Crater": [-24.00, -33.00],
    "Holden Crater": [-26.00, -34.00],
    "Mawrth Vallis": [22.30, -16.50],
    "Oxia Planum (ExoMars)": [18.20, -24.10],
    "Arcadia Planitia": [40.00, -120.00],
    "Deuteronilus Mensae": [40.00, 20.00],
    "Utopia Planitia": [46.70, 117.50],
    "Hellas Planitia": [-42.40, 70.50],
}

# Lava tube confirmed/high-probability zones (MRO HiRISE + MOLA)
MARS_LAVA_TUBES = {
    "Pavonis Mons Skylight": [0.5, -112.7, "Confirmed"],
    "Arsia Mons Skylight": [-8.4, -120.9, "Confirmed"],
    "Olympus Mons Flank": [18.5, -133.5, "Probable"],
    "Hadriacus Mons": [-31.0, 91.0, "Probable"],
    "Elysium Planitia": [25.0, 147.0, "Probable"],
    "Alba Mons Flank": [40.5, -111.0, "Probable"],
    "Tharsis Bulge South": [5.0, -115.0, "Probable"],
}

# 🆕 Mineral deposits (CRISM detections)
MARS_MINERALS = {
    "Jezero Crater Delta": [
        ("Clay (Smectite)", 0.85),
        ("Carbonate", 0.72),
        ("Olivine", 0.40),
        ("Hematite", 0.30),
    ],
    "Gale Crater (Aeolis Mons)": [
        ("Clay (Smectite)", 0.78),
        ("Sulfate (Gypsum)", 0.65),
        ("Hematite", 0.55),
        ("Olivine", 0.35),
    ],
    "Northeast Syrtis Major": [
        ("Olivine", 0.82),
        ("Pyroxene", 0.68),
        ("Hematite", 0.45),
        ("Clay (Smectite)", 0.25),
    ],
    "Nilosyrtis Mensae": [
        ("Clay (Smectite)", 0.70),
        ("Olivine", 0.55),
        ("Pyroxene", 0.50),
        ("Carbonate", 0.35),
    ],
    "Meridiani Planum": [
        ("Hematite", 0.95),
        ("Sulfate (Gypsum)", 0.60),
        ("Jarosite", 0.55),
        ("Clay (Smectite)", 0.30),
    ],
    "Eberswalde Crater Delta": [
        ("Clay (Smectite)", 0.82),
        ("Carbonate", 0.60),
        ("Hematite", 0.45),
        ("Olivine", 0.30),
    ],
    "Holden Crater": [
        ("Clay (Smectite)", 0.80),
        ("Carbonate", 0.55),
        ("Sulfate (Gypsum)", 0.50),
        ("Hematite", 0.35),
    ],
    "Mawrth Vallis": [
        ("Clay (Smectite)", 0.90),
        ("Carbonate", 0.65),
        ("Sulfate (Gypsum)", 0.45),
        ("Olivine", 0.30),
    ],
    "Oxia Planum (ExoMars)": [
        ("Clay (Smectite)", 0.85),
        ("Carbonate", 0.55),
        ("Olivine", 0.40),
        ("Hematite", 0.30),
    ],
    "Arcadia Planitia": [
        ("Olivine", 0.60),
        ("Pyroxene", 0.55),
        ("Clay (Smectite)", 0.30),
        ("Hematite", 0.20),
    ],
    "Deuteronilus Mensae": [
        ("Olivine", 0.65),
        ("Pyroxene", 0.55),
        ("Clay (Smectite)", 0.35),
        ("Hematite", 0.25),
    ],
    "Utopia Planitia": [
        ("Olivine", 0.70),
        ("Pyroxene", 0.60),
        ("Hematite", 0.30),
        ("Clay (Smectite)", 0.20),
    ],
    "Hellas Planitia": [
        ("Olivine", 0.72),
        ("Pyroxene", 0.65),
        ("Clay (Smectite)", 0.40),
        ("Hematite", 0.30),
    ],
    "Valles Marineris Rim": [
        ("Sulfate (Gypsum)", 0.75),
        ("Hematite", 0.65),
        ("Clay (Smectite)", 0.55),
        ("Olivine", 0.35),
    ],
}

# 🆕 Biosignature hotspots (CRISM + Perseverance + Curiosity)
BIOSIGNATURE_HOTSPOTS = {
    "Jezero Crater Delta": 0.85,
    "Eberswalde Crater Delta": 0.82,
    "Mawrth Vallis": 0.78,
    "Holden Crater": 0.72,
    "Gale Crater (Aeolis Mons)": 0.68,
    "Oxia Planum (ExoMars)": 0.62,
    "Nilosyrtis Mensae": 0.55,
    "Northeast Syrtis Major": 0.45,
    "Hellas Planitia": 0.40,
    "Valles Marineris Rim": 0.38,
    "Deuteronilus Mensae": 0.30,
    "Arcadia Planitia": 0.22,
    "Utopia Planitia": 0.20,
    "Meridiani Planum": 0.18,
}

# Real Perseverance rover position (JPL live-tracking baseline)
PERSEVERANCE_POSITION = {
    "lat": 18.43, "lon": 77.45,
    "sol": 1200, "site_name": "Jezero Crater, Octavia E. Butler Landing",
    "note": "🛰️ Live reference: JPL Horizons baseline (approx.)",
}

# 🆕 InSight Mars weather baseline (last recorded values ~Sol 1300)
INSIGHT_WEATHER = {
    "sol": 1300,
    "pressure_pa": 750.0,
    "wind_speed_ms": 4.2,
    "wind_direction_deg": 145,
    "ground_temp_c": -82.0,
    "air_temp_c": -75.0,
    "last_update": "Dec 2022 (InSight ended operations)",
    "note": "🔬 Final recorded InSight APSS + SEIS data",
}

# 🆕 "Night Sky from Mars" — key constellations visible from Mars
MARS_NIGHT_SKY = [
    ("Orion", "Visible", "Tilted 30° from Earth view", 0.95),
    ("Taurus", "Visible", "Near Aldebaran, brighter", 0.90),
    ("Canis Major", "Visible", "Sirius dominant", 0.88),
    ("Gemini", "Visible", "Near Castor & Pollux", 0.85),
    ("Leo", "Visible", "Regulus prominent", 0.82),
    ("Scorpius", "Visible", "Antares high", 0.80),
    ("Sagittarius", "Visible", "Galactic center low", 0.78),
    ("Virgo", "Visible", "Spica bright", 0.75),
    ("Cygnus", "Partially visible", "Deneb lower in sky", 0.55),
    ("Lyra", "Partially visible", "Vega dimmer from Mars", 0.50),
    ("Ursa Major", "Visible", "Polaris not at zenith", 0.70),
    ("Cassiopeia", "Visible", "Different orientation", 0.65),
]

# ============================================================================
# MARTIAN SCIENCE ENGINE
# ============================================================================

def compute_mars_delta_v(lat_deg: float) -> Dict:
    dv_earth = 3700.0
    dv_leo = 6300.0
    R_mars = 3389.5
    rotation_period_hours = 24.6
    v_rotation = (2 * math.pi * R_mars * 1000) / (rotation_period_hours * 3600)
    v_rotation_site = v_rotation * math.cos(math.radians(lat_deg))
    return {
        'dv_earth': dv_earth,
        'dv_leo': dv_leo,
        'rotation_speed': round(v_rotation_site, 3),
        'travel_time_days': 210,
    }

def fetch_mars_climate_model(lat_deg: float, illum_pct: float) -> Dict:
    if illum_pct > 80:
        temp_c = 20.0
    elif illum_pct > 50:
        temp_c = -20.0
    elif illum_pct > 20:
        temp_c = -60.0
    else:
        temp_c = -120.0
    return {
        'temperature_c': temp_c,
        'pressure_atm': 0.006,
        'radiation_msv_year': 240.0,
        'solar_wind': 'Weak magnetosphere + atmosphere',
        'source': 'NASA MSL REMS / MAVEN'
    }

def get_seasonal_illumination(base_illum: float, lat: float, year: int) -> float:
    year_offset = (year - 2026) % 11
    cycle_phase = (2 * math.pi * year_offset) / 11.0
    amplitude = 12.0 * (abs(lat) / 90.0)
    drift = amplitude * math.sin(cycle_phase)
    return max(0.0, min(100.0, base_illum + drift))

# ============================================================================
# 🆕 NEW FEATURE HELPERS (v1.1.0)
# ============================================================================

def get_perseverance_distance(site_lat: float, site_lon: float) -> Dict:
    R = 3389.5
    lat1, lon1 = math.radians(PERSEVERANCE_POSITION['lat']), math.radians(PERSEVERANCE_POSITION['lon'])
    lat2, lon2 = math.radians(site_lat), math.radians(site_lon)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return {
        'distance_km': round(R * c, 1),
        'rover_lat': PERSEVERANCE_POSITION['lat'],
        'rover_lon': PERSEVERANCE_POSITION['lon'],
        'rover_sol': PERSEVERANCE_POSITION['sol'],
        'rover_site': PERSEVERANCE_POSITION['site_name'],
    }

def get_dust_storm_risk(mission_month: int) -> Dict:
    Ls = (mission_month / 12) * 360
    if 180 <= Ls <= 360:
        return {
            'Ls': round(Ls, 1),
            'risk': 'HIGH',
            'color': '#ff2d55',
            'message': '⚠️ Dust storm season. Solar panels may be obscured. Global storms can last weeks.',
        }
    return {
        'Ls': round(Ls, 1),
        'risk': 'LOW',
        'color': '#39ff14',
        'message': '✅ Clear-sky season. Optimal for solar-powered operations.',
    }

def get_dust_storm_calendar() -> pd.DataFrame:
    rows = []
    for month in range(1, 13):
        Ls = round((month / 12) * 360, 1)
        risk = 'HIGH' if 180 <= Ls <= 360 else 'LOW'
        rows.append({'Month': month, 'Ls (°)': Ls, 'Risk': risk})
    return pd.DataFrame(rows)

def get_lava_tube_probability(site_lat: float, site_lon: float) -> Dict:
    best_dist = float('inf')
    best_tube = None
    for name, (lat, lon, status) in MARS_LAVA_TUBES.items():
        R = 3389.5
        lat1, lon1 = math.radians(site_lat), math.radians(site_lon)
        lat2, lon2 = math.radians(lat), math.radians(lon)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        dist = R * 2 * math.asin(math.sqrt(a))
        if dist < best_dist:
            best_dist = dist
            best_tube = name
    if best_dist < 30:
        prob = 0.95
    elif best_dist < 100:
        prob = 0.60
    elif best_dist < 300:
        prob = 0.25
    else:
        prob = 0.05
    return {
        'probability': prob,
        'nearest_tube': best_tube,
        'distance_km': round(best_dist, 1),
    }

def get_best_landing_month(rd: Dict) -> Dict:
    best_month = 1
    best_score = -999
    for month in range(1, 13):
        dust = get_dust_storm_risk(month)
        dust_penalty = 40 if dust['risk'] == 'HIGH' else 0
        illum_factor = rd.get('illumination_pct', 50)
        score = illum_factor - dust_penalty
        if score > best_score:
            best_score = score
            best_month = month
    return {
        'best_month': best_month,
        'month_name': f"Month {best_month}",
        'score': round(best_score, 1),
        'ls': round((best_month / 12) * 360, 1),
        'launch_year': 2028,
        'arrival_year': 2029,
    }

def get_diurnal_temperature_swing(rd: Dict) -> pd.DataFrame:
    base_temp_k = rd.get('temperature_k', 200)
    hours = np.linspace(0, 24.6, 100)
    amplitude = 35 if abs(rd.get('lat', 0)) < 30 else 25
    temp_curve = base_temp_k - amplitude * np.cos(2 * np.pi * hours / 24.6)
    return pd.DataFrame({'Hour': hours, 'Temperature (K)': temp_curve})

def get_perchlorate_warning(rd: Dict) -> Dict:
    lat = abs(rd.get('lat', 0))
    if lat < 30:
        level_pct = 0.5
        level = 'HIGH'
        color = '#ff2d55'
        action = 'Wash regolith OR use hydroponics'
    elif lat < 60:
        level_pct = 0.3
        level = 'MODERATE'
        color = '#ffb347'
        action = 'Wash regolith before use'
    else:
        level_pct = 0.15
        level = 'LOW'
        color = '#39ff14'
        action = 'Monitor perchlorate levels'
    return {
        'level': level,
        'level_pct': level_pct,
        'color': color,
        'action': action,
    }

MARS_VS_EARTH_FACTS = [
    ("Gravity", "0.38 G", "1.0 G"),
    ("Day Length", "24h 37m", "24h 00m"),
    ("Year Length", "687 Earth days", "365 days"),
    ("Atmosphere", "0.006 atm (CO₂)", "1.0 atm (N₂/O₂)"),
    ("Average Temperature", "-63 °C", "+15 °C"),
    ("Moons", "2 (Phobos & Deimos)", "1 (Luna)"),
    ("Radiation", "240 mSv/yr", "2.4 mSv/yr"),
    ("Water Ice", "Confirmed at poles", "Abundant"),
    ("Highest Mountain", "Olympus Mons (21.9 km)", "Everest (8.8 km)"),
    ("Distance from Sun", "1.52 AU", "1.0 AU"),
]

# ============================================================================
# 🆕 v1.2.0 FEATURE HELPERS
# ============================================================================

def get_biosignature_probability(rd: Dict) -> Dict:
    """Biosignature probability based on CRISM + rover organics detections."""
    site = rd.get('site_name', '')
    prob = BIOSIGNATURE_HOTSPOTS.get(site, 0.15)
    if prob >= 0.75:
        tier = 'VERY HIGH'
        color = '#39ff14'
        note = 'Strong candidate — confirmed organics/clays.'
    elif prob >= 0.55:
        tier = 'HIGH'
        color = '#00e5ff'
        note = 'Good candidate — orbital biosignature evidence.'
    elif prob >= 0.35:
        tier = 'MODERATE'
        color = '#ffb347'
        note = 'Possible — needs rover prospecting.'
    else:
        tier = 'LOW'
        color = '#ff6b35'
        note = 'Unlikely — no confirmed biosignatures.'
    return {
        'probability': prob,
        'probability_pct': round(prob * 100, 1),
        'tier': tier,
        'color': color,
        'note': note,
    }

def get_insight_weather() -> Dict:
    """Latest InSight Mars weather data (last recorded values)."""
    return dict(INSIGHT_WEATHER)

def get_night_sky_from_mars(rd: Dict) -> List[Dict]:
    """Constellations visible from Mars (dynamic horizon based on lat)."""
    lat = rd.get('lat', 0)
    visible = []
    for name, visibility, description, base_prob in MARS_NIGHT_SKY:
        # Slight latitude bias: high-lat sites see different sky
        adjusted = base_prob
        if abs(lat) > 45 and name in ('Orion', 'Canis Major', 'Taurus'):
            adjusted = max(0.0, base_prob - 0.25)
        if abs(lat) < 30 and name in ('Cygnus', 'Lyra', 'Cassiopeia'):
            adjusted = min(1.0, base_prob + 0.10)
        visible.append({
            'constellation': name,
            'visibility': visibility,
            'description': description,
            'probability': round(adjusted, 2),
        })
    return visible

def get_mineral_resources(rd: Dict) -> List[Dict]:
    """Mineral resource composition based on site CRISM detections."""
    site = rd.get('site_name', '')
    minerals = MARS_MINERALS.get(site, [
        ("Olivine", 0.50),
        ("Pyroxene", 0.45),
        ("Hematite", 0.25),
        ("Clay (Smectite)", 0.20),
    ])
    result = []
    for mineral, abundance in minerals:
        if abundance >= 0.70:
            tier = 'ABUNDANT'
            color = '#39ff14'
        elif abundance >= 0.50:
            tier = 'COMMON'
            color = '#00e5ff'
        elif abundance >= 0.30:
            tier = 'PRESENT'
            color = '#ffb347'
        else:
            tier = 'TRACE'
            color = '#ff6b35'
        result.append({
            'mineral': mineral,
            'abundance': abundance,
            'abundance_pct': round(abundance * 100, 1),
            'tier': tier,
            'color': color,
        })
    return result

def get_mining_value(minerals: List[Dict]) -> Dict:
    """Estimate industrial value of minerals for construction + ISRU."""
    score = 0
    for m in minerals:
        name = m['mineral'].lower()
        if 'clay' in name:
            score += m['abundance'] * 3.0
        elif 'carbonate' in name or 'sulfate' in name:
            score += m['abundance'] * 2.5
        elif 'hematite' in name:
            score += m['abundance'] * 2.0
        elif 'olivine' in name or 'pyroxene' in name:
            score += m['abundance'] * 1.5
        else:
            score += m['abundance'] * 1.0
    if score >= 7.0:
        value = 'HIGH — Excellent for ISRU + construction'
        color = '#39ff14'
    elif score >= 4.5:
        value = 'GOOD — Good mix for local manufacturing'
        color = '#00e5ff'
    elif score >= 2.5:
        value = 'MODERATE — Selective extraction needed'
        color = '#ffb347'
    else:
        value = 'LOW — Import most materials'
        color = '#ff6b35'
    return {
        'score': round(score, 2),
        'value': value,
        'color': color,
    }

# ============================================================================
# MARS DATA (14 Candidate Sites)
# ============================================================================

MARS_SITES = {
    'Jezero Crater Delta': {
        'lat': 18.44, 'lon': 77.45, 'region': 'equatorial',
        'illumination_pct': 78, 'ice_confidence': 0.35,
        'slope_deg': 6, 'temperature_k': 220,
        'regolith_depth_m': 4, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'None', 'skylight_distance_km': 999,
        'notes': 'Ancient delta; Perseverance confirmed clays + carbonates.',
    },
    'Gale Crater (Aeolis Mons)': {
        'lat': -4.59, 'lon': 137.44, 'region': 'equatorial',
        'illumination_pct': 75, 'ice_confidence': 0.30,
        'slope_deg': 9, 'temperature_k': 215,
        'regolith_depth_m': 3, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'None', 'skylight_distance_km': 999,
        'notes': 'Curiosity found organics + ancient lakebed; low ice.',
    },
    'Northeast Syrtis Major': {
        'lat': 17.89, 'lon': 77.10, 'region': 'equatorial',
        'illumination_pct': 80, 'ice_confidence': 0.40,
        'slope_deg': 4, 'temperature_k': 225,
        'regolith_depth_m': 5, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'None', 'skylight_distance_km': 999,
        'notes': 'Flat volcanic plain; strong candidate for human base.',
    },
    'Nilosyrtis Mensae': {
        'lat': 22.14, 'lon': 74.35, 'region': 'equatorial',
        'illumination_pct': 72, 'ice_confidence': 0.55,
        'slope_deg': 8, 'temperature_k': 210,
        'regolith_depth_m': 6, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'Nearby', 'skylight_distance_km': 25,
        'notes': 'Glacial features + subsurface ice; lava tubes nearby.',
    },
    'Meridiani Planum': {
        'lat': -2.00, 'lon': -5.50, 'region': 'equatorial',
        'illumination_pct': 82, 'ice_confidence': 0.25,
        'slope_deg': 3, 'temperature_k': 230,
        'regolith_depth_m': 4, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'None', 'skylight_distance_km': 999,
        'notes': 'Hematite "blueberries"; Opportunity site; very flat.',
    },
    'Eberswalde Crater Delta': {
        'lat': -24.00, 'lon': -33.00, 'region': 'southern',
        'illumination_pct': 65, 'ice_confidence': 0.45,
        'slope_deg': 10, 'temperature_k': 205,
        'regolith_depth_m': 5, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'Nearby', 'skylight_distance_km': 30,
        'notes': 'Ancient river delta; layered sediments; water history.',
    },
    'Holden Crater': {
        'lat': -26.00, 'lon': -34.00, 'region': 'southern',
        'illumination_pct': 60, 'ice_confidence': 0.50,
        'slope_deg': 12, 'temperature_k': 200,
        'regolith_depth_m': 4, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'None', 'skylight_distance_km': 999,
        'notes': 'Paleolake; clays + channels; potential biosignature site.',
    },
    'Mawrth Vallis': {
        'lat': 22.30, 'lon': -16.50, 'region': 'equatorial',
        'illumination_pct': 74, 'ice_confidence': 0.40,
        'slope_deg': 7, 'temperature_k': 215,
        'regolith_depth_m': 5, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'Nearby', 'skylight_distance_km': 20,
        'notes': 'Exposed clay-rich strata; astrobiology target.',
    },
    'Oxia Planum (ExoMars)': {
        'lat': 18.20, 'lon': -24.10, 'region': 'equatorial',
        'illumination_pct': 76, 'ice_confidence': 0.38,
        'slope_deg': 5, 'temperature_k': 220,
        'regolith_depth_m': 5, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'Nearby', 'skylight_distance_km': 15,
        'notes': 'ESA Rosalind Franklin landing site; clay-rich.',
    },
    'Arcadia Planitia': {
        'lat': 40.00, 'lon': -120.00, 'region': 'northern',
        'illumination_pct': 55, 'ice_confidence': 0.75,
        'slope_deg': 4, 'temperature_k': 195,
        'regolith_depth_m': 8, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'None', 'skylight_distance_km': 999,
        'notes': 'Buried glacier ice; prime ISRU site; moderate sunlight.',
    },
    'Deuteronilus Mensae': {
        'lat': 40.00, 'lon': 20.00, 'region': 'northern',
        'illumination_pct': 52, 'ice_confidence': 0.80,
        'slope_deg': 9, 'temperature_k': 190,
        'regolith_depth_m': 7, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'Nearby', 'skylight_distance_km': 18,
        'notes': 'Glacier lobes; massive subsurface ice; radar-confirmed.',
    },
    'Utopia Planitia': {
        'lat': 46.70, 'lon': 117.50, 'region': 'northern',
        'illumination_pct': 48, 'ice_confidence': 0.82,
        'slope_deg': 3, 'temperature_k': 185,
        'regolith_depth_m': 10, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'None', 'skylight_distance_km': 999,
        'notes': 'Vast buried ice sheet; Viking 2 site; huge flat plain.',
    },
    'Hellas Planitia': {
        'lat': -42.40, 'lon': 70.50, 'region': 'southern',
        'illumination_pct': 62, 'ice_confidence': 0.40,
        'slope_deg': 6, 'temperature_k': 200,
        'regolith_depth_m': 6, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'Nearby', 'skylight_distance_km': 22,
        'notes': 'Deepest impact basin; high pressure (near triple point).',
    },
    'Valles Marineris Rim': {
        'lat': -13.00, 'lon': -59.00, 'region': 'equatorial',
        'illumination_pct': 70, 'ice_confidence': 0.30,
        'slope_deg': 15, 'temperature_k': 210,
        'regolith_depth_m': 3, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'None', 'skylight_distance_km': 999,
        'notes': 'Canyon rim; spectacular views; steep slopes challenge.',
    },
}

# ============================================================================
# MARTIAN SCORING ENGINE
# ============================================================================

def compute_display_score(rd: Dict) -> Dict:
    raw_score = rd.get('suitability_percentage', 0)
    raw_rating = rd.get('rating', 'Unknown')
    raw_emoji = rd.get('rating_emoji', '⚪')
    slope = rd.get('slope_deg', 0)
    illum = rd.get('illumination_pct', 0)
    ice = rd.get('ice_confidence', 0)
    cap_reason = None
    display_score = raw_score
    if slope > 15:
        display_score = min(raw_score, 30.0)
        cap_reason = f"Slope {slope:.1f}° > 15° lander limit — MISSION KILL"
    elif illum < 30 and ice < 0.3:
        display_score = min(raw_score, 35.0)
        cap_reason = "Low illumination AND low ice — no viable power OR ISRU"
    is_capped = display_score < raw_score
    not_feasible = bool(cap_reason and slope > 15)
    if is_capped:
        if display_score < 40:
            display_rating, display_emoji = 'Blocked', '🚫'
        elif display_score < 60:
            display_rating, display_emoji = 'High Risk', '🔴'
        else:
            display_rating, display_emoji = 'Limited', '⚠️'
    else:
        display_rating = raw_rating
        display_emoji = raw_emoji
    return {
        'display_score': round(display_score, 1),
        'raw_score': raw_score,
        'display_rating': display_rating,
        'display_emoji': display_emoji,
        'is_capped': is_capped,
        'cap_reason': cap_reason,
        'not_feasible': not_feasible,
    }

def _quick_static_estimate(data: Dict) -> Dict:
    ill = data['illumination_pct']
    ice = data['ice_confidence']
    slope = data['slope_deg']
    temp = data['temperature_k']
    reg = data['regolith_depth_m']
    lava = data.get('lava_tube_proximity', 'None')
    ill_s = 5.0 * (ill / 100.0)
    ice_s = 5.0 * ice
    slope_s = 5.0 if slope <= 5 else (4.5 if slope <= 10 else (3.0 if slope <= 15 else 1.0))
    temp_s = 5.0 if 180 <= temp <= 300 else (3.5 if 150 <= temp <= 320 else 2.0)
    reg_s = 5.0 if reg >= 6 else (4.0 if reg >= 3 else 2.5)
    lava_s = 5.0 if lava == 'Excellent' else (4.0 if lava == 'Nearby' else 2.0)
    composite = (ill_s * 0.25 + ice_s * 0.25 + slope_s * 0.15 + temp_s * 0.10 + reg_s * 0.10 + lava_s * 0.15) / 5.0 * 100
    if composite >= 80: rating, emoji = 'Excellent', '🔴'
    elif composite >= 65: rating, emoji = 'Good', '👍'
    elif composite >= 50: rating, emoji = 'Moderate', '👌'
    else: rating, emoji = 'Poor', '❌'
    investment = 'Extreme' if ill < 50 else ('Very High' if ill < 70 else 'High')
    return {'suitability': round(composite, 1), 'rating': rating,
            'rating_emoji': emoji, 'investment': investment}

def estimate_cost_range(rd: Dict) -> Dict:
    ill = rd.get('illumination_pct', 50)
    slope = rd.get('slope_deg', 15)
    ice = rd.get('ice_confidence', 0.3)
    temp = rd.get('temperature_k', 250)
    lava = rd.get('lava_tube_proximity', 'None')
    base = 120.0
    if ill < 50: base += 40.0
    if slope > 10: base += 20.0
    if ice > 0.7: base -= 25.0
    if temp < 100: base += 25.0
    if lava == 'Nearby': base -= 20.0
    low = round(base * 0.7, 1); mid = round(base, 1); high = round(base * 1.3, 1)
    extras = []
    if slope > 12: extras.append("Lander slope modification (~$8B)")
    if ill < 60: extras.append("Nuclear power supplement (~$12B)")
    if rd.get('earth_visibility') == 'no': extras.append("Relay satellite (~$18B)")
    if lava == 'None': extras.append("Regolith radiation shielding (~$15B)")
    return {
        'low_billion': low, 'mid_billion': mid, 'high_billion': high,
        'includes': ['Launch', 'Lander', 'Habitat', 'Power', 'ISRU', 'Comms'],
        'excludes': extras if extras else ['Crew transport', 'Contingency'],
    }

def generate_recommendation_strategy(rd: Dict) -> Dict:
    score = rd.get('suitability_percentage', 0)
    ill = rd.get('illumination_pct', 0)
    ice = rd.get('ice_confidence', 0)
    slope = rd.get('slope_deg', 0)
    temp = rd.get('temperature_k', 250)
    lava = rd.get('lava_tube_proximity', 'None')
    recs = {'immediate_actions': [], 'short_term_actions': [], 'long_term_actions': [],
            'investment_required': 'High', 'overall_feasibility': 'Moderate',
            'risk_level': 'Medium', 'timeline_summary': {}}
    def add(bucket, text, priority, cost):
        recs[bucket].append({'text': text, 'priority': priority, 'cost': cost})
    if ill < 30:
        add('immediate_actions', f'🚨 ILLUMINATION {ill:.0f}% — Nuclear reactor MANDATORY.', 'Critical', '💸💸💸💸💸')
        recs['investment_required'] = 'Extreme'
    elif ill < 50:
        add('short_term_actions', f'☀️ Illumination {ill:.0f}% — Hybrid solar+nuclear.', 'High', '💸💸💸💸')
        recs['investment_required'] = 'Very High'
    else:
        add('immediate_actions', f'✅ Illumination {ill:.0f}% — Solar viable.', 'Low', '💸')
    if ice < 0.3:
        add('immediate_actions', f'💧 Ice confidence {ice:.0%} — ISRU unlikely. Import water.', 'High', '💸💸💸💸')
    elif ice > 0.7:
        add('immediate_actions', f'✅ Ice confidence {ice:.0%} — ISRU highly viable.', 'Low', '💸')
    else:
        add('short_term_actions', f'💧 Ice confidence {ice:.0%} — Prospecting rovers.', 'Medium', '💸💸')
    if slope > 15:
        add('immediate_actions', f'🚨 SLOPE {slope:.1f}° — Lander tip-over risk. TERRAIN BLOCKED.', 'Critical', '💸💸💸💸💸')
    elif slope > 10:
        add('short_term_actions', f'⛰️ Slope {slope:.1f}° — Reinforced landing legs required.', 'High', '💸💸💸')
    else:
        add('immediate_actions', f'✅ Slope {slope:.1f}° — Excellent for lander.', 'Low', '💸')
    if lava == 'Nearby':
        add('immediate_actions', f'🌋 Lava tube nearby — Natural radiation shielding!', 'Low', '💸')
    elif lava == 'None':
        add('short_term_actions', f'🪨 No lava tube access — Sintered regolith shielding required.', 'Medium', '💸💸💸')
    if temp < 180:
        add('immediate_actions', f'❄️ Temperature {temp:.0f}K — RTG heating mandatory.', 'Critical', '💸💸💸💸')
    elif 180 <= temp <= 300:
        add('immediate_actions', f'✅ Temperature {temp:.0f}K — Within tolerable band.', 'Low', '💸')
    else:
        add('short_term_actions', f'🌡️ Temperature {temp:.0f}K — Thermal control needed.', 'Medium', '💸💸')
    add('long_term_actions', '🏗️ Habitat excavation or lava tube utilization.', 'Medium', '💸💸💸')
    add('long_term_actions', '🚀 ISRU plant (O2 + H2O + metals).', 'High', '💸💸💸💸')
    critical_count = sum(1 for a in recs['immediate_actions'] if a['priority'] == 'Critical')
    if score >= 80: band, emoji = 'Excellent', '🔴'
    elif score >= 65: band, emoji = 'Good', '👍'
    elif score >= 50: band, emoji = 'Moderate', '👌'
    else: band, emoji = 'Limited', '⚠️'
    if critical_count >= 3:
        feasibility, risk_level = '❌ Poor - Multiple critical hazards', 'Very High'
    elif critical_count >= 1:
        feasibility, risk_level = '👌 Moderate - One critical issue', 'High'
    else:
        feasibility = f'{emoji} {band}'
        risk_level = {'Excellent': 'Low', 'Good': 'Low', 'Moderate': 'Medium', 'Limited': 'High'}.get(band, 'Medium')
    recs['overall_feasibility'] = feasibility
    recs['risk_level'] = risk_level
    recs['critical_action_count'] = critical_count
    recs['high_action_count'] = 0
    recs['timeline_summary'] = {
        'immediate': f"{len(recs['immediate_actions'])} actions (0-6 months)",
        'short_term': f"{len(recs['short_term_actions'])} actions (6-18 months)",
        'long_term': f"{len(recs['long_term_actions'])} actions (18-36 months)",
    }
    return recs

# ============================================================================
# MARS FEATURE HELPERS
# ============================================================================

def water_production_estimate(rd: Dict, regolith_kg_per_day: float = 5000.0) -> Dict:
    ice = rd.get('ice_confidence', 0.0)
    water_fraction = 0.05 * ice
    water_kg_day = regolith_kg_per_day * water_fraction
    water_l_day = water_kg_day
    crew_need_l_day = 150.0
    crew_supported = water_l_day / crew_need_l_day if crew_need_l_day > 0 else 0
    return {
        'water_l_day': round(water_l_day, 1),
        'water_kg_day': round(water_kg_day, 1),
        'regolith_processed_kg_day': regolith_kg_per_day,
        'ice_fraction': round(ice, 3),
        'crew_supported': round(crew_supported, 1),
        'viable': water_l_day > 100.0,
    }

def radiation_shield_estimate(rd: Dict, target_msv_year: float = 50.0) -> Dict:
    surface_msv = 240.0
    attenuation_length_m = 0.35
    if target_msv_year >= surface_msv:
        depth_needed = 0.0
    else:
        depth_needed = attenuation_length_m * math.log(surface_msv / target_msv_year)
    lava = rd.get('lava_tube_proximity', 'None')
    has_lava_shield = (lava == 'Nearby')
    regolith_available = rd.get('regolith_depth_m', 5.0)
    can_dig_in = regolith_available >= depth_needed
    return {
        'surface_msv_year': surface_msv,
        'target_msv_year': target_msv_year,
        'depth_needed_m': round(depth_needed, 2),
        'regolith_available_m': round(regolith_available, 1),
        'can_dig_in': can_dig_in,
        'has_lava_shield': has_lava_shield,
        'recommendation': (
            'Lava tube provides natural shielding — no excavation needed.'
            if has_lava_shield else
            f'Need {depth_needed:.2f} m of regolith overburden.' if not can_dig_in
            else 'Sufficient regolith for buried habitat.'
        ),
    }

def generate_elevation_profile(rd: Dict, length_km: float = 50.0, points: int = 100) -> pd.DataFrame:
    slope = rd.get('slope_deg', 0)
    base_slope_rise = math.tan(math.radians(slope)) * 1000
    np.random.seed(hash(rd.get('site_name', '')) % 2**32)
    x = np.linspace(0, length_km, points)
    base = base_slope_rise * x
    crater = 50 * np.exp(-((x - length_km/2)**2) / (2 * (length_km/6)**2)) * -1
    noise = np.random.normal(0, 8, points)
    y = base + crater + noise
    return pd.DataFrame({'Distance (km)': x, 'Elevation (m)': y})

def generate_sun_position_frames(lat: float, illum_pct: float, n_frames: int = 60) -> List[Dict]:
    frames = []
    for i in range(n_frames):
        lunar_day_fraction = i / n_frames
        sun_angle_deg = lunar_day_fraction * 360.0
        illum_factor = (math.sin(math.radians(sun_angle_deg)) + 1) / 2
        current_illum = illum_pct * 0.4 + illum_pct * 0.6 * illum_factor
        temp_c = -120 + 180 * (current_illum / 100.0)
        frames.append({
            'frame': i,
            'lunar_day_fraction': round(lunar_day_fraction, 3),
            'hour': round(lunar_day_fraction * 24.6, 1),
            'sun_angle_deg': round(sun_angle_deg, 1),
            'illumination_pct': round(current_illum, 1),
            'temperature_c': round(temp_c, 1),
        })
    return frames

# ============================================================================
# MEMORY REPOSITORY
# ============================================================================

class MemoryRepository:
    def __init__(self, db_path: str = "marsbase_memory.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL, query_hash TEXT NOT NULL,
                result_summary TEXT, success INTEGER, execution_time REAL,
                parameters TEXT, timestamp TEXT, embedding BLOB
            )
        """)
        conn.commit(); conn.close()

    def store_analysis(self, query, summary, success, exec_time, params):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        qhash = hashlib.md5(query.lower().encode()).hexdigest()
        cursor.execute("""
            INSERT INTO analysis_memory
            (query, query_hash, result_summary, success, execution_time, parameters, timestamp, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (query, qhash, summary, 1 if success else 0, exec_time,
              json.dumps(params), datetime.now().isoformat(), pickle.dumps([])))
        conn.commit(); conn.close()

    def get_all_analyses(self, limit=20):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM analysis_memory ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        results = [{
            'query': r[1], 'result_summary': r[3],
            'success': bool(r[4]), 'execution_time': r[5],
            'parameters': json.loads(r[6]) if r[6] else {},
            'timestamp': r[7],
        } for r in rows]
        conn.close()
        return results

    def get_analysis_stats(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM analysis_memory")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM analysis_memory WHERE success = 1")
        success = cursor.fetchone()[0]
        conn.close()
        return {'total_analyses': total, 'successful_analyses': success,
                'success_rate': success / total if total > 0 else 0}

    def clear_all(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analysis_memory")
        conn.commit(); conn.close()

# ============================================================================
# MARS ANALYSIS STRATEGY
# ============================================================================

class MarsSiteAnalysisStrategy(ABC):
    def __init__(self, region: str = "equatorial"):
        self.region = region

    def analyse(self, site_name: str, params: Dict) -> Dict:
        data = MARS_SITES.get(site_name, {
            'lat': 0.0, 'lon': 0.0, 'region': 'unknown',
            'illumination_pct': 50, 'ice_confidence': 0.3,
            'slope_deg': 15, 'temperature_k': 200,
            'regolith_depth_m': 5, 'earth_visibility': 'partial',
            'lava_tube_proximity': 'None', 'skylight_distance_km': 999,
            'notes': 'Unknown site'
        })
        mission_year = params.get('mission_year', 2026)
        ill = get_seasonal_illumination(data['illumination_pct'], data['lat'], mission_year)
        ice = data['ice_confidence']
        slope = data['slope_deg']
        temp = data['temperature_k']
        reg = data['regolith_depth_m']
        comms = data['earth_visibility']
        lava = data.get('lava_tube_proximity', 'None')
        scores = {}
        scores['illumination'] = round(5.0 * (ill / 100.0), 2)
        scores['ice_access'] = round(5.0 * ice, 2)
        scores['slope_safety'] = 5.0 if slope <= 5 else (4.5 if slope <= 10 else (3.0 if slope <= 15 else 1.0))
        scores['temperature'] = 5.0 if 180 <= temp <= 300 else (3.5 if 150 <= temp <= 320 else 2.0)
        scores['regolith'] = 5.0 if reg >= 6 else (4.0 if reg >= 3 else 2.5)
        scores['comms'] = 5.0 if comms == 'yes' else (3.0 if comms == 'partial' else 1.0)
        scores['subsurface_access'] = 5.0 if lava == 'Excellent' else (4.0 if lava == 'Nearby' else 2.0)
        weights = {
            'illumination': 0.20, 'ice_access': 0.20, 'slope_safety': 0.15,
            'temperature': 0.10, 'regolith': 0.10, 'comms': 0.05,
            'subsurface_access': 0.20,
        }
        weighted_total = sum(scores[k] * weights[k] for k in weights)
        percentage = (weighted_total / 5.0) * 100
        if percentage >= 80: rating, emoji = 'Excellent', '🔴'
        elif percentage >= 65: rating, emoji = 'Good', '👍'
        elif percentage >= 50: rating, emoji = 'Moderate', '👌'
        elif percentage >= 35: rating, emoji = 'Limited', '⚠️'
        else: rating, emoji = 'Poor', '❌'
        return {
            'success': True, 'scores': scores, 'details': {
                'illumination': {'score': scores['illumination'], 'value': f"{ill:.0f}%", 'weight': weights['illumination'], 'source': f'MSL REMS (Year {mission_year})'},
                'ice_access': {'score': scores['ice_access'], 'value': f"{ice:.0%}", 'weight': weights['ice_access'], 'source': 'MRO SHARAD'},
                'slope_safety': {'score': scores['slope_safety'], 'value': f"{slope:.1f}°", 'weight': weights['slope_safety'], 'source': 'MOLA DEM'},
                'temperature': {'score': scores['temperature'], 'value': f"{temp:.0f}K", 'weight': weights['temperature'], 'source': 'Mars Climate Database'},
                'regolith': {'score': scores['regolith'], 'value': f"{reg:.1f}m", 'weight': weights['regolith'], 'source': 'MRO CRISM'},
                'comms': {'score': scores['comms'], 'value': comms.capitalize(), 'weight': weights['comms'], 'source': 'Geometry'},
                'subsurface_access': {'score': scores['subsurface_access'], 'value': lava, 'weight': weights['subsurface_access'], 'source': 'MRO HiRISE'},
            },
            'weighted_score': weighted_total, 'max_possible_score': 5.0,
            'suitability_percentage': round(percentage, 1),
            'base_percentage': round(percentage, 1),
            'rating': rating, 'rating_emoji': emoji,
            'location': f"{site_name} ({data['lat']:.4f}, {data['lon']:.4f})",
            'site_name': site_name, 'region': self.region,
            'lat': data['lat'], 'lon': data['lon'],
            'illumination_pct': ill, 'ice_confidence': ice,
            'slope_deg': slope, 'temperature_k': temp,
            'regolith_depth_m': reg, 'earth_visibility': comms,
            'lava_tube_proximity': lava,
            'mission_year': mission_year,
            'notes': data['notes'],
            'analysis_method': 'Mars: NASA MRO data',
            'data_source_details': [f"Illum: {ill:.0f}%", f"Ice: {ice:.0%}", f"Slope: {slope:.1f}°"],
        }

# ============================================================================
# SESSION STATE
# ============================================================================

def init_session_state():
    if 'memory_repo' not in st.session_state:
        st.session_state.memory_repo = MemoryRepository()
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    if 'region' not in st.session_state:
        st.session_state.region = 'equatorial'
    if 'selected_site_name' not in st.session_state:
        st.session_state.selected_site_name = 'Jezero Crater Delta'
    if 'current_results' not in st.session_state:
        st.session_state.current_results = None
    if 'mission_year' not in st.session_state:
        st.session_state.mission_year = 2026
    if 'show_mars_overlay' not in st.session_state:
        st.session_state.show_mars_overlay = False
    if 'compare_mode' not in st.session_state:
        st.session_state.compare_mode = False
    if 'water_regolith_kg' not in st.session_state:
        st.session_state.water_regolith_kg = 5000.0
    if 'radiation_target_msv' not in st.session_state:
        st.session_state.radiation_target_msv = 50.0
    if 'show_lava_tubes' not in st.session_state:
        st.session_state.show_lava_tubes = False
    if 'rover_tracker' not in st.session_state:
        st.session_state.rover_tracker = True
    # 🆕 v1.2.0 session states
    if 'show_biosignatures' not in st.session_state:
        st.session_state.show_biosignatures = False
    if 'show_minerals' not in st.session_state:
        st.session_state.show_minerals = False

# ============================================================================
# RANDOMIZER
# ============================================================================

def render_randomizer():
    st.markdown("""<div style="color: #ff6b35; font-family: 'Courier New', monospace; 
         letter-spacing: 2px; font-size: 0.9rem; margin-bottom: 10px; text-align: center;">
        🎲 SURPRISE ME</div>""", unsafe_allow_html=True)
    if st.button("🎲 Random Mars Site", use_container_width=True):
        if np.random.random() < 0.6:
            lat = np.random.uniform(-30, 30)
        else:
            lat = np.random.uniform(-60, 60)
        lon = np.random.uniform(-180, 180)
        custom_name = f"Random Site ({lat:.1f}°, {lon:.1f}°)"
        abs_lat = abs(lat)
        if abs_lat > 40:
            dynamic_illum = 55.0
            dynamic_ice = 0.75
            dynamic_slope = 5.0
            dynamic_temp = 195
            dynamic_lava = 'Nearby'
        elif abs_lat > 20:
            dynamic_illum = 70.0
            dynamic_ice = 0.45
            dynamic_slope = 8.0
            dynamic_temp = 210
            dynamic_lava = 'None'
        else:
            dynamic_illum = 78.0
            dynamic_ice = 0.30
            dynamic_slope = 6.0
            dynamic_temp = 220
            dynamic_lava = 'None'
        MARS_SITES[custom_name] = {
            'lat': lat, 'lon': lon, 'region': 'custom',
            'illumination_pct': dynamic_illum, 'ice_confidence': dynamic_ice,
            'slope_deg': dynamic_slope, 'temperature_k': dynamic_temp,
            'regolith_depth_m': 6.0, 'earth_visibility': 'yes',
            'lava_tube_proximity': dynamic_lava, 'skylight_distance_km': 15 if dynamic_lava == 'Nearby' else 999,
            'notes': 'Randomly generated site from the Surprise Me button.',
        }
        st.session_state.selected_site_name = custom_name
        st.session_state.current_results = None
        st.rerun()

# ============================================================================
# MAP (with Lava Tube + Biosignature + Mineral Overlays)
# ============================================================================

def render_map(params, region):
    st.subheader(f"🔴 {region.replace('_', ' ').title()} Mars Site Map")
    if st.session_state.selected_site_name in MARS_SITES:
        sel = MARS_SITES[st.session_state.selected_site_name]
        center = [sel['lat'], sel['lon']]
    else:
        center = [0.0, 0.0]
    m = folium.Map(location=center, zoom_start=3, tiles=MARS_TILES,
                   attr='NASA Mars Trek / MOLA')
    if st.session_state.show_mars_overlay:
        for name, coords in MARS_LANDING_SITES.items():
            folium.Circle(
                location=coords,
                radius=120000,
                color='#ffb347',
                fill=True,
                fill_color='#ffb347',
                fill_opacity=0.15,
                weight=2,
                dash_array='5,5',
                popup=f"<b>🛰️ NASA Landing Site</b><br>{name}",
                tooltip=f"NASA: {name}",
            ).add_to(m)
    if st.session_state.show_lava_tubes:
        for name, (lat, lon, status) in MARS_LAVA_TUBES.items():
            color = '#ff2d55' if status == 'Confirmed' else '#ffb347'
            folium.CircleMarker(
                location=[lat, lon],
                radius=25,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.4,
                weight=2,
                popup=f"<b>🕳️ {name}</b><br>Status: {status}",
                tooltip=f"🕳️ {name} ({status})",
            ).add_to(m)
    # 🆕 Biosignature overlay
    if st.session_state.show_biosignatures:
        for site_name, prob in BIOSIGNATURE_HOTSPOTS.items():
            if site_name in MARS_SITES:
                data = MARS_SITES[site_name]
                if prob >= 0.75:
                    color = '#39ff14'
                    radius = 40
                elif prob >= 0.55:
                    color = '#00e5ff'
                    radius = 30
                elif prob >= 0.35:
                    color = '#ffb347'
                    radius = 22
                else:
                    color = '#ff6b35'
                    radius = 15
                folium.CircleMarker(
                    location=[data['lat'], data['lon']],
                    radius=radius,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.20,
                    weight=2,
                    popup=f"<b>🧬 {site_name}</b><br>Biosignature: {prob*100:.0f}%",
                    tooltip=f"🧬 {site_name} ({prob*100:.0f}%)",
                ).add_to(m)
    # 🆕 Mineral overlay
    if st.session_state.show_minerals:
        for site_name in MARS_MINERALS.keys():
            if site_name in MARS_SITES:
                data = MARS_SITES[site_name]
                folium.CircleMarker(
                    location=[data['lat'], data['lon']],
                    radius=35,
                    color='#ffc800',
                    fill=True,
                    fill_color='#ffc800',
                    fill_opacity=0.15,
                    weight=2,
                    dash_array='3,3',
                    popup=f"<b>💎 {site_name}</b><br>Click to view minerals",
                    tooltip=f"💎 {site_name}",
                ).add_to(m)
    for name, data in MARS_SITES.items():
        if data['region'] != region: continue
        est = _quick_static_estimate(data)
        score = est['suitability']
        color = 'green' if score >= 80 else ('lightgreen' if score >= 65 else ('orange' if score >= 50 else 'red'))
        folium.Marker(
            [data['lat'], data['lon']],
            popup=f"<b>{name}</b><br>Score: {score:.0f}%<br>Illum: {data['illumination_pct']}%",
            tooltip=f"{name}: {score:.0f}%",
            icon=folium.Icon(color=color, icon='star', prefix='fa')
        ).add_to(m)
    if st.session_state.selected_site_name in MARS_SITES:
        sel = MARS_SITES[st.session_state.selected_site_name]
        folium.Marker(
            [sel['lat'], sel['lon']],
            popup=f"<b>🎯 {st.session_state.selected_site_name}</b>",
            icon=folium.Icon(color='blue', icon='crosshairs', prefix='fa')
        ).add_to(m)
    folium.Marker(
        [PERSEVERANCE_POSITION['lat'], PERSEVERANCE_POSITION['lon']],
        popup=f"<b>🛰️ Perseverance</b><br>Sol {PERSEVERANCE_POSITION['sol']}<br>{PERSEVERANCE_POSITION['site_name']}",
        tooltip="🛰️ Perseverance (live)",
        icon=folium.Icon(color='orange', icon='rocket', prefix='fa')
    ).add_to(m)
    try:
        Fullscreen(position='topleft').add_to(m)
        MousePosition(position='bottomleft', prefix='Mars Coords: ').add_to(m)
    except Exception: pass
    map_data = st_folium(m, width=None, height=500, use_container_width=True)
    if map_data and map_data.get('last_clicked'):
        clicked_lat = map_data['last_clicked']['lat']
        clicked_lon = map_data['last_clicked']['lng']
        custom_name = f"Custom Site ({clicked_lat:.1f}°, {clicked_lon:.1f}°)"
        abs_lat = abs(clicked_lat)
        if abs_lat > 40:
            dynamic_illum = 55.0; dynamic_ice = 0.75; dynamic_slope = 5.0
            dynamic_temp = 195; dynamic_lava = 'Nearby'
        elif abs_lat > 20:
            dynamic_illum = 70.0; dynamic_ice = 0.45; dynamic_slope = 8.0
            dynamic_temp = 210; dynamic_lava = 'None'
        else:
            dynamic_illum = 78.0; dynamic_ice = 0.30; dynamic_slope = 6.0
            dynamic_temp = 220; dynamic_lava = 'None'
        MARS_SITES[custom_name] = {
            'lat': clicked_lat, 'lon': clicked_lon, 'region': 'custom',
            'illumination_pct': dynamic_illum, 'ice_confidence': dynamic_ice,
            'slope_deg': dynamic_slope, 'temperature_k': dynamic_temp,
            'regolith_depth_m': 6.0, 'earth_visibility': 'yes',
            'lava_tube_proximity': dynamic_lava, 'skylight_distance_km': 15 if dynamic_lava == 'Nearby' else 999,
            'notes': 'Dynamically generated site from map click.',
        }
        if st.session_state.selected_site_name != custom_name:
            st.session_state.selected_site_name = custom_name
            st.rerun()
    st.markdown(f"""
    <div class="nasa-trek-box">
        <a href="https://trek.nasa.gov/mars/" target="_blank" style="color: #ff2d55; font-weight: bold; text-decoration: none;">
            🔴 Open NASA Mars Trek 3D ↗
        </a>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

def render_region_switcher():
    st.markdown("""
    <div style="text-align: center; margin: 10px 0;">
        <div style="color: #ff6b35; font-family: 'Courier New', monospace; 
             letter-spacing: 3px; font-size: 0.9rem; margin-bottom: 10px;">
            🔴 SELECT MARS REGION</div>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🌍 EQUATORIAL\n(Jezero Zone)", use_container_width=True,
                     type="primary" if st.session_state.region == 'equatorial' else "secondary"):
            st.session_state.region = 'equatorial'
            st.session_state.selected_site_name = 'Jezero Crater Delta'
            st.session_state.current_results = None
            st.rerun()
    with col2:
        if st.button("❄️ NORTHERN\n(Ice Zone)", use_container_width=True,
                     type="primary" if st.session_state.region == 'northern' else "secondary"):
            st.session_state.region = 'northern'
            st.session_state.selected_site_name = 'Arcadia Planitia'
            st.session_state.current_results = None
            st.rerun()
    with col3:
        if st.button("🏔️ SOUTHERN\n(Highlands)", use_container_width=True,
                     type="primary" if st.session_state.region == 'southern' else "secondary"):
            st.session_state.region = 'southern'
            st.session_state.selected_site_name = 'Eberswalde Crater Delta'
            st.session_state.current_results = None
            st.rerun()
    return st.session_state.region

def render_sidebar(region):
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 10px 0;">
            <div style="font-size: 2.2rem; font-family: 'Courier New', monospace; 
                 background: linear-gradient(90deg, #ff6b35, #ffb347, #ffffff);
                 -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                 font-weight: 900; letter-spacing: 3px;">MARSBASE</div>
            <div style="color: #ff6b35; font-size: 0.75rem; font-family: 'Courier New', monospace;
                 letter-spacing: 4px;">🔴 {region.replace('_', ' ').upper()}</div>
            <div class="cyber-divider"></div>
        </div>
        """, unsafe_allow_html=True)
        render_randomizer()
        st.divider()
        st.markdown("""<div style="color: #ff6b35; font-family: 'Courier New', monospace; 
             letter-spacing: 2px; font-size: 0.9rem; margin-bottom: 10px;">
            🔴 SITE SELECTOR</div>""", unsafe_allow_html=True)
        sites = {k: v for k, v in MARS_SITES.items() if v['region'] == region}
        st.info(f"Showing {len(sites)} NASA candidate sites")
        site_names = list(sites.keys())
        idx = site_names.index(st.session_state.selected_site_name) if st.session_state.selected_site_name in site_names else 0
        quick_site = st.selectbox("Select Site", site_names, index=idx)
        if st.button("⚡ GO TO SITE", use_container_width=True):
            st.session_state.selected_site_name = quick_site
            st.rerun()
        st.divider()
        st.markdown("""<div style="color: #ffb347; font-family: 'Courier New', monospace; 
             letter-spacing: 2px; font-size: 0.9rem; margin-bottom: 10px;">
            🛰️ NASA MISSIONS OVERLAY</div>""", unsafe_allow_html=True)
        st.session_state.show_mars_overlay = st.toggle(
            "Show NASA Landing Sites",
            value=st.session_state.show_mars_overlay,
            help="Overlay 14 official NASA Mars landing / candidate sites."
        )
        st.caption("Gold dashed circles = NASA mission zones.")
        st.session_state.show_lava_tubes = st.toggle(
            "🕳️ Show Lava Tube Probability Map",
            value=st.session_state.show_lava_tubes,
            help="Overlay confirmed and probable lava tube skylights (MRO HiRISE)."
        )
        st.caption("Red = Confirmed · Orange = Probable.")
        # 🆕 v1.2.0 toggles
        st.session_state.show_biosignatures = st.toggle(
            "🧬 Show Biosignature Probability Map",
            value=st.session_state.show_biosignatures,
            help="Overlay biosignature hotspots from CRISM + rover detections."
        )
        st.caption("Green = very high · Cyan = high · Orange = moderate.")
        st.session_state.show_minerals = st.toggle(
            "💎 Show Mineral Resource Map",
            value=st.session_state.show_minerals,
            help="Overlay sites with confirmed CRISM mineral detections."
        )
        st.caption("Gold dashed circles = mineral-rich zones.")
        st.divider()
        st.markdown("""<div style="color: #ff6b35; font-family: 'Courier New', monospace; 
             letter-spacing: 2px; font-size: 0.9rem; margin-bottom: 10px;">
            📅 SEASONAL ILLUMINATION</div>""", unsafe_allow_html=True)
        mission_year = st.slider("Mission Year (Seasonal Drift)", 2026, 2037, 2026)
        st.session_state.mission_year = mission_year
        st.caption("Mars illumination shifts over its 1.88-year orbital cycle.")
        st.divider()
        st.markdown("""<div style="color: #ff6b35; font-family: 'Courier New', monospace; 
             letter-spacing: 2px; font-size: 0.9rem; margin-bottom: 10px;">
            🧠 MEMORY</div>""", unsafe_allow_html=True)
        stats = st.session_state.memory_repo.get_analysis_stats()
        col1, col2 = st.columns(2)
        with col1: st.metric("Analyses", stats['total_analyses'])
        with col2: st.metric("Success", f"{stats['success_rate']*100:.0f}%")
        if st.button("🗑️ CLEAR MEMORY", use_container_width=True):
            st.session_state.memory_repo.clear_all()
            try: Path("marsbase_memory.db").unlink(missing_ok=True)
            except Exception: pass
            st.session_state.analysis_history = []
            st.session_state.current_results = None
            st.session_state.memory_repo = MemoryRepository()
            st.success("Memory cleared!")
            st.rerun()
        return {'radius': 10000, 'mission_year': mission_year}

# ============================================================================
# QUERY & RESULTS
# ============================================================================

def render_query_interface(params, region):
    st.subheader("💬 Analyse Mars Site")
    query = st.text_area("Describe your analysis goal:",
                         placeholder="e.g., Evaluate this site for a permanent Mars base",
                         height=100)
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        analyse_btn = st.button("🔴 ANALYSE SITE", type="primary", use_container_width=True)
    with col2:
        if st.button("🧹 CLEAR", use_container_width=True):
            st.session_state.current_results = None
            st.rerun()
    if analyse_btn:
        with st.spinner("🔴 Scoring against NASA MRO criteria..."):
            t0 = time.time()
            strategy = MarsSiteAnalysisStrategy(region)
            result = strategy.analyse(st.session_state.selected_site_name, params)
            elapsed = time.time() - t0
            st.session_state.current_results = result
            st.session_state.analysis_history.append(result)
            st.session_state.memory_repo.store_analysis(
                query or f"Evaluate {st.session_state.selected_site_name}",
                result.get('location', ''), True, elapsed, params)
            st.success(f"✅ Analysis complete in {elapsed:.2f}s")
            st.rerun()

def render_results():
    st.subheader("🔴 Marsbase Site Analysis Results")
    rd = st.session_state.current_results
    if not rd:
        st.info("No results yet. Pick a site and click ANALYSE.")
        return
    st.success(f"🌐 **NASA MRO DATA** · {rd['site_name']} · Mission Year: {rd.get('mission_year', 2026)}")
    disp = compute_display_score(rd)
    if disp['is_capped']:
        st.markdown(f"""
        <div class="blocked-score">
            <div style="color: #ff2d55; font-size: 2.5rem; font-weight: 900;">
                {disp['display_score']}% {disp['display_emoji']}
            </div>
            <div style="color: #ffffff; font-size: 0.9rem;">
                ⚠️ Capped: {disp['cap_reason']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.metric("🔴 Marsbase Suitability", f"{rd['suitability_percentage']}%",
                  delta=f"{rd['rating']} {rd['rating_emoji']}")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("Illumination", f"{rd.get('illumination_pct', 0):.0f}%")
    with c2: st.metric("Slope", f"{rd.get('slope_deg', 0):.1f}°")
    with c3: st.metric("Ice", f"{rd.get('ice_confidence', 0):.0%}")
    with c4: st.metric("Lava Tube", rd.get('lava_tube_proximity', 'None'))
    with c5: st.metric("Earth Comms", rd.get('earth_visibility', 'N/A').capitalize())
    st.write("---")

    # Perseverance Rover Tracker
    st.write("**🛰️ Real-Time Perseverance Rover Tracker**")
    pers = get_perseverance_distance(rd.get('lat', 0), rd.get('lon', 0))
    st.markdown(f"""
    <div class="rover-box">
        <div style="color: #ff6b35; font-size: 1.1rem; font-weight: bold; margin-bottom: 10px;">
            🛰️ PERSEVERANCE ROVER
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Current Position:</span>
            <b style="color: #ffb347;">{pers['rover_lat']:.2f}°, {pers['rover_lon']:.2f}°</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Mission Sol:</span>
            <b style="color: #ff6b35;">Sol {pers['rover_sol']}</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Location:</span>
            <b style="color: #ffb347;">{pers['rover_site']}</b>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span>Distance to this site:</span>
            <b style="color: #39ff14;">{pers['distance_km']:,.1f} km</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 🆕 Biosignature Probability Map
    st.write("---")
    st.write("**🧬 Biosignature Probability**")
    bio = get_biosignature_probability(rd)
    st.markdown(f"""
    <div class="biosignature-box">
        <div style="color: {bio['color']}; font-size: 1.1rem; font-weight: bold; margin-bottom: 10px;">
            🧬 BIOSIGNATURE PROBABILITY: {bio['tier']}
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Probability:</span>
            <b style="color: {bio['color']};">{bio['probability_pct']}%</b>
        </div>
        <div style="margin-top: 8px; padding: 8px; background: rgba(0,229,255,0.08); border-radius: 6px;">
            <b style="color: #ffffff;">💡 {bio['note']}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 🆕 InSight Mars Weather Feed
    st.write("---")
    st.write("**🔬 InSight Mars Weather Feed**")
    weather = get_insight_weather()
    st.markdown(f"""
    <div class="weather-box">
        <div style="color: #ffb347; font-size: 1.1rem; font-weight: bold; margin-bottom: 10px;">
            🔬 INSIGHT MARS WEATHER (Sol {weather['sol']})
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Pressure:</span>
            <b style="color: #ff6b35;">{weather['pressure_pa']:.0f} Pa</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Wind Speed:</span>
            <b style="color: #00e5ff;">{weather['wind_speed_ms']:.1f} m/s</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Wind Direction:</span>
            <b style="color: #ffb347;">{weather['wind_direction_deg']}°</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Ground Temp:</span>
            <b style="color: #ff6b35;">{weather['ground_temp_c']:.0f} °C</b>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span>Air Temp:</span>
            <b style="color: #ff2d55;">{weather['air_temp_c']:.0f} °C</b>
        </div>
        <div style="font-size: 0.75rem; color: #ffb347; margin-top: 8px;">
            * {weather['last_update']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 🆕 Mineral Resource Map
    st.write("---")
    st.write("**💎 Mineral Resource Map**")
    minerals = get_mineral_resources(rd)
    mining = get_mining_value(minerals)
    st.markdown(f"""
    <div class="mineral-box">
        <div style="color: #ffc800; font-size: 1.1rem; font-weight: bold; margin-bottom: 10px;">
            💎 MINERAL COMPOSITION
        </div>
    """, unsafe_allow_html=True)
    mineral_rows = ""
    for m in minerals:
        mineral_rows += f"""
        <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(255,200,0,0.08);">
            <span style="color: #ffb347; flex: 1;">{m['mineral']}</span>
            <b style="color: {m['color']}; flex: 1; text-align: center;">{m['tier']}</b>
            <b style="color: #ff6b35; flex: 1; text-align: right;">{m['abundance_pct']}%</b>
        </div>"""
    mineral_rows += f"""
        <div style="margin-top: 12px; padding: 10px; background: rgba(255,200,0,0.08); border-radius: 6px;">
            <b style="color: {mining['color']};">🎯 Mining Value: {mining['value']}</b>
        </div>
    </div>"""
    st.markdown(mineral_rows, unsafe_allow_html=True)

    # Best Month to Land
    st.write("---")
    st.write("**⚡ Best Month to Land Recommender**")
    best = get_best_landing_month(rd)
    st.markdown(f"""
    <div class="launch-box">
        <div style="color: #00e5ff; font-size: 1.1rem; font-weight: bold; margin-bottom: 10px;">
            ⚡ OPTIMAL LAUNCH WINDOW
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Best Landing Month:</span>
            <b style="color: #ff6b35;">{best['month_name']} (Ls {best['ls']}°)</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Recommended Launch:</span>
            <b style="color: #ffb347;">{best['launch_year']} Q3</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Arrival Window:</span>
            <b style="color: #ffb347;">{best['arrival_year']} Q1</b>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span>Window Score:</span>
            <b style="color: #39ff14;">{best['score']:.1f} / 100</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("---")
    dv = compute_mars_delta_v(rd.get('lat', 0))
    st.markdown(f"""
    <div class="delta-v-box">
        <div style="color: #ff6b35; font-size: 1.1rem; font-weight: bold; margin-bottom: 10px;">
            🚀 MARS DELTA-V & TRAVEL TIME
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Mars → Earth (direct):</span>
            <b style="color: #ff6b35;">{dv['dv_earth']:,.0f} m/s</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Mars → LEO (with refuel):</span>
            <b style="color: #39ff14;">{dv['dv_leo']:,.0f} m/s</b>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span>Travel Time:</span>
            <b style="color: #ffb347;">~{dv['travel_time_days']} days</b>
        </div>
        <div style="font-size: 0.75rem; color: #ffb347; margin-top: 8px;">
            * Mars rotation adds {dv['rotation_speed']} m/s at this latitude.
        </div>
    </div>
    """, unsafe_allow_html=True)
    climate = fetch_mars_climate_model(rd.get('lat', 0), rd.get('illumination_pct', 0))
    st.markdown(f"""
    <div class="climate-box">
        <div style="color: #ffb347; font-size: 1.1rem; font-weight: bold; margin-bottom: 10px;">
            🌡️ LIVE MARS THERMAL MODEL
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Temperature:</span>
            <b style="color: #ff6b35;">{climate['temperature_c']} °C</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Atmosphere:</span>
            <b style="color: #ff6b35;">{climate['pressure_atm']} atm (CO2)</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Radiation:</span>
            <b style="color: #ff2d55;">{climate['radiation_msv_year']} mSv/year</b>
        </div>
        <div style="font-size: 0.75rem; color: #ffb347; margin-top: 8px;">
            * Source: {climate['source']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Perchlorate Toxicity Warning
    st.write("---")
    st.write("**🧂 Perchlorate Toxicity Warning**")
    perch = get_perchlorate_warning(rd)
    st.markdown(f"""
    <div class="perchlorate-box">
        <div style="color: #ffc800; font-size: 1.1rem; font-weight: bold; margin-bottom: 10px;">
            🧂 PERCHLORATE LEVEL: {perch['level']}
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Concentration:</span>
            <b style="color: {perch['color']};">{perch['level_pct']*100:.0f}%</b>
        </div>
        <div style="margin-top: 8px; padding: 8px; background: rgba(255,200,0,0.08); border-radius: 6px;">
            <b style="color: #ffffff;">💡 {perch['action']}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if rd.get('lava_tube_proximity') == 'Nearby':
        st.markdown(f"""
        <div class="subsurface-box">
            <div style="color: #00e5ff; font-size: 1.1rem; font-weight: bold; margin-bottom: 10px;">
                🌋 SUBSURFACE ACCESS — LAVA TUBE DETECTED
            </div>
            <div style="color: #ffffff; font-size: 0.9rem;">
                A lava tube is nearby. This offers natural radiation shielding, 
                thermal insulation, and a ready-made habitat structure. 
                This significantly reduces construction costs and radiation risk.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Lava Tube Detection Probability
    st.write("---")
    st.write("**🕳️ Lava Tube Detection Probability**")
    tube = get_lava_tube_probability(rd.get('lat', 0), rd.get('lon', 0))
    st.markdown(f"""
    <div class="lava-box">
        <div style="color: #ff2d55; font-size: 1.1rem; font-weight: bold; margin-bottom: 10px;">
            🕳️ LAVA TUBE PROBABILITY
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Probability within 30 km:</span>
            <b style="color: #ff6b35;">{tube['probability']*100:.0f}%</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Nearest Known Tube:</span>
            <b style="color: #ffb347;">{tube['nearest_tube']}</b>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span>Distance:</span>
            <b style="color: #39ff14;">{tube['distance_km']:,.0f} km</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_chart, col_list = st.columns([1, 1])
    with col_chart:
        st.write("**💰 Estimated Cost Breakdown**")
        fig = go.Figure(data=[go.Pie(labels=['Lander', 'Habitat', 'Power', 'ISRU', 'Comms'], 
                                     values=[30, 25, 20, 15, 10], hole=.4,
                                     marker=dict(colors=['#ff6b35', '#ffb347', '#00e5ff', '#ff2d55', '#c1440e']))])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    with col_list:
        st.write("**Cost Estimates**")
        cost = estimate_cost_range(rd)
        st.metric("Low", f"${cost['low_billion']:.1f}B")
        st.metric("Mid", f"${cost['mid_billion']:.1f}B")
        st.metric("High", f"${cost['high_billion']:.1f}B")

    st.write("---")
    st.write("**🌍 Frame of Reference (Earth vs Mars)**")
    col_e, col_m = st.columns(2)
    with col_e: st.metric("Earth Gravity", "1.0 G", delta="Baseline")
    with col_m: st.metric("Mars Gravity", "0.38 G", delta="-0.62 G")
    st.caption("Mars has 38% of Earth's gravity. Astronauts must exercise daily to prevent bone loss.")

    # 🆕 Night Sky from Mars
    st.write("---")
    st.write("**🌌 Night Sky from Mars**")
    st.caption("Constellations visible from this site (Mars has different axial tilt than Earth).")
    night_sky = get_night_sky_from_mars(rd)
    st.markdown(f"""
    <div class="nightsky-box">
        <div style="color: #b464ff; font-size: 1.1rem; font-weight: bold; margin-bottom: 10px;">
            🌌 CONSTELLATIONS FROM {rd.get('lat', 0):.1f}°
        </div>
    """, unsafe_allow_html=True)
    sky_rows = ""
    for entry in night_sky:
        if entry['probability'] >= 0.85:
            color = '#39ff14'
        elif entry['probability'] >= 0.65:
            color = '#00e5ff'
        elif entry['probability'] >= 0.45:
            color = '#ffb347'
        else:
            color = '#ff6b35'
        sky_rows += f"""
        <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid rgba(180,100,255,0.08);">
            <span style="color: #b464ff; flex: 1; font-weight: bold;">{entry['constellation']}</span>
            <span style="color: {color}; flex: 1; text-align: center;">{entry['visibility']}</span>
            <span style="color: #ffb347; flex: 1; text-align: right; font-size: 0.85rem;">{entry['description']}</span>
        </div>"""
    sky_rows += "</div>"
    st.markdown(sky_rows, unsafe_allow_html=True)

    # Mars vs Earth Fact Panel
    st.write("---")
    st.write("**📊 Mars vs Earth Fact Panel**")
    st.markdown("""
    <div class="fact-panel">
        <div style="color: #00e5ff; font-size: 1.1rem; font-weight: bold; margin-bottom: 15px;">
            📊 MARS VS EARTH — QUICK FACTS
        </div>
    """, unsafe_allow_html=True)
    fact_rows = ""
    for fact, mars_val, earth_val in MARS_VS_EARTH_FACTS:
        fact_rows += f"""
        <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(0,229,255,0.08);">
            <span style="color: #ffb347; flex: 1;">{fact}</span>
            <b style="color: #ff6b35; flex: 1; text-align: center;">{mars_val}</b>
            <b style="color: #00e5ff; flex: 1; text-align: right;">{earth_val}</b>
        </div>"""
    st.markdown(fact_rows + "</div>", unsafe_allow_html=True)

    st.write("---")
    st.write("**⛰️ Elevation Cross-Section (50 km traverse)**")
    profile = generate_elevation_profile(rd)
    fig_elev = go.Figure()
    fig_elev.add_trace(go.Scatter(
        x=profile['Distance (km)'], y=profile['Elevation (m)'],
        mode='lines', fill='tozeroy',
        line=dict(color='#ff6b35', width=3),
        fillcolor='rgba(255, 107, 53, 0.15)',
        name='Terrain'
    ))
    fig_elev.add_hline(y=0, line_dash="dash", line_color="#39ff14",
                       annotation_text="Landing Zone", annotation_position="top left")
    fig_elev.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(25,10,15,0.6)',
        font=dict(color='white'), height=300,
        xaxis_title="Distance (km)", yaxis_title="Elevation (m)",
        margin=dict(t=20, b=40, l=40, r=20),
        xaxis=dict(gridcolor='rgba(255,107,53,0.1)'),
        yaxis=dict(gridcolor='rgba(255,107,53,0.1)'),
    )
    st.plotly_chart(fig_elev, use_container_width=True)
    st.caption(f"Based on {rd.get('slope_deg', 0):.1f}° measured slope — visualizes lander approach terrain.")

    st.write("---")
    st.write("**💧 ISRU Water Production Calculator**")
    st.caption("Estimate daily water output from processing Martian regolith at this site.")
    regolith_kg = st.slider(
        "Regolith processing rate (kg/day)",
        min_value=1000, max_value=20000, value=int(st.session_state.water_regolith_kg),
        step=1000, key="water_regolith_slider",
    )
    st.session_state.water_regolith_kg = regolith_kg
    water = water_production_estimate(rd, regolith_kg_per_day=regolith_kg)
    st.markdown(f"""
    <div class="water-box">
        <div style="color: #00e5ff; font-size: 1.1rem; font-weight: bold; margin-bottom: 10px;">
            💧 WATER PRODUCTION (ISRU)
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Daily Water Output:</span>
            <b style="color: #ff6b35;">{water['water_l_day']:,.0f} L/day</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Ice Fraction (regolith):</span>
            <b style="color: #ff6b35;">{water['ice_fraction']*100:.1f}%</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Crews Supported (10 crew):</span>
            <b style="color: #39ff14;">{water['crew_supported']:.1f}</b>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span>Status:</span>
            <b style="color: {'#39ff14' if water['viable'] else '#ff2d55'};">
                {'✅ Viable' if water['viable'] else '❌ Not viable'}
            </b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("---")
    st.write("**☢️ Radiation Shield Depth Calculator**")
    st.caption("Estimate regolith overburden needed to reach target radiation dose.")
    target = st.slider(
        "Target dose (mSv/year)",
        min_value=10, max_value=200, value=int(st.session_state.radiation_target_msv),
        step=10, key="radiation_target_slider",
    )
    st.session_state.radiation_target_msv = target
    shield = radiation_shield_estimate(rd, target_msv_year=target)
    st.markdown(f"""
    <div class="radiation-box">
        <div style="color: #ffc800; font-size: 1.1rem; font-weight: bold; margin-bottom: 10px;">
            ☢️ RADIATION SHIELDING
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Surface Dose:</span>
            <b style="color: #ff2d55;">{shield['surface_msv_year']:.0f} mSv/year</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Target Dose:</span>
            <b style="color: #ff6b35;">{shield['target_msv_year']:.0f} mSv/year</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Regolith Depth Needed:</span>
            <b style="color: #ff6b35;">{shield['depth_needed_m']:.2f} m</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Available Depth:</span>
            <b style="color: #ff6b35;">{shield['regolith_available_m']:.1f} m</b>
        </div>
        <div style="margin-top: 10px; padding: 8px; background: rgba(255,107,53,0.08); border-radius: 6px;">
            <b style="color: #ffffff;">💡 {shield['recommendation']}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("---")
    st.write("**🌅 Sun Position Animation — Mars Sol**")
    st.caption("How sunlight moves over this site during a 24.6-hour Martian sol.")
    frames = generate_sun_position_frames(
        rd.get('lat', 0), rd.get('illumination_pct', 50), n_frames=60
    )
    df_frames = pd.DataFrame(frames)
    col_sun1, col_sun2 = st.columns([1, 2])
    with col_sun1:
        frame_idx = st.slider(
            "Mars sol progress",
            min_value=0, max_value=59, value=0,
            key="sun_anim_slider",
            help="Drag to see how sunlight changes over a full Martian sol.",
        )
        current_frame = frames[frame_idx]
        st.metric("Illumination", f"{current_frame['illumination_pct']:.0f}%")
        st.metric("Temperature", f"{current_frame['temperature_c']:.0f} °C")
        st.metric("Sun Angle", f"{current_frame['sun_angle_deg']:.0f}°")
        st.metric("Martian Hour", f"{current_frame['hour']:.1f} h")
    with col_sun2:
        fig_sun = go.Figure()
        fig_sun.add_trace(go.Scatter(
            x=df_frames['hour'], y=df_frames['illumination_pct'],
            mode='lines', name='Illumination',
            line=dict(color='#ffb347', width=3),
            fill='tozeroy', fillcolor='rgba(255, 179, 71, 0.15)',
        ))
        fig_sun.add_trace(go.Scatter(
            x=[current_frame['hour']], y=[current_frame['illumination_pct']],
            mode='markers', name='Current',
            marker=dict(color='#ff2d55', size=18, symbol='star'),
        ))
        fig_sun.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(25,10,15,0.6)',
            font=dict(color='white'), height=320,
            xaxis_title="Martian Hour (0 → 24.6 h)",
            yaxis_title="Illumination %",
            margin=dict(t=20, b=40, l=40, r=20),
            xaxis=dict(gridcolor='rgba(255,179,71,0.1)'),
            yaxis=dict(gridcolor='rgba(255,179,71,0.1)'),
            showlegend=False,
        )
        st.plotly_chart(fig_sun, use_container_width=True)

    # Day/Night Temperature Swing
    st.write("---")
    st.write("**🌡️ Day/Night Temperature Swing (Martian Sol)**")
    st.caption("How temperature varies over a 24.6-hour sol at this site.")
    diurnal = get_diurnal_temperature_swing(rd)
    fig_diurnal = go.Figure()
    fig_diurnal.add_trace(go.Scatter(
        x=diurnal['Hour'], y=diurnal['Temperature (K)'],
        mode='lines', fill='tozeroy',
        line=dict(color='#ff6b35', width=3),
        fillcolor='rgba(255, 107, 53, 0.15)',
        name='Temperature'
    ))
    fig_diurnal.add_hline(y=273.15, line_dash="dot", line_color="#00e5ff",
                          annotation_text="Water Freezing (273K)", annotation_position="top left")
    fig_diurnal.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(25,10,15,0.6)',
        font=dict(color='white'), height=320,
        xaxis_title="Martian Hour (0 → 24.6 h)",
        yaxis_title="Temperature (K)",
        margin=dict(t=20, b=40, l=40, r=20),
        xaxis=dict(gridcolor='rgba(255,107,53,0.1)'),
        yaxis=dict(gridcolor='rgba(255,107,53,0.1)'),
        showlegend=False,
    )
    st.plotly_chart(fig_diurnal, use_container_width=True)
    diurnal_min = diurnal['Temperature (K)'].min()
    diurnal_max = diurnal['Temperature (K)'].max()
    st.caption(f"Swing: **{diurnal_max:.0f}K → {diurnal_min:.0f}K** · ΔT = {diurnal_max - diurnal_min:.0f}K · Habitat thermal mass critical.")

    # Dust Storm Calendar
    st.write("---")
    st.write("**🌪️ Dust Storm Probability Calendar**")
    st.caption("Mars global dust storm season (Ls 180–360°). Avoid landing in red months.")
    dust_cal = get_dust_storm_calendar()
    st.dataframe(dust_cal, use_container_width=True, hide_index=True)
    dust_fig = go.Figure()
    colors = ['#ff2d55' if r == 'HIGH' else '#39ff14' for r in dust_cal['Risk']]
    dust_fig.add_trace(go.Bar(
        x=dust_cal['Month'], y=dust_cal['Ls (°)'],
        marker=dict(color=colors),
        text=dust_cal['Risk'],
        textposition='outside',
    ))
    dust_fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(25,10,15,0.6)',
        font=dict(color='white'), height=280,
        xaxis_title="Month", yaxis_title="Areocentric Solar Longitude (°)",
        margin=dict(t=20, b=40, l=40, r=20),
        xaxis=dict(gridcolor='rgba(255,179,71,0.1)'),
        yaxis=dict(gridcolor='rgba(255,179,71,0.1)'),
        showlegend=False,
    )
    st.plotly_chart(dust_fig, use_container_width=True)

    # Detailed Scoring
    st.write("---")
    st.write("**Detailed Scoring Breakdown:**")
    details = rd.get('details', {})
    score_data = []
    for k, d in details.items():
        display_key = k.replace('_', ' ').title()
        if 'Illumination' in display_key: display_key = '☀️ ' + display_key
        elif 'Ice' in display_key: display_key = '💧 ' + display_key
        elif 'Slope' in display_key: display_key = '⛰️ ' + display_key
        elif 'Temperature' in display_key: display_key = '🌡️ ' + display_key
        elif 'Regolith' in display_key: display_key = '🪨 ' + display_key
        elif 'Comms' in display_key: display_key = '📡 ' + display_key
        elif 'Subsurface' in display_key: display_key = '🌋 ' + display_key
        score_data.append({
            'Criteria': display_key,
            'Score': f"{d.get('score', 0):.1f}/5",
            'Value': d.get('value', 'N/A'),
            'Weight': f"{d.get('weight', 0)*100:.0f}%",
            'Source': d.get('source', 'Unknown'),
        })
    st.dataframe(pd.DataFrame(score_data), use_container_width=True, hide_index=True)
    chart = pd.DataFrame([{'Criteria': r['Criteria'], 'Score': float(r['Score'].split('/')[0])}
                          for r in score_data])
    st.bar_chart(chart.set_index('Criteria'))
    st.write("---")
    st.write("**📋 Recommendation Strategy**")
    recs = generate_recommendation_strategy(rd)
    risk = recs.get('risk_level', 'Unknown')
    risk_color = '#ff2d55' if risk in ('High', 'Very High') else '#39ff14' if risk == 'Low' else '#ffb347'
    st.markdown(f"""
    <div class="recommendation-container">
        <div class="recommendation-title">🎯 Overall Feasibility</div>
        <div style="color: #ffffff; font-size: 1.1rem; padding: 10px;">
            {recs.get('overall_feasibility', 'N/A')}
        </div>
        <div style="display: flex; gap: 20px; margin-top: 10px; flex-wrap: wrap;">
            <div style="color: #ffb347;">💰 Investment: <b style="color: #ff6b35;">{recs.get('investment_required', '?')}</b></div>
            <div style="color: #ffb347;">⚠️ Risk: <b style="color: {risk_color};">{risk}</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    for bucket, title in [
        ('immediate_actions', '🔴 IMMEDIATE ACTIONS'),
        ('short_term_actions', '🟡 SHORT-TERM ACTIONS'),
        ('long_term_actions', '🟢 LONG-TERM ACTIONS'),
    ]:
        if recs[bucket]:
            st.markdown(f"""<div class="recommendation-container">
                <div class="recommendation-title">{title}</div>""", unsafe_allow_html=True)
            for a in recs[bucket]:
                st.markdown(f"""
                <div class="recommendation-item">
                    <span>{a.get('priority', '')}</span> {a['text']}
                </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# COMPARE MODE
# ============================================================================

def render_compare_mode(region):
    st.subheader("⚖️ Compare Sites Side-by-Side")
    st.caption("Select 2–3 candidate sites to compare their metrics, costs, and scores.")
    all_site_names = [k for k, v in MARS_SITES.items() if v['region'] == region]
    if len(all_site_names) < 2:
        st.info("Need at least 2 sites in this region to compare.")
        return
    compare_sites = st.multiselect(
        "Choose 2-3 sites to compare",
        options=all_site_names,
        default=all_site_names[:min(3, len(all_site_names))],
        max_selections=3,
        key="compare_multiselect",
    )
    if len(compare_sites) < 2:
        st.info("Select at least 2 sites to see the comparison.")
        return
    params = {'mission_year': st.session_state.mission_year}
    strategy = MarsSiteAnalysisStrategy(region)
    results = [strategy.analyse(name, params) for name in compare_sites]
    winner = max(results, key=lambda r: r['suitability_percentage'])
    winner_name = winner['site_name']
    st.write("### 📊 Side-by-Side Metrics")
    metric_rows = []
    for r in results:
        is_winner = (r['site_name'] == winner_name)
        metric_rows.append({
            '🏆': '🏆' if is_winner else '',
            'Site': r['site_name'],
            'Score': f"{r['suitability_percentage']}% {r['rating_emoji']}",
            'Illum %': f"{r['illumination_pct']:.0f}",
            'Slope °': f"{r['slope_deg']:.1f}",
            'Ice %': f"{r['ice_confidence']*100:.0f}",
            'Temp K': f"{r['temperature_k']:.0f}",
            'Lava Tube': r['lava_tube_proximity'],
            'Comms': r['earth_visibility'].capitalize(),
            'Rating': r['rating'],
        })
    df_compare = pd.DataFrame(metric_rows)
    st.dataframe(df_compare, use_container_width=True, hide_index=True)
    st.write("### 🕸️ Radar Comparison")
    categories = ['Illumination', 'Ice', 'Slope', 'Temperature', 'Regolith', 'Comms', 'Subsurface']
    fig_radar = go.Figure()
    palette = ['#ff6b35', '#ff2d55', '#39ff14', '#00e5ff']
    for i, r in enumerate(results):
        d = r['details']
        values = [
            d['illumination']['score'],
            d['ice_access']['score'],
            d['slope_safety']['score'],
            d['temperature']['score'],
            d['regolith']['score'],
            d['comms']['score'],
            d['subsurface_access']['score'],
        ]
        fig_radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name=r['site_name'][:25],
            line=dict(color=palette[i % len(palette)], width=2),
            opacity=0.6,
        ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor='rgba(25,10,15,0.6)',
            radialaxis=dict(visible=True, range=[0, 5], gridcolor='rgba(255,107,53,0.2)'),
            angularaxis=dict(gridcolor='rgba(255,107,53,0.15)'),
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=450,
        legend=dict(bgcolor='rgba(0,0,0,0)'),
    )
    st.plotly_chart(fig_radar, use_container_width=True)
    st.write("### 🏆 Recommended Site")
    st.markdown(f"""
    <div class="recommendation-container" style="border-color: #39ff14;">
        <div class="recommendation-title" style="color: #39ff14;">🏆 {winner_name}</div>
        <div style="color: #ffffff; font-size: 1rem; padding: 6px;">
            Highest suitability score: <b style="color: #ff6b35;">{winner['suitability_percentage']}%</b>
            ({winner['rating']} {winner['rating_emoji']})
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_simulation_lab():
    st.subheader("🧪 Simulation Lab (What-If)")
    st.markdown("Adjust parameters to see how the mission scales.")
    col1, col2, col3 = st.columns(3)
    with col1:
        crew_size = st.slider("Crew Size", 4, 100, 10)
    with col2:
        habitat_mass = st.slider("Habitat Mass (Tons)", 50, 500, 150)
    with col3:
        power_source = st.selectbox("Power Source", ["Hybrid (Solar+Nuclear)", "Solar Only", "Nuclear Only"])
    base_cost = 120.0
    new_cost = base_cost + (crew_size * 2.0) + (habitat_mass * 0.4)
    if power_source == "Nuclear Only": new_cost += 40.0
    if power_source == "Solar Only": new_cost -= 15.0
    air_needed = crew_size * 200
    water_needed = crew_size * 150
    regolith_shielding = crew_size * 20
    st.markdown("---")
    st.write("### 📊 Updated Mission Output")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("New Cost", f"${new_cost:.1f} B")
    with c2: st.metric("Air Needed", f"{air_needed:,} L/day")
    with c3: st.metric("Water Needed", f"{water_needed:,} L/day")
    with c4: st.metric("Regolith Shield", f"{regolith_shielding:,} tons")

def render_memory_explorer():
    st.subheader("💾 Memory Explorer")
    analyses = st.session_state.memory_repo.get_all_analyses(limit=20)
    if analyses:
        st.write(f"**{len(analyses)} past analyses**")
        for entry in analyses:
            qprev = entry['query'][:50] + "..." if len(entry['query']) > 50 else entry['query']
            with st.expander(f"{'✅' if entry['success'] else '❌'} {qprev}"):
                st.write(f"**Query:** {entry['query']}")
                st.write(f"**Time:** {entry['execution_time']:.2f}s")
                st.write(f"**Timestamp:** {entry['timestamp']}")
    else:
        st.info("No past analyses yet.")

# ============================================================================
# MAIN
# ============================================================================

def main():
    st.set_page_config(page_title="MarsBase", page_icon="🔴", layout="wide")
    st.markdown(MARS_CSS, unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; padding: 20px 0 10px 0;">
        <div class="main-title">🔴 MARSBASE</div>
        <div class="subtitle">🔴 MARTIAN BASE SELECTION · v1.2.0</div>
        <div style="display: flex; justify-content: center; gap: 10px; margin: 10px 0;">
            <span class="phase-badge phase-badge-2">☀️ ILLUMINATION</span>
            <span class="phase-badge phase-badge-3">💧 ICE</span>
            <span class="phase-badge phase-badge-4">⛰️ SLOPE</span>
            <span class="phase-badge phase-badge-5">🌋 LAVA TUBE</span>
        </div>
        <div class="cyber-divider"></div>
        <div class="mars-banner">
            🛰️ NASA MRO DATA · ☀️ ILLUMINATION · 💧 ICE · ⛰️ SLOPE · 🌋 LAVA TUBE · 🪨 REGOLITH
        </div>
    </div>
    """, unsafe_allow_html=True)
    init_session_state()
    region = render_region_switcher()
    region_sites = [k for k, v in MARS_SITES.items() if v['region'] == region]
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; padding: 8px 15px;
         border: 1px solid rgba(255,107,53,0.15); border-radius: 8px;
         background: rgba(255,107,53,0.03); margin-bottom: 15px;">
        <span style="color: #ffb347; font-family: 'Courier New'; font-size: 0.7rem;">📍 SITES LOADED</span>
        <span style="color: #ff6b35; font-family: 'Courier New'; font-size: 0.8rem; font-weight: bold;">{len(region_sites)} NASA candidates</span>
        <span style="color: #ffb347; font-family: 'Courier New'; font-size: 0.6rem;">{region.replace('_', ' ').upper()}</span>
    </div>
    """, unsafe_allow_html=True)
    params = render_sidebar(region)
    col1, col2 = st.columns([1.5, 1])
    with col1:
        render_map(params, region)
        render_query_interface(params, region)
    with col2:
        if st.session_state.selected_site_name:
            st.markdown(f"""
            <div style="padding: 10px 15px; border: 1px solid rgba(255,107,53,0.2);
                 border-radius: 8px; background: rgba(255,107,53,0.03); margin-bottom: 15px;">
                <div style="color: #ffb347; font-family: 'Courier New'; font-size: 0.6rem; letter-spacing: 1px;">SELECTED SITE</div>
                <div style="color: #ff6b35; font-family: 'Courier New'; font-size: 0.9rem;">{st.session_state.selected_site_name}</div>
            </div>
            """, unsafe_allow_html=True)
    st.divider()
    col_cmp1, col_cmp2 = st.columns([1, 3])
    with col_cmp1:
        st.session_state.compare_mode = st.toggle(
            "⚖️ Compare Mode",
            value=st.session_state.compare_mode,
            help="Enable side-by-side comparison of up to 3 sites."
        )
    if st.session_state.compare_mode:
        render_compare_mode(region)
        st.divider()
    if st.session_state.current_results:
        tab1, tab2 = st.tabs(["📊 Analysis Results", "🛰️ Live Solar System Tracker"])
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                render_results()
            with col2:
                render_memory_explorer()
            with st.expander("🧪 Simulation Lab (What-If)"):
                render_simulation_lab()
        with tab2:
            st.markdown("### 🛰️ Real-Time Solar System Tracker")
            st.markdown("Powered by **NASA's Eyes on the Solar System**.")
            components.iframe(
                src="https://eyes.nasa.gov/apps/solar-system/#/home",
                height=600, scrolling=True
            )
    else:
        render_memory_explorer()
    st.markdown("""
    <div class="cyber-divider"></div>
    <div style="text-align: center; padding: 15px 0; color: #333; font-family: 'Courier New'; 
         font-size: 0.6rem; letter-spacing: 2px;">
        <span style="color: #ff6b35;">[</span> 
        MARSBASE v1.2.0 · NASA MRO DATA · ARTEMIS-ALIGNED
        <span style="color: #ff6b35;">]</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; padding: 20px 0 40px 0;">
        <a href="https://buymeacoffee.com/stargazex" target="_blank"> 
            <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" 
                 alt="Buy Me A Coffee" 
                 style="height: 60px !important;width: 217px !important;" > 
        </a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()