from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_DIR            = Path(".")
ADMIN_GEOM_PATH     = DATA_DIR / "sri_lanka_admin5.fgb"
BUILDINGS_GEOM_PATH = DATA_DIR / "sri_lanka_buildings.fgb"
MOCK_PATH           = DATA_DIR / "mock_building_attributes.csv"
COUNTS_CACHE        = DATA_DIR / "admin5_building_counts.csv"

# ── Colours ───────────────────────────────────────────────────────────────────
BG      = "#f5f5f0"
PANEL   = "#ffffff"
ACCENT  = "#003f5c"
TEXT    = "#1a1a2e"
SUBTEXT = "#555566"
GRID    = "#e0e0e0"

PALETTE = [
    "#003f5c", "#594e90", "#bc4c96", "#ff5f66", "#ffa600",
    "#2f7bb5", "#7a3f8f", "#e8836a",
]

# ── Column lists ──────────────────────────────────────────────────────────────
CONTINUOUS = ["footprint_area_m2", "building_height_m"]
DISCRETE   = ["construction_era", "building_use", "building_material", "use_source"]

# ── Map settings ──────────────────────────────────────────────────────────────
ADMIN_LEVEL    = "5"
MAP_EXTENT_PAD = 0.1   # fractional padding around map bounds
