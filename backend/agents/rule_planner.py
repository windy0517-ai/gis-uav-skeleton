"""Offline rule planner used until a real LLM planner is configured."""

from typing import Any, Dict, List, Optional

from agents.schemas import AgentPlan, PlanStep


FLOOD_WORDS = ("洪水", "洪涝", "淹没", "水体", "积水")
PERSON_WORDS = ("人员", "受困", "救援", "搜救", "被困")
DAMAGE_WORDS = ("灾情", "建筑", "道路", "受影响", "评估", "统计")
ROUTE_WORDS = ("路线", "航线", "巡检", "路径", "避障")
RISK_WORDS = ("风险", "等级", "预警", "建议")
REPORT_WORDS = ("报告", "简报", "汇报", "导出", "专题图")


def _has(message: str, words: tuple) -> bool:
    return any(word in message for word in words)


def _step(tool_id: str, label: str, reason: str, params: Optional[Dict[str, Any]] = None) -> PlanStep:
    return PlanStep(tool_id, label, reason, params or {})


class RulePlanner:
    """Convert a small set of common Chinese task descriptions into plans."""

    name = "rule_planner"

    def make_plan(self, message: str, context: Optional[dict] = None) -> AgentPlan:
        context = context or {}
        message = str(message or "").strip()
        region = str(context.get("region", "guigang"))
        if not message:
            return AgentPlan(
                goal="",
                region=region,
                plan=[],
                planner=self.name,
                needs_clarification=True,
                clarification="请描述需要完成的洪涝分析或无人机任务。",
            )

        flood = _has(message, FLOOD_WORDS)
        person = _has(message, PERSON_WORDS)
        report = _has(message, REPORT_WORDS)
        # "灾情简报" is a reporting request, not a request to run the full
        # damage-assessment chain unless the user also names a flood/route/person target.
        report_only = report and not _has(message, FLOOD_WORDS + PERSON_WORDS + ROUTE_WORDS)
        damage = _has(message, DAMAGE_WORDS) and not report_only
        route = _has(message, ROUTE_WORDS)
        risk = _has(message, RISK_WORDS)

        steps: List[PlanStep] = []
        shared = context.get("params", {})
        water_params = {}
        if shared.get("image_path") or shared.get("sar_image_path"):
            water_params["image_path"] = shared.get("sar_image_path", shared.get("image_path"))
        uav_params = {}
        if shared.get("uav_image_path"):
            uav_params["image_path"] = shared["uav_image_path"]

        if flood or damage or person:
            steps.append(_step("water_extract", "水体提取", "确认当前淹没范围", water_params))
        if person:
            steps.append(_step("object_detect", "目标识别", "重点寻找受困人员", uav_params))
        if damage or person:
            steps.append(_step("gis_overlay", "GIS叠置", "统计受影响对象", {
                key: shared[key]
                for key in ("layer1_gdbp", "layer2_gdbp", "result_gdbp", "over_type")
                if key in shared
            }))
        if (risk or flood or damage or person or report) and not report_only:
            steps.append(_step("risk_assess", "风险评估", "根据分析结果判断风险等级"))
        if route or person:
            steps.append(_step("path_plan", "路径规划", "生成重点区域无人机巡检航线", {
                key: shared[key]
                for key in ("start", "goal", "coverage_polygon", "no_fly_zones", "grid_size_m")
                if key in shared
            }))
        if damage or report:
            steps.append(_step("stats", "统计汇总", "汇总面积、目标和受影响对象指标"))
        if report_only:
            steps.append(_step("risk_assess", "风险评估", "根据汇总指标判断风险等级"))
        if report:
            steps.append(_step("generate_report", "生成报告", "形成灾情简报或专题报告"))

        if not steps:
            return AgentPlan(
                goal="",
                region=region,
                plan=[],
                planner=self.name,
                needs_clarification=True,
                clarification="暂时无法识别任务。请说明洪涝分析、人员搜救、路径规划、灾情评估或报告生成目标。",
            )

        if person:
            goal = "flood_rescue"
        elif report:
            goal = "decision_report"
        elif damage:
            goal = "damage_assess"
        elif route:
            goal = "uav_inspect"
        else:
            goal = "flood_recon"

        return AgentPlan(goal=goal, region=region, plan=steps, planner=self.name)
