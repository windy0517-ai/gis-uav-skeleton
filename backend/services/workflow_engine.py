"""Single source of truth for the fixed MVP workflows."""

from typing import Optional
from uuid import uuid4

from core.contracts import failure, success
from core.task_context import TaskContext
from services.tool_services import run_tool


# Tool output is also registered under a stable artifact name. Future report
# generation or an LLM planner can consume artifacts without knowing which
# concrete algorithm produced them.
ARTIFACTS = {
    "water_extract": "flood_extent",
    "path_plan": "inspection_route",
    "object_detect": "detected_objects",
    "gis_overlay": "affected_stats",
    "risk_assess": "risk_assessment",
    "stats": "decision_metrics",
    "generate_report": "decision_report",
}


SCENARIOS = {
    "flood_recon": {
        "name": "洪水侦察",
        "steps": [
            {"id": "water_extract", "label": "水体提取"},
            {"id": "path_plan", "label": "路径规划"},
            {"id": "gis_overlay", "label": "GIS叠置"},
            {"id": "risk_assess", "label": "风险评估"},
            {"id": "stats", "label": "统计汇总"},
            {"id": "display", "label": "三维展示", "display_only": True},
        ],
    },
    "damage_assess": {
        "name": "灾情评估",
        "steps": [
            {"id": "water_extract", "label": "水体提取"},
            {"id": "gis_overlay", "label": "GIS叠置"},
            {"id": "risk_assess", "label": "风险评估"},
            {"id": "stats", "label": "统计汇总"},
            {"id": "display", "label": "结果展示", "display_only": True},
        ],
    },
    "uav_inspect": {
        "name": "无人机巡检",
        "steps": [
            {"id": "path_plan", "label": "路径规划"},
            {"id": "object_detect", "label": "目标识别"},
            {"id": "gis_overlay", "label": "GIS叠置"},
            {"id": "risk_assess", "label": "风险评估"},
            {"id": "stats", "label": "统计汇总"},
            {"id": "display", "label": "三维展示", "display_only": True},
        ],
    },
    "situation_deduce": {
        "name": "态势推演",
        "steps": [
            {"id": "gis_simulate", "label": "GIS模拟"},
            {"id": "gis_overlay", "label": "GIS叠置"},
            {"id": "risk_assess", "label": "风险评估"},
            {"id": "stats", "label": "统计汇总"},
            {"id": "display", "label": "三维展示", "display_only": True},
        ],
    },
    "decision_report": {
        "name": "决策简报",
        "steps": [
            {"id": "stats", "label": "汇总数据"},
            {"id": "risk_assess", "label": "风险评估"},
            {"id": "generate_report", "label": "生成专题图/简报"},
            {"id": "display", "label": "展示结果", "display_only": True},
        ],
    },
}


def _step_payload(params: dict, context: TaskContext) -> dict:
    payload = dict(params)
    water = context["results"].get("water_extract", {})
    if "coverage_polygon" not in payload and water.get("geojson"):
        # Translate the previous GeoJSON artifact into the simple coordinate
        # shape expected by the path planner.
        features = water["geojson"].get("features", [])
        if features:
            geometry = features[0].get("geometry", {})
            coordinates = geometry.get("coordinates", [])
            if geometry.get("type") == "Polygon" and coordinates:
                payload["coverage_polygon"] = coordinates[0]
    return payload


def _workflow_data(context: TaskContext, logs: list, scenario_id: str) -> dict:
    return {
        "task_id": context["task_id"],
        "scenario": scenario_id,
        "state": context["state"],
        "logs": logs,
        "results": context["results"],
        "artifacts": context["artifacts"],
        "metrics": context["metrics"],
    }


def execute_workflow(scenario_id: str, params: Optional[dict] = None,
                     task_id: Optional[str] = None) -> dict:
    if scenario_id not in SCENARIOS:
        return failure("UNKNOWN_SCENARIO", f"未知场景: {scenario_id}", "workflow")

    params = params or {}
    task_id = task_id or str(uuid4())[:8]
    scenario = SCENARIOS[scenario_id]
    context = TaskContext(task_id, scenario_id, params)
    logs = []

    for index, step in enumerate(scenario["steps"]):
        step_id = step["id"]
        logs.append({
            "type": "step_start",
            "step": step["label"],
            "step_id": step_id,
            "progress": round(index / len(scenario["steps"]) * 100),
            "message": f"正在执行: {step['label']}",
        })

        if step.get("display_only"):
            logs.append({"type": "step_done", "step": step["label"], "step_id": step_id,
                         "message": f"完成: {step['label']}"})
            continue

        result = run_tool(step_id, _step_payload(params, context), context)
        if result.get("status") != "success":
            context["state"] = "failed"
            logs.append({"type": "step_error", "step": step["label"], "step_id": step_id,
                         "message": result.get("error", {}).get("message", "执行失败")})
            return {
                **result,
                "data": _workflow_data(context, logs, scenario_id),
            }

        context.record(step_id, result, ARTIFACTS.get(step_id))
        logs.append({"type": "step_done", "step": step["label"], "step_id": step_id,
                     "message": f"完成: {step['label']}"})

    context["state"] = "completed"
    return success(
        {
            **_workflow_data(context, logs, scenario_id),
            "summary": f"{scenario['name']} 已完成!",
        },
        module="workflow",
        algorithm="fixed_rule_engine",
        scenario=scenario_id,
    )


class RuleEngine:
    """Compatibility wrapper kept for teammates using the original import path."""

    def execute(self, scenario_id: str, params: Optional[dict] = None) -> dict:
        return execute_workflow(scenario_id, params)
