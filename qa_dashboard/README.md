# Sri Lanka Building Stock Dashboard

An interactive Bokeh dashboard visualising building counts across Sri Lanka's administrative provinces, built from OSM data with a mock attribute dataset.

## Project structure

```
├── download_osm_sri_lanka_data.sh  # Download and extract OSM data to FlatGeobuf
├── generate_mock_buildings.py      # Generate mock building attribute CSV
├── config.py                       # Paths, colours, column lists
├── spatial.py                      # GeoPandas data loading and processing
├── plots.py                        # Bokeh figure factories
└── sri_lanka_dashboard.py          # Main entry point — assembles and renders dashboard
```

## Setup

```bash
pip install -r requirements.txt
```

External dependencies (install via Homebrew or package manager):
```bash
brew install osmium-tool gdal curl
```

## Usage

**1. Download OSM data**
```bash
./download_osm_sri_lanka_data.sh
```
Outputs `sri_lanka_admin5.fgb` and `sri_lanka_buildings.fgb`.

**2. Generate mock building attributes**
```bash
python generate_mock_buildings.py
```
Outputs `mock_building_attributes.csv` (~3.4M rows). Note that actual OSM buildings geometries are used but buildings attributes are synthesised for the purpose of dashboard visualisations

**3. Run the dashboard**
```bash
python sri_lanka_dashboard.py
```
Opens the dashboard in the browser. Building counts per province are cached to `admin5_building_counts.csv` after the first run.

## Data files

`.fgb` files are excluded from version control due to size — regenerate them by running the download script. `.csv` outputs and Bokeh `.html` exports are tracked.

## Data sources

- OSM extract: [Geofabrik — Asia/Sri Lanka](https://download.geofabrik.de/asia/sri-lanka.html)
- Building attributes: synthetically generated, calibrated to approximate Sri Lanka's building stock
