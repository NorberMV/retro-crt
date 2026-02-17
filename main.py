import json
import sys
from pathlib import Path

import pygame

GEOJSON_FILE = Path(__file__).parent / "map" / "lines.geojson"

SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 900
BLACK = (0, 0, 0)
GREEN = (0, 230, 0)  # Base retro green
BRIGHT = (0, 255, 120)  # For primary/secondary roads
DARK = (0, 35, 0)  # Scanlines
PADDING = 60  # Pixels from edge
LINE_WIDTH_BASE = 2

if not GEOJSON_FILE.is_file():
    print(f"GeoJSON not found: {GEOJSON_FILE}")
    print("Tip: Export from https://overpass-turbo.eu/ → highway=* in your neighborhood → Export → GeoJSON")
    sys.exit(1)


def read_geojson(geojson_file: Path) -> dict:
    with open(geojson_file, encoding="utf-8") as f:
        geojson_data = json.load(f)

    if geojson_data.get("type") != "FeatureCollection":
        print("File is not a FeatureCollection. Expected OSM/Overpass export.")
        return None
    return geojson_data


def get_lon_lat(data: dict) -> tuple:
    if data is not None:
        lons, lats = [], []
        for feature in data.get("features", []):
            geom = feature.get("geometry", {})
            coords = geom.get("coordinates", [])
            gtype = geom.get("type")

            if gtype == "LineString":
                for lon, lat in coords:
                    lons.append(lon)
                    lats.append(lat)
            elif gtype == "MultiLineString":
                for line in coords:
                    for lon, lat in line:
                        lons.append(lon)
                        lats.append(lat)

    if not lons or not lats:
        raise RuntimeError("No valid coordinates found in GeoJSON.")
    return lons, lats


def main():
    data = read_geojson(GEOJSON_FILE)
    try:
        lons, lats = get_lon_lat(data)
    except RuntimeError:
        sys.exit(1)

    lon_min, lon_max = min(lons), max(lons)
    lat_min, lat_max = min(lats), max(lats)
    lon_range = lon_max - lon_min if lon_max > lon_min else 1.0
    lat_range = lat_max - lat_min if lat_max > lat_min else 1.0

    draw_w = SCREEN_WIDTH - 2 * PADDING
    draw_h = SCREEN_HEIGHT - 2 * PADDING

    # ── Pygame init ───────────────────────────────────────────────────────────
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Retro CRT Street Map")
    clock = pygame.time.Clock()

    # ── Zoom/Pan State ────────────────────────────────────────────────────────
    zoom = 1.0
    offset_x = PADDING
    offset_y = PADDING
    is_dragging = False
    last_mouse_pos = (0, 0)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            # ── Mouse Events ──────────────────────────────────────────────────────
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    is_dragging = True
                    last_mouse_pos = event.pos
                elif event.button == 4:  # Wheel up (Zoom in)
                    mx, my = event.pos
                    factor = 1.1
                    offset_x = mx - (mx - offset_x) * factor
                    offset_y = my - (my - offset_y) * factor
                    zoom *= factor
                elif event.button == 5:  # Wheel down (Zoom out)
                    mx, my = event.pos
                    factor = 1 / 1.1
                    offset_x = mx - (mx - offset_x) * factor
                    offset_y = my - (my - offset_y) * factor
                    zoom *= factor

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    is_dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if is_dragging:
                    mx, my = event.pos
                    dx = mx - last_mouse_pos[0]
                    dy = my - last_mouse_pos[1]
                    offset_x += dx
                    offset_y += dy
                    last_mouse_pos = (mx, my)

        screen.fill(BLACK)

        # ── CRT scanlines ─────────────────────────────────────────────────────
        for y in range(0, SCREEN_HEIGHT, 4):
            pygame.draw.line(screen, DARK, (0, y), (SCREEN_WIDTH, y), 1)

        # ── Draw each street ──────────────────────────────────────────────────
        for feature in data["features"]:
            geom = feature.get("geometry", {})
            props = feature.get("properties", {})
            gtype = geom.get("type")
            coords = geom.get("coordinates", [])

            highway = props.get("highway", "other")

            # Color & width by road class (OSM highway tags)
            color = GREEN
            width = LINE_WIDTH_BASE
            if highway in ["motorway", "trunk", "primary"]:
                color = BRIGHT
                width = 4
            elif highway in ["secondary", "tertiary"]:
                color = (0, 255, 80)
                width = 3
            elif highway == "residential":
                color = (0, 180, 0)
                width = 2

            if gtype == "LineString":
                line_list = [coords]
            elif gtype == "MultiLineString":
                line_list = coords
            else:
                continue  # Skip points, polygons, etc.

            for line_coords in line_list:
                points = []
                for lon, lat in line_coords:
                    # Normalize to screen coords (flip y for map convention)
                    bx = (lon - lon_min) / lon_range * draw_w
                    by = (lat_max - lat) / lat_range * draw_h

                    x = int(bx * zoom + offset_x)
                    y = int(by * zoom + offset_y)
                    points.append((x, y))

                if len(points) >= 2:
                    pygame.draw.lines(screen, color, False, points, width)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    print("Exited cleanly.")


if __name__ == "__main__":
    main()
