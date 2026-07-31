"""Stable demo fixtures.

These fixtures are deliberately kept outside route files. A teammate can replace
the implementation behind a tool without changing the API contract or frontend.
"""

from copy import deepcopy


FLOOD_GEOJSON = {
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "properties": {
            "area_km2": 12.5,
            "confidence": 0.87,
            "method": "SDWI_threshold",
            "timestamp": "2026-07-22T12:00:00Z",
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [109.55, 23.05], [109.58, 23.08], [109.62, 23.10],
                [109.65, 23.08], [109.63, 23.04], [109.58, 23.02],
                [109.55, 23.05],
            ]],
        },
    }],
}


ROUTE_GEOJSON = {
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "properties": {
            "total_distance_km": 15.2,
            "duration_min": 42,
            "waypoint_count": 28,
            "algorithm": "astar_grid",
        },
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [109.55, 23.05, 150], [109.57, 23.07, 150],
                [109.60, 23.10, 150], [109.62, 23.08, 150],
                [109.60, 23.02, 150], [109.55, 23.05, 150],
            ],
        },
    }],
}


OBJECTS_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"class": "person", "confidence": 0.85, "in_flood": True},
            "geometry": {"type": "Point", "coordinates": [109.59, 23.06, 150]},
        },
        {
            "type": "Feature",
            "properties": {"class": "vehicle", "confidence": 0.92, "in_flood": False},
            "geometry": {"type": "Point", "coordinates": [109.58, 23.04, 150]},
        },
        {
            "type": "Feature",
            "properties": {"class": "building", "confidence": 0.95, "in_flood": True},
            "geometry": {"type": "Point", "coordinates": [109.60, 23.07, 150]},
        },
    ],
}


OVERLAY_STATS = {
    "farmland": {"area_km2": 8.2},
    "buildings": {"count": 47},
    "roads": {"length_km": 3.1},
}


def clone(value):
    return deepcopy(value)
