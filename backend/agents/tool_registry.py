"""Safe list of tools that an Agent is allowed to call."""

from services.tool_services import TOOL_HANDLERS


AGENT_TOOLS = frozenset(set(TOOL_HANDLERS) | {"stats", "generate_report"})

TOOL_CATALOG = {
    "water_extract": {"label": "水体提取", "description": "提取洪水或水体范围"},
    "path_plan": {"label": "路径规划", "description": "生成无人机巡检航线"},
    "object_detect": {"label": "目标识别", "description": "识别人、车辆和建筑目标"},
    "gis_overlay": {"label": "GIS叠置", "description": "统计受影响建筑、道路和人口"},
    "gis_simulate": {"label": "GIS模拟", "description": "执行洪涝态势推演"},
    "risk_assess": {"label": "风险评估", "description": "生成风险等级和行动建议"},
    "stats": {"label": "统计汇总", "description": "汇总各工具的指标结果"},
    "generate_report": {"label": "生成报告", "description": "生成灾情简报或专题报告"},
}


def available_tools() -> list:
    return [
        {"tool_id": tool_id, **TOOL_CATALOG[tool_id]}
        for tool_id in sorted(AGENT_TOOLS)
    ]
