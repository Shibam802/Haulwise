"""
Thin wrappers around two free, key-less public APIs:

- Nominatim (OpenStreetMap) for geocoding place names -> coordinates.
- OSRM public demo server for turn-by-turn driving routes + distance/duration.

Both are rate-limited public demo services. That's fine for an assessment /
portfolio project; swap in Mapbox/Google/self-hosted OSRM for production use.
"""
import time

import requests

# Nominatim's usage policy requires a real, identifying User-Agent (a
# placeholder like example.com can get rejected outright by some
# deployments). Swap the URL below for your own repo if you have one.
USER_AGENT = "Haulwise-Trip-Planner/1.0 (https://github.com/Shibam802/haulwise-eld-app)"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_URL_TEMPLATE = "https://router.project-osrm.org/route/v1/driving/{coords}"

# Nominatim's public server hard-caps usage at ~1 request/second per IP.
# We call geocode() up to 3x per trip (current, pickup, drop-off) — this
# tracks the last call time so we never exceed that, instead of hoping.
_last_nominatim_call = 0.0
_MIN_INTERVAL_SECONDS = 1.1


def _respect_nominatim_rate_limit():
    global _last_nominatim_call
    elapsed = time.monotonic() - _last_nominatim_call
    if elapsed < _MIN_INTERVAL_SECONDS:
        time.sleep(_MIN_INTERVAL_SECONDS - elapsed)
    _last_nominatim_call = time.monotonic()


class GeocodeError(Exception):
    pass


class RoutingError(Exception):
    pass


def geocode(place_name: str):
    """Return (lat, lon, display_name) for a free-text place name."""
    _respect_nominatim_rate_limit()
    resp = requests.get(
        NOMINATIM_URL,
        params={"q": place_name, "format": "json", "limit": 1},
        headers={"User-Agent": USER_AGENT},
        timeout=15,
    )
    if resp.status_code == 403:
        raise GeocodeError(
            "The geocoding service (Nominatim) is temporarily rate-limiting this "
            "machine's requests. Wait about a minute and try again."
        )
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise GeocodeError(f"Could not find a location matching '{place_name}'.")
    result = data[0]
    return float(result["lat"]), float(result["lon"]), result.get("display_name", place_name)


def route(coords_sequence):
    """
    coords_sequence: list of (lat, lon) tuples, in travel order (>= 2 points).
    Returns dict with:
      geometry: list of [lat, lon] points describing the road path
      legs: list of {distance_miles, duration_hours} per leg, in the same
            order as consecutive pairs of coords_sequence
      distance_miles, duration_hours: totals
    """
    coord_str = ";".join(f"{lon},{lat}" for lat, lon in coords_sequence)
    url = OSRM_URL_TEMPLATE.format(coords=coord_str)
    resp = requests.get(
        url,
        params={"overview": "full", "geometries": "geojson", "steps": "false"},
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != "Ok" or not data.get("routes"):
        raise RoutingError("Could not compute a driving route between those locations.")

    route_data = data["routes"][0]
    geometry = [[lat, lon] for lon, lat in route_data["geometry"]["coordinates"]]

    legs = []
    for leg in route_data["legs"]:
        meters = leg["distance"]
        seconds = leg["duration"]
        legs.append(
            {
                "distance_miles": meters / 1609.344,
                "duration_hours": seconds / 3600.0,
            }
        )

    total_miles = route_data["distance"] / 1609.344
    total_hours = route_data["duration"] / 3600.0

    return {
        "geometry": geometry,
        "legs": legs,
        "distance_miles": total_miles,
        "duration_hours": total_hours,
    }


def _haversine_miles(a, b):
    from math import radians, sin, cos, asin, sqrt

    lat1, lon1 = a
    lat2, lon2 = b
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * 3958.7613 * asin(sqrt(h))


def interpolate_along_route(geometry, target_miles):
    """Walk a [lat, lon] polyline and return the point at `target_miles` in."""
    if not geometry:
        return None
    if target_miles <= 0:
        return geometry[0]
    traveled = 0.0
    for i in range(1, len(geometry)):
        a, b = geometry[i - 1], geometry[i]
        seg_miles = _haversine_miles(a, b)
        if traveled + seg_miles >= target_miles or i == len(geometry) - 1:
            if seg_miles <= 1e-9:
                return b
            frac = min(max((target_miles - traveled) / seg_miles, 0.0), 1.0)
            lat = a[0] + (b[0] - a[0]) * frac
            lon = a[1] + (b[1] - a[1]) * frac
            return [lat, lon]
        traveled += seg_miles
    return geometry[-1]
