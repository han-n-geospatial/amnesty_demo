import pandas as pd
from bokeh.plotting import show
from bokeh.layouts import column, row, gridplot

from config import (
    ADMIN_GEOM_PATH, BUILDINGS_GEOM_PATH, MOCK_PATH, COUNTS_CACHE,
    CONTINUOUS, DISCRETE, PALETTE, BG,
)
from spatial import (
    load_admin_regions, 
    count_buildings_per_region, 
    get_patch_coords, 
    padded_bounds
)
from plots import (
    make_choropleth_map, make_histogram, make_pie, make_stacked_bar,
    make_continuous_stats_table, make_discrete_stats_table,
    header, title_div,
)

# ── Spatial data ──────────────────────────────────────────────────────────────
print("Loading admin regions...")
admin = load_admin_regions(ADMIN_GEOM_PATH)
admin = count_buildings_per_region(admin, BUILDINGS_GEOM_PATH, COUNTS_CACHE)
admin_wm = admin.to_crs("EPSG:3857")

xs, ys = get_patch_coords(admin_wm)
bounds = padded_bounds(admin_wm)

map_data = dict(
    x=xs, y=ys,
    name=list(admin_wm["admin_name"]),
    building_count=list(admin_wm["building_count"]),
)

# ── Attribute data ────────────────────────────────────────────────────────────
print("Loading mock building attributes...")
df = pd.read_csv(MOCK_PATH)

# ── Figures ───────────────────────────────────────────────────────────────────
map_fig      = make_choropleth_map(map_data, **bounds)
hist_area    = make_histogram(df["footprint_area_m2"], "Footprint Area",  "m²", PALETTE[0], bins=60)
hist_height  = make_histogram(df["building_height_m"], "Building Height", "m",  PALETTE[2])
pie_era      = make_pie(df["construction_era"],  "Construction Era")
pie_material = make_pie(df["building_material"], "Building Material")
bar_use      = make_stacked_bar(df, "building_use", "use_source", "Building Use by Source")

stats_table  = make_continuous_stats_table(df, CONTINUOUS)
disc_table   = make_discrete_stats_table(df, DISCRETE)

# ── Layout ────────────────────────────────────────────────────────────────────
layout = column(
    title_div(),
    header("Spatial Distribution — Building Counts by Province"),
    row(map_fig, column(
        header("Quantitative Attribute Summary Statistics"),
        stats_table,
        header("Attribute Distributions"),
        gridplot([[hist_area, hist_height]], toolbar_location=None, merge_tools=False),
        header("Categorical Attribute Summary"),
        disc_table,
    )),
    header("Categorical Attribute Breakdown"),
    row(pie_era, pie_material, bar_use),
    background=BG,
    sizing_mode="fixed",
)

show(layout)
