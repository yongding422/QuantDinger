"""
健康检查路由
"""
from flask import Blueprint, jsonify
from datetime import datetime

health_bp = Blueprint('health', __name__)


@health_bp.route('/', methods=['GET'])
def index():
    """
    API homepage - returns API information.

    ---
    tags:
      - health
    parameters: []
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            name:
              type: string
              example: QuantDinger Python API
            version:
              type: string
              example: 2.0.0
            status:
              type: string
              example: running
            timestamp:
              type: string
              example: 2024-01-15T10:30:00.000000
    """
    return jsonify({
        'name': 'QuantDinger Python API',
        'version': '2.0.0',
        'status': 'running',
        'timestamp': datetime.now().isoformat()
    })


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.

    ---
    tags:
      - health
    parameters: []
    responses:
      200:
        description: Service is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              example: healthy
            timestamp:
              type: string
              example: 2024-01-15T10:30:00.000000
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@health_bp.route('/api/health', methods=['GET'])
def api_health_check():
    """
    Health check endpoint (compatible path for container health checks / reverse proxy probes).

    ---
    tags:
      - health
    parameters: []
    responses:
      200:
        description: Service is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              example: healthy
            timestamp:
              type: string
              example: 2024-01-15T10:30:00.000000
    """
    return health_check()
