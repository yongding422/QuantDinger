"""
AI chat API routes (optional).
Currently kept as a minimal compatibility layer for legacy frontend calls.
"""

from flask import Blueprint, request, jsonify

from app.utils.logger import get_logger

logger = get_logger(__name__)

ai_chat_bp = Blueprint('ai_chat', __name__)


@ai_chat_bp.route('/chat/message', methods=['POST'])
def chat_message():
    """
    Send a chat message (legacy compatibility stub).

    ---
    tags:
      - ai-chat
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - message
          properties:
            message:
              type: string
              description: The message content to send
              example: What is the trend for BTC?
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 1
            msg:
              type: string
              example: success
            data:
              type: object
              properties:
                reply:
                  type: string
                  example: Chat API is not implemented yet in local-only mode.
                echo:
                  type: string
                  example: What is the trend for BTC?
      400:
        description: Missing message
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 0
            msg:
              type: string
              example: Missing message
            data:
              type: string
              example: null
    """
    data = request.get_json() or {}
    msg = (data.get('message') or '').strip()
    if not msg:
        return jsonify({'code': 0, 'msg': 'Missing message', 'data': None}), 400
    return jsonify({
        'code': 1,
        'msg': 'success',
        'data': {
            'reply': 'Chat API is not implemented yet in local-only mode.',
            'echo': msg
        }
    })


@ai_chat_bp.route('/chat/history', methods=['GET'])
def get_chat_history():
    """
    Get chat history (legacy compatibility stub).

    ---
    tags:
      - ai-chat
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 1
            msg:
              type: string
              example: success
            data:
              type: array
              items:
                type: object
              example: []
    """
    return jsonify({'code': 1, 'msg': 'success', 'data': []})


@ai_chat_bp.route('/chat/history/save', methods=['POST'])
def save_chat_history():
    """
    Save chat history (legacy compatibility stub).

    ---
    tags:
      - ai-chat
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties: {}
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 1
            msg:
              type: string
              example: success
            data:
              type: string
              example: null
    """
    return jsonify({'code': 1, 'msg': 'success', 'data': None})


