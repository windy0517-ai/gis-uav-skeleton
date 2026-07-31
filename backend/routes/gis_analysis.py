"""HTTP entry point for MapGIS/local GIS analysis."""
from flask import Blueprint, jsonify, request

from core.contracts import http_status
from services.tool_services import overlay_layers

gis_bp = Blueprint('gis', __name__)


@gis_bp.route('/overlay', methods=['POST'])
def overlay_analysis():
    data = request.get_json(silent=True) or {}
    result = overlay_layers(data)
    return jsonify(result), http_status(result)


@gis_bp.route('/workflows', methods=['GET'])
def list_workflows():
    return jsonify({"status": "success", "data": {
        "workflows": [
            {"id": "600227", "name": "OverlayByLayer", "provider": "IGServer_or_mock"},
            {"id": "600228", "name": "BufferAnalysis", "provider": "IGServer_or_mock"},
        ]
    }})
