"""Stable tool entry points for the MVP.

Each function has one responsibility and one response envelope. The default
provider is ``mock`` so the whole system remains runnable while teammates are
implementing real algorithms. Set ``provider`` to ``real`` or ``auto`` when a
module is ready.
"""

from time import perf_counter

from core.contracts import failure, success
from services.mock_data import (
    FLOOD_GEOJSON,
    OBJECTS_GEOJSON,
    OVERLAY_STATS,
    ROUTE_GEOJSON,
    clone,
)


def _provider(payload: dict) -> str:
    return str(payload.get("provider", "mock")).lower()


def _should_fallback(payload: dict) -> bool:
    return bool(payload.get("fallback", True))


def _results(context: dict) -> dict:
    """Accept both the new TaskContext and the old plain result mapping."""
    return context.get("results", context)


def extract_water(payload: dict) -> dict:
    started = perf_counter()
    provider = _provider(payload)
    image_path = payload.get("image_path")

    if provider in {"real", "auto"}:
        try:
            from services.ndwi_extractor import extract_flood

            geojson = extract_flood(image_path)
            return success(
                {"geojson": geojson},
                module="water_extract",
                algorithm=payload.get("algorithm", "sdwi"),
                started_at=started,
                provider="real",
            )
        except Exception as exc:
            if provider == "real" or not _should_fallback(payload):
                return failure("WATER_EXTRACT_FAILED", str(exc), "water_extract", started)

    return success(
        {
            "geojson": clone(FLOOD_GEOJSON),
            "area_km2": 12.5,
            "confidence": 0.87,
        },
        module="water_extract",
        algorithm="SDWI_threshold_mock",
        started_at=started,
        provider="mock",
        input_image=image_path,
    )


def plan_path(payload: dict) -> dict:
    started = perf_counter()
    provider = _provider(payload)

    if provider in {"real", "auto"}:
        try:
            from services.path_planner import AStarPlanner

            planner = AStarPlanner(grid_size=float(payload.get("grid_size_m", 30)))
            start = tuple(payload.get("start", (109.55, 23.05)))
            coverage = payload.get("coverage_polygon")
            if coverage:
                result = planner.plan_coverage(
                    start=start,
                    coverage_polygon=coverage,
                    no_fly_zones=payload.get("no_fly_zones", []),
                )
                return success(result, "path_plan", "astar_coverage", started, provider="real")

            goal = tuple(payload.get("goal", (109.65, 23.10)))
            waypoints = planner.plan(start=start, goal=goal, obstacles=payload.get("obstacles", []))
            route = planner.to_geojson(waypoints)
            return success({"route": route, "waypoints": waypoints}, "path_plan", "astar", started, provider="real")
        except Exception as exc:
            if provider == "real" or not _should_fallback(payload):
                return failure("PATH_PLAN_FAILED", str(exc), "path_plan", started)

    return success(
        {
            "route": clone(ROUTE_GEOJSON),
            "total_distance_km": 15.2,
            "duration_min": 42,
            "segments": 1,
            "coverage_rate": 0.85,
        },
        module="path_plan",
        algorithm="astar_mock",
        started_at=started,
        provider="mock",
    )


def detect_objects(payload: dict) -> dict:
    started = perf_counter()
    provider = _provider(payload)

    if provider in {"real", "auto"}:
        try:
            from services.color_detector import detect_by_color

            result = detect_by_color(payload.get("image_path"))
            return success(result, "object_detect", "color_detector", started, provider="real")
        except Exception as exc:
            if provider == "real" or not _should_fallback(payload):
                return failure("OBJECT_DETECT_FAILED", str(exc), "object_detect", started)

    return success(
        {
            "geojson": clone(OBJECTS_GEOJSON),
            "counts": {"person": 1, "vehicle": 1, "building": 1},
        },
        module="object_detect",
        algorithm="mock_detection",
        started_at=started,
        provider="mock",
    )


