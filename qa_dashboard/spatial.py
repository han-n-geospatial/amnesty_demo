import geopandas as gpd
import pandas as pd
from pathlib import Path

from config import ADMIN_LEVEL, MAP_EXTENT_PAD


def load_admin_regions(path: Path) -> gpd.GeoDataFrame:
    admin = gpd.read_file(path).set_crs("EPSG:4326", allow_override=True)
    admin = admin[
        admin.geometry.geom_type.isin(["Polygon", "MultiPolygon"]) &
        (admin["admin_level"] == ADMIN_LEVEL)
    ].copy()
    name_col = "name:en" if "name:en" in admin.columns else "name"
    admin["admin_name"] = admin[name_col].fillna("Unknown")
    return admin


def count_buildings_per_region(
    admin: gpd.GeoDataFrame,
    buildings_path: Path,
    cache_path: Path,
) -> gpd.GeoDataFrame:
    if cache_path.exists():
        print(f"Loading cached counts from {cache_path}...")
        count_df = pd.read_csv(cache_path, index_col="idx")
        admin = admin.join(count_df[["building_count"]])
    else:
        print(f"Counting buildings across {len(admin)} regions...")
        total = len(admin)
        counts = []
        for i, (idx, region) in enumerate(admin.iterrows(), start=1):
            print(f"  {region['admin_name']} ({i}/{total})")
            buildings = gpd.read_file(buildings_path, mask=region.geometry)
            buildings = buildings[
                buildings.geometry.geom_type.isin(["Polygon", "MultiPolygon"])
            ]
            counts.append({
                "idx": idx,
                "admin_name": region["admin_name"],
                "building_count": len(buildings),
            })

        count_df = pd.DataFrame(counts).set_index("idx")
        count_df.to_csv(cache_path)
        print(f"Saved counts to {cache_path}")
        admin = admin.join(count_df[["building_count"]])

    admin["building_count"] = admin["building_count"].fillna(0).astype(int)
    return admin


def get_patch_coords(gdf: gpd.GeoDataFrame) -> tuple[list, list]:
    """Extract exterior ring coordinates for each feature.

    MultiPolygons are represented by their largest polygon — a deliberate
    simplification to keep the choropleth rendering straightforward.
    """
    xs, ys = [], []
    for geom in gdf.geometry:
        if geom.geom_type == "MultiPolygon":
            geom = max(geom.geoms, key=lambda g: g.area)
        x, y = geom.exterior.coords.xy
        xs.append(list(x))
        ys.append(list(y))
    return xs, ys


def padded_bounds(gdf: gpd.GeoDataFrame, pad: float = MAP_EXTENT_PAD) -> dict:
    b = gdf.total_bounds  # [minx, miny, maxx, maxy]
    px = (b[2] - b[0]) * pad
    py = (b[3] - b[1]) * pad
    return dict(
        x_range=(b[0] - px, b[2] + px),
        y_range=(b[1] - py, b[3] + py),
    )
