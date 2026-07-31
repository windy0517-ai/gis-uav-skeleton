"""HTTP entry point for object detection."""
from flask import Blueprint, jsonify, request

from core.contracts import http_status
from services.tool_services import detect_objects as detect_objects_tool

detect_bp = Blueprint('detect', __name__)


@detect_bp.route('/objects', methods=['POST'])
def detect_objects():
    data = request.get_json(silent=True) or {}
    result = detect_objects_tool(data)
    return jsonify(result), http_status(result)


@detect_bp.route('/status', methods=['GET'])
def status():
    return jsonify({"module": "object_detect", "status": "ready", "provider": "mock_or_real"})
