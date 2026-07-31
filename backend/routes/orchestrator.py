"""Workflow API.

The workflow engine calls tool functions in-process. Individual tool endpoints
remain available for each teammate to test independently.
"""

from flask import Blueprint, jsonify, request

from core.contracts import http_status
from services.workflow_engine import SCENARIOS, execute_workflow

orc_bp = Blueprint("orchestrator", __name__)
TASKS = {}


@orc_bp.route("/scenarios", methods=["GET"])
def list_scenarios():
    scenarios = [
        {"id": scenario_id, "name": scenario["name"], "steps": scenario["steps"]}
        for scenario_id, scenario in SCENARIOS.items()
    ]
    return jsonify({"status": "success", "data": {"scenarios": scenarios}})


@orc_bp.route("/execute", methods=["POST"])
def execute_scenario():
    data = request.get_json(silent=True) or {}
    scenario_id = data.get("scenario", "")
    params = data.get("params", {})

    result = execute_workflow(scenario_id, params)
    task_id = result.get("data", {}).get("task_id") if isinstance(result.get("data"), dict) else None
    if task_id:
        TASKS[task_id] = result.get("data")
    return jsonify(result), http_status(result)


@orc_bp.route("/tasks/<task_id>", methods=["GET"])
def get_task(task_id):
    task = TASKS.get(task_id)
    if task is None:
        return jsonify({
            "status": "error",
            "data": None,
            "error": {"code": "TASK_NOT_FOUND", "message": f"任务不存在: {task_id}"},
        }), 404
    return jsonify({"status": "success", "data": task, "error": None})
