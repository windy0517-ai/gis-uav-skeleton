"""Hybrid Agent: plan with rules now, execute through the shared tool layer."""

from typing import Optional
from uuid import uuid4

from agents.rule_planner import RulePlanner
from agents.schemas import AgentPlan, PlanValidationError, validate_plan
from agents.tool_registry import AGENT_TOOLS
from core.contracts import failure, success
from core.task_context import TaskContext
from services.tool_services import run_tool
from services.workflow_engine import ARTIFACTS


MAX_PLAN_STEPS = 8


def _agent_data(context: TaskContext, plan: AgentPlan, logs: list, final_answer: dict) -> dict:
    return {
        "task_id": context["task_id"],
        "mode": context["mode"],
        "goal": plan.goal,
        "plan": [step.to_dict() for step in plan.plan],
        "state": context["state"],
        "results": context["results"],
        "artifacts": context["artifacts"],
        "final_answer": final_answer,
        "logs": logs,
        "metrics": context["metrics"],
    }


def _final_answer(context: TaskContext, plan: AgentPlan) -> dict:
    risk = context["results"].get("risk_assess", {})
    level = risk.get("risk_level", "medium")
    action = risk.get("recommended_action", "请结合地图结果继续开展重点区域巡检")
    summaries = {
        "flood_rescue": "已完成洪涝重点区域与人员目标分析",
        "damage_assess": "已完成洪涝灾情评估",
        "uav_inspect": "已完成无人机巡检任务规划",
        "decision_report": "已完成决策简报数据整理",
        "flood_recon": "已完成洪涝侦察分析",
    }
    return {
        "summary": summaries.get(plan.goal, "已完成智能任务分析"),
        "risk_level": level,
        "reasons": risk.get("reasons", []),
        "recommended_action": action,
    }


class EmergencyAgent:
    """Coordinates safe tool calls while keeping the existing task context."""

    planner_name = "rule_planner"

    def __init__(self, planner=None):
        self.planner = planner or RulePlanner()

    def execute(
        self,
        message: str,
        params: Optional[dict] = None,
        mode: str = "hybrid",
        task_id: Optional[str] = None,
    ) -> dict:
        if mode != "hybrid":
            return failure("UNSUPPORTED_AGENT_MODE", "当前 Agent 仅支持 hybrid 模式", "agent")

        params = dict(params or {})
        params.setdefault("provider", "mock")
        task_id = task_id or str(uuid4())[:8]
        context = TaskContext(task_id, "agent", params)
        context["mode"] = mode
        logs = []

        raw_plan = self.planner.make_plan(message, {"region": params.get("region", "guigang"), "params": params})
        if isinstance(raw_plan, AgentPlan):
            raw_plan_dict = raw_plan.to_dict()
        else:
            raw_plan_dict = raw_plan

        if raw_plan_dict.get("needs_clarification"):
            context["state"] = "needs_clarification"
            final_answer = {
                "summary": "无法确定任务目标",
                "risk_level": "unknown",
                "reasons": [],
                "recommended_action": raw_plan_dict.get("clarification", "请补充任务描述"),
            }
            plan = AgentPlan(
                goal="",
                region=str(params.get("region", "guigang")),
                plan=[],
                planner=raw_plan_dict.get("planner", self.planner_name),
                needs_clarification=True,
                clarification=final_answer["recommended_action"],
            )
            return success(
                _agent_data(context, plan, logs, final_answer),
                module="agent",
                algorithm=self.planner_name,
                planner=self.planner_name,
                state="needs_clarification",
            )

        try:
            plan = validate_plan(raw_plan_dict, AGENT_TOOLS, MAX_PLAN_STEPS)
        except PlanValidationError as exc:
            context["state"] = "failed"
            return failure(
                "AGENT_PLAN_INVALID",
                str(exc),
                "agent",
                planner=self.planner_name,
                task_id=task_id,
            )

        logs.append({
            "type": "plan_ready",
            "step": "Agent规划",
            "step_id": "agent_plan",
            "message": f"已生成 {len(plan.plan)} 个工具步骤",
        })

        for index, step in enumerate(plan.plan):
            logs.append({
                "type": "step_start",
                "step": step.label,
                "step_id": step.tool_id,
                "progress": round(index / len(plan.plan) * 100),
                "message": f"正在执行: {step.label}",
                "reason": step.reason,
            })
            payload = dict(params)
            payload.update(step.params)
            result = run_tool(step.tool_id, payload, context)
            if result.get("status") != "success":
                context["state"] = "failed"
                logs.append({
                    "type": "step_error",
                    "step": step.label,
                    "step_id": step.tool_id,
                    "message": result.get("error", {}).get("message", "工具执行失败"),
                })
                return {
                    **result,
                    "data": _agent_data(context, plan, logs, {
                        "summary": "智能任务执行失败",
                        "risk_level": "unknown",
                        "reasons": [result.get("error", {}).get("message", "工具执行失败")],
                        "recommended_action": "请检查输入数据或切换到 Mock 模式",
                    }),
                }

            context.record(step.tool_id, result, ARTIFACTS.get(step.tool_id))
            logs.append({
                "type": "step_done",
                "step": step.label,
                "step_id": step.tool_id,
                "message": f"完成: {step.label}",
            })

        context["state"] = "completed"
        answer = _final_answer(context, plan)
        return success(
            _agent_data(context, plan, logs, answer),
            module="agent",
            algorithm=self.planner_name,
            planner=self.planner_name,
            mode=mode,
        )


def execute_agent(message: str, params: Optional[dict] = None, mode: str = "hybrid") -> dict:
    return EmergencyAgent().execute(message, params, mode)
