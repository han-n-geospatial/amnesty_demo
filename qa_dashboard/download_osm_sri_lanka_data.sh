#!/usr/bin/env bash
# Download and extract Sri Lanka OSM admin boundaries and buildings as FlatGeobuf files.
# Requires: osmium-tool, gdal (ogr2ogr), curl
set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
PBF="sri-lanka-latest.osm.pbf"
GEOFABRIK_URL="https://download.geofabrik.de/asia/sri-lanka-latest.osm.pbf"

ADMIN_OUTPUT="sri_lanka_admin5.fgb"
BUILDINGS_OUTPUT="sri_lanka_buildings.fgb"

ADMIN_TMP="tmp_admin_boundaries.osm.pbf"
ADMIN_FILTERED="tmp_admin_filtered.osm.pbf"
BUILDINGS_TMP="tmp_buildings.osm.pbf"

# ── Download ──────────────────────────────────────────────────────────────────
echo "Downloading Sri Lanka OSM extract..."
curl -L -o "$PBF" "$GEOFABRIK_URL"

# ── Admin boundaries (admin_level=5) ─────────────────────────────────────────
# Two-pass filter: osmium applies OR logic per pass so AND requires chaining
echo "Extracting admin boundaries..."
osmium tags-filter "$PBF" "r/boundary=administrative" -o "$ADMIN_TMP" --overwrite
osmium tags-filter "$ADMIN_TMP" "r/admin_level=5" -o "$ADMIN_FILTERED" --overwrite

ogr2ogr -f FlatGeobuf "$ADMIN_OUTPUT" "$ADMIN_FILTERED" multipolygons \
  -nln admin5_sri_lanka -overwrite
echo "  -> $ADMIN_OUTPUT"

# ── Buildings ─────────────────────────────────────────────────────────────────
# Includes closed ways (w/) and multipolygon relations (r/)
echo "Extracting buildings..."
osmium tags-filter "$PBF" "w/building" "r/building" -o "$BUILDINGS_TMP" --overwrite

ogr2ogr -f FlatGeobuf "$BUILDINGS_OUTPUT" "$BUILDINGS_TMP" multipolygons \
  -nln buildings_sri_lanka -overwrite
echo "  -> $BUILDINGS_OUTPUT"

# ── Cleanup ───────────────────────────────────────────────────────────────────
echo "Cleaning up intermediates..."
rm -f "$ADMIN_TMP" "$ADMIN_FILTERED" "$BUILDINGS_TMP"

echo "Done."
