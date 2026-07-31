"""HTTP entry point for the water extraction tool."""
from flask import Blueprint, jsonify, request

from core.contracts import http_status
from services.tool_services import extract_water as extract_water_tool

water_bp = Blueprint('water', __name__)


@water_bp.route('/extract', methods=['POST'])
def extract_water():
    data = request.get_json(silent=True) or {}
    result = extract_water_tool(data)
    return jsonify(result), http_status(result)


@water_bp.route('/status', methods=['GET'])
def status():
    return jsonify({"module": "water_extract", "status": "ready", "provider": "mock_or_real"})
