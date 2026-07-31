"""Natural-language Agent API with a local rule planner by default."""

from flask import Blueprint, jsonify, request

from agents.emergency_agent import execute_agent
from core.contracts import http_status


agent_bp = Blueprint("agent", __name__)
AGENT_TASKS = {}


@agent_bp.route("/execute", methods=["POST"])
def execute_agent_task():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    params = data.get("params", {})
    mode = str(data.get("mode", "hybrid")).lower()

    if not message:
        return jsonify({
            "status": "error",
            "data": None,
            "meta": {"module": "agent"},
            "error": {"code": "AGENT_MESSAGE_REQUIRED", "message": "message 不能为空"},
        }), 400
    if not isinstance(params, dict):
        return jsonify({
            "status": "error",
            "data": None,
            "meta": {"module": "agent"},
            "error": {"code": "AGENT_PARAMS_INVALID", "message": "params 必须是对象"},
        }), 400

    result = execute_agent(message, params, mode)
    task_id = result.get("data", {}).get("task_id") if isinstance(result.get("data"), dict) else None
    if task_id:
        AGENT_TASKS[task_id] = result.get("data")
    return jsonify(result), http_status(result)


@agent_bp.route("/tasks/<task_id>", methods=["GET"])
def get_agent_task(task_id):
    task = AGENT_TASKS.get(task_id)
    if task is None:
        return jsonify({
            "status": "error",
            "data": None,
            "meta": {"module": "agent"},
            "error": {"code": "TASK_NOT_FOUND", "message": f"任务不存在: {task_id}"},
        }), 404
    return jsonify({"status": "success", "data": task, "meta": {"module": "agent"}, "error": None})


@agent_bp.route("/tools", methods=["GET"])
def list_agent_tools():
    from agents.tool_registry import available_tools

    return jsonify({
        "status": "success",
        "data": {"tools": available_tools()},
        "meta": {"module": "agent"},
        "error": None,
    })