def overlay_layers(payload: dict) -> dict:
    started = perf_counter()
    provider = _provider(payload)

    if provider in {"real", "auto"}:
        try:
            from services.igs_client import overlay_layers as igs_overlay

            result = igs_overlay(
                payload["layer1_gdbp"],
                payload["layer2_gdbp"],
                over_type=int(payload.get("over_type", 1)),
                result_gdbp=payload.get("result_gdbp"),
            )
            return success({"stats": result}, "gis_overlay", "IGServer_600227", started, provider="real")
        except Exception as exc:
            if provider == "real" or not _should_fallback(payload):
                return failure("GIS_OVERLAY_FAILED", str(exc), "gis_overlay", started)

    return success(
        {"stats": clone(OVERLAY_STATS)},
        module="gis_overlay",
        algorithm="overlay_mock",
        started_at=started,
        provider="mock",
    )


def aggregate_stats(context: dict) -> dict:
    """Create a stable summary from whatever tools have completed."""
    result_map = _results(context)
    water = result_map.get("water_extract", {})
    path = result_map.get("path_plan", {})
    detect = result_map.get("object_detect", {})
    overlay = result_map.get("gis_overlay", {})
    return success(
        {
            "flood_area_km2": water.get("area_km2", 12.5),
            "route_length_km": path.get("total_distance_km", 15.2),
            "route_duration_min": path.get("duration_min", 42),
            "detected_counts": detect.get("counts", {}),
            "overlay_stats": overlay.get("stats", {}),
        },
        module="stats",
        algorithm="aggregation",
    )


def assess_risk(context: dict) -> dict:
    """Explainable risk layer for the MVP.

    A future model can replace this function while keeping the same output
    shape for the frontend and report generator.
    """
    result_map = _results(context)
    water = result_map.get("water_extract", {})
    detect = result_map.get("object_detect", {})
    overlay = result_map.get("gis_overlay", {})
    counts = detect.get("counts", {})
    people = counts.get("person", 0)
    flooded_buildings = overlay.get("stats", {}).get("buildings", {}).get("count", 0)

    reasons = []
    if people > 0:
        reasons.append(f"发现{people}名人员目标")
    if flooded_buildings > 0:
        reasons.append(f"受影响建筑约{flooded_buildings}栋")
    if water.get("area_km2", 0) > 10:
        reasons.append("淹没面积较大")

    level = "high" if people > 0 else ("medium" if reasons else "low")
    action = "优先规划人员目标巡检航线" if people > 0 else "继续开展重点区域巡检"
    return success(
        {
            "risk_level": level,
            "reasons": reasons or ["当前暂无明显高风险指标"],
            "recommended_action": action,
            "confidence": 0.75 if reasons else 0.55,
        },
        module="risk_assess",
        algorithm="explainable_rules",
    )


def simulate_gis(payload: dict) -> dict:
    """Placeholder for future flood-depth/terrain simulation."""
    return success(
        {
            "simulation": "mock",
            "water_level_m": payload.get("water_level_m", 2.0),
            "message": "GIS态势推演占位结果，等待真实模拟工具接入",
        },
        module="gis_simulate",
        algorithm="mock_simulation",
    )


def generate_report(context: dict) -> dict:
    """Stable report result shape; PDF/专题图 can be added later."""
    result_map = _results(context)
    stats = result_map.get("stats", {})
    risk = result_map.get("risk_assess", {})
    return success(
        {
            "format": "html",
            "title": "洪涝应急灾情简报",
            "content": {
                "flood_area_km2": stats.get("flood_area_km2", 12.5),
                "route_length_km": stats.get("route_length_km", 15.2),
                "risk_level": risk.get("risk_level", "medium"),
                "recommended_action": risk.get("recommended_action", "继续开展重点区域巡检"),
            },
            "download_url": None,
        },
        module="report",
        algorithm="mock_report",
    )


TOOL_HANDLERS = {
    "water_extract": extract_water,
    "path_plan": plan_path,
    "object_detect": detect_objects,
    "gis_overlay": overlay_layers,
    "gis_simulate": simulate_gis,
    "risk_assess": assess_risk,
}


def run_tool(tool_id: str, payload: dict, context: dict) -> dict:
    if tool_id == "stats":
        return aggregate_stats(context)
    if tool_id == "generate_report":
        return generate_report(context)
    if tool_id == "risk_assess":
        return assess_risk(context)
    handler = TOOL_HANDLERS.get(tool_id)
    if handler is None:
        return failure("UNKNOWN_TOOL", f"未知工具: {tool_id}", "workflow")
    return handler(payload)
