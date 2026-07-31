"""Dependency-free schemas and validation for Agent plans."""

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Tuple


class PlanValidationError(ValueError):
    """Raised when a planner returns an unsafe or malformed plan."""


@dataclass
class PlanStep:
    tool_id: str
    label: str
    reason: str = ""
    params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "tool_id": self.tool_id,
            "label": self.label,
            "reason": self.reason,
            "params": dict(self.params),
        }


@dataclass
class AgentPlan:
    goal: str
    region: str
    plan: List[PlanStep]
    planner: str = "rule_planner"
    needs_clarification: bool = False
    clarification: str = ""

    def to_dict(self) -> dict:
        data = {
            "goal": self.goal,
            "region": self.region,
            "plan": [step.to_dict() for step in self.plan],
            "planner": self.planner,
        }
        if self.needs_clarification:
            data["needs_clarification"] = True
            data["clarification"] = self.clarification
        return data


def validate_plan(raw_plan: dict, allowed_tools: Iterable[str], max_steps: int = 8) -> AgentPlan:
    """Normalize and validate a planner response before any tool is called."""
    if not isinstance(raw_plan, dict):
        raise PlanValidationError("Agent 计划必须是 JSON 对象")

    goal = str(raw_plan.get("goal", "")).strip()
    region = str(raw_plan.get("region", "guigang")).strip() or "guigang"
    raw_steps = raw_plan.get("plan")
    if not goal:
        raise PlanValidationError("Agent 计划缺少 goal")
    if not isinstance(raw_steps, list) or not raw_steps:
        raise PlanValidationError("Agent 计划不能为空")
    if len(raw_steps) > max_steps:
        raise PlanValidationError(f"Agent 计划最多允许 {max_steps} 个步骤")

    allowed = set(allowed_tools)
    steps: List[PlanStep] = []
    for index, raw_step in enumerate(raw_steps, start=1):
        if not isinstance(raw_step, dict):
            raise PlanValidationError(f"第 {index} 个步骤格式错误")
        tool_id = str(raw_step.get("tool_id", "")).strip()
        if tool_id not in allowed:
            raise PlanValidationError(f"不允许调用工具: {tool_id or '<empty>'}")
        params = raw_step.get("params", {})
        if params is None:
            params = {}
        if not isinstance(params, dict):
            raise PlanValidationError(f"工具 {tool_id} 的 params 必须是对象")
        if any(not isinstance(key, str) for key in params):
            raise PlanValidationError(f"工具 {tool_id} 的参数名必须是字符串")
        steps.append(PlanStep(
            tool_id=tool_id,
            label=str(raw_step.get("label", tool_id)),
            reason=str(raw_step.get("reason", "")),
            params=params,
        ))

    return AgentPlan(
        goal=goal,
        region=region,
        plan=steps,
        planner=str(raw_plan.get("planner", "rule_planner")),
    )
