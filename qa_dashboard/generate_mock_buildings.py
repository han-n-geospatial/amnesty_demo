import numpy as np
import pandas as pd
from pathlib import Path

OUTPUT_PATH = Path("mock_building_attributes.csv")
N_ROWS      = 3_379_369  # added manually from .fbg buildings count
RNG         = np.random.default_rng(42)

# Discrete columns and their category distributions, calibrated for Sri Lanka
DISCRETE_SPEC = {
    "construction_era": (
        ["Pre-1950", "1950–1980", "1980–2000", "Post-2000"],
        [0.05, 0.20, 0.28, 0.47],
    ),
    "building_use": (
        ["Residential", "Commercial", "Industrial", "Agricultural", "Religious", "Educational", "Healthcare"],
        [0.78, 0.10, 0.04, 0.04, 0.02, 0.01, 0.01],
    ),
    "building_material": (
        ["Brick/Masonry", "Concrete", "Wood", "Metal/Corrugated Iron", "Mixed", "Adobe/Mud"],
        [0.45, 0.30, 0.10, 0.08, 0.05, 0.02],
    ),
    "use_source": (
        ["OSM", "National Datasets", "Satellite Imagery", "Overture Maps", "Estimate"],
        [0.55, 0.15, 0.18, 0.07, 0.05],
    ),
}

# Missing-value rates per column
MISSING_RATES = {
    "construction_era":  0.08,
    "footprint_area_m2": 0.12,
    "building_height_m": 0.15,
    "num_floors":        0.10,
    "building_use":      0.06,
    "building_material": 0.09,
    "use_source":        0.07,
}


def sample_discrete(cats: list, probs: list, n: int) -> np.ndarray:
    return RNG.choice(cats, size=n, p=probs).astype(object)


def apply_nans(arr: np.ndarray, frac: float) -> np.ndarray:
    arr[RNG.random(size=len(arr)) < frac] = None
    return arr


def generate_continuous(n: int) -> dict:
    footprint_area = np.round(RNG.lognormal(mean=4.2, sigma=0.6, size=n), 1)

    num_floors_raw  = np.clip(RNG.integers(1, 6, size=n), 1, 5)
    per_floor_height = RNG.lognormal(mean=1.0, sigma=0.4, size=n)
    building_height  = np.round(per_floor_height * num_floors_raw, 1)

    return {
        "footprint_area_m2": footprint_area,
        "building_height_m": building_height,
        "num_floors":        num_floors_raw.astype(float),
    }


def generate_discrete(n: int) -> dict:
    return {
        col: sample_discrete(cats, probs, n)
        for col, (cats, probs) in DISCRETE_SPEC.items()
    }


def introduce_missing(columns: dict, rates: dict) -> dict:
    return {
        col: apply_nans(arr.copy(), rates[col]) if col in rates else arr
        for col, arr in columns.items()
    }


def main() -> None:
    print(f"Generating {N_ROWS:,} mock building records...")

    continuous = generate_continuous(N_ROWS)
    discrete   = generate_discrete(N_ROWS)

    # Merge and reorder columns to match logical grouping
    all_columns = {
        "construction_era":   discrete["construction_era"],
        "footprint_area_m2":  continuous["footprint_area_m2"],
        "building_height_m":  continuous["building_height_m"],
        "num_floors":         continuous["num_floors"],
        "building_use":       discrete["building_use"],
        "building_material":  discrete["building_material"],
        "use_source":         discrete["use_source"],
    }

    all_columns = introduce_missing(all_columns, MISSING_RATES)
    df = pd.DataFrame(all_columns)

    print(f"Writing to {OUTPUT_PATH}...")
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Done. Shape: {df.shape}")

if __name__ == "__main__":
    main()
