"""HTTP entry point for the path planning tool."""
from flask import Blueprint, jsonify, request

from core.contracts import http_status
from services.tool_services import plan_path

path_bp = Blueprint('path', __name__)


@path_bp.route('/plan', methods=['POST'])
def plan_route():
    data = request.get_json(silent=True) or {}
    result = plan_path(data)
    return jsonify(result), http_status(result)


@path_bp.route('/status', methods=['GET'])
def status():
    return jsonify({"module": "path_plan", "status": "ready", "provider": "mock_or_real"})
