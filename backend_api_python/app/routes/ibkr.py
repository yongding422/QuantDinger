"""
Interactive Brokers API Routes

Standalone API endpoints for US stock trading.
"""

from flask import Blueprint, request, jsonify

from app.utils.logger import get_logger
from app.services.ibkr_trading import IBKRClient, IBKRConfig
from app.services.ibkr_trading.client import get_ibkr_client, reset_ibkr_client

logger = get_logger(__name__)

ibkr_bp = Blueprint('ibkr', __name__)

# Global client instance
_client: IBKRClient = None


def _get_client() -> IBKRClient:
    """Get current client instance."""
    global _client
    if _client is None:
        _client = get_ibkr_client()
    return _client


# ==================== Connection Management ====================

@ibkr_bp.route('/status', methods=['GET'])
def get_status():
    """
    Get connection status.
    ---
    tags:
      - ibkr
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                connected:
                  type: boolean
                  example: true
    """
    try:
        client = _get_client()
        return jsonify({
            "success": True,
            "data": client.get_connection_status()
        })
    except Exception as e:
        logger.error(f"Get status failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@ibkr_bp.route('/connect', methods=['POST'])
def connect():
    """
    Connect to TWS / IB Gateway.
    ---
    tags:
      - ibkr
    parameters:
      - in: body
        name: body
        required: false
        schema:
          type: object
          properties:
            host:
              type: string
              description: Host address
              example: 127.0.0.1
            port:
              type: integer
              description: TWS Live=7497, Paper=7496, Gateway Live=4001, Paper=4002
              example: 7497
            clientId:
              type: integer
              description: Client ID for connection
              example: 1
            account:
              type: string
              description: Account ID for multi-account setups
              example: ""
            readonly:
              type: boolean
              description: Readonly mode
              example: false
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: Connected successfully
            data:
              type: object
      400:
        description: Connection failed
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Connection failed. Please check if TWS/Gateway is running.
    """
    global _client
    
    try:
        data = request.get_json() or {}
        
        # Build config
        config = IBKRConfig(
            host=data.get('host', '127.0.0.1'),
            port=int(data.get('port', 7497)),
            client_id=int(data.get('clientId', 1)),
            account=data.get('account', ''),
            readonly=data.get('readonly', False),
        )
        
        # Disconnect existing connection
        if _client is not None and _client.connected:
            _client.disconnect()
        
        # Create new client and connect
        _client = IBKRClient(config)
        success = _client.connect()
        
        if success:
            return jsonify({
                "success": True,
                "message": "Connected successfully",
                "data": _client.get_connection_status()
            })
        else:
            return jsonify({
                "success": False,
                "error": "Connection failed. Please check if TWS/Gateway is running."
            }), 400
            
    except ImportError as e:
        return jsonify({
            "success": False,
            "error": "ib_insync not installed. Run: pip install ib_insync"
        }), 500
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@ibkr_bp.route('/disconnect', methods=['POST'])
def disconnect():
    """
    Disconnect from IBKR.
    ---
    tags:
      - ibkr
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: Disconnected
    """
    global _client
    
    try:
        if _client is not None:
            _client.disconnect()
            _client = None
        
        reset_ibkr_client()
        
        return jsonify({
            "success": True,
            "message": "Disconnected"
        })
    except Exception as e:
        logger.error(f"Disconnect failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==================== Account Queries ====================

@ibkr_bp.route('/account', methods=['GET'])
def get_account():
    """
    Get account information.
    ---
    tags:
      - ibkr
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
      400:
        description: Not connected
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Not connected to IBKR
    """
    try:
        client = _get_client()
        if not client.connected:
            return jsonify({
                "success": False,
                "error": "Not connected to IBKR"
            }), 400
        
        return jsonify({
            "success": True,
            "data": client.get_account_summary()
        })
    except Exception as e:
        logger.error(f"Get account info failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@ibkr_bp.route('/positions', methods=['GET'])
def get_positions():
    """
    Get positions.
    ---
    tags:
      - ibkr
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: array
              items:
                type: object
      400:
        description: Not connected
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Not connected to IBKR
    """
    try:
        client = _get_client()
        if not client.connected:
            return jsonify({
                "success": False,
                "error": "Not connected to IBKR"
            }), 400
        
        positions = client.get_positions()
        return jsonify({
            "success": True,
            "data": positions
        })
    except Exception as e:
        logger.error(f"Get positions failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@ibkr_bp.route('/orders', methods=['GET'])
def get_orders():
    """
    Get open orders.
    ---
    tags:
      - ibkr
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: array
              items:
                type: object
      400:
        description: Not connected
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Not connected to IBKR
    """
    try:
        client = _get_client()
        if not client.connected:
            return jsonify({
                "success": False,
                "error": "Not connected to IBKR"
            }), 400
        
        orders = client.get_open_orders()
        return jsonify({
            "success": True,
            "data": orders
        })
    except Exception as e:
        logger.error(f"Get orders failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==================== Trading ====================

@ibkr_bp.route('/order', methods=['POST'])
def place_order():
    """
    Place an order.
    ---
    tags:
      - ibkr
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - symbol
            - side
            - quantity
          properties:
            symbol:
              type: string
              description: Stock symbol
              example: AAPL
            side:
              type: string
              enum: [buy, sell]
              description: Order side
              example: buy
            quantity:
              type: number
              description: Number of shares
              example: 10
            marketType:
              type: string
              description: Market type
              example: USStock
            orderType:
              type: string
              enum: [market, limit]
              description: Order type
              example: market
            price:
              type: number
              description: Limit price (required for limit orders)
              example: 150.00
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: Order placed
            data:
              type: object
              properties:
                orderId:
                  type: integer
                  example: 123
                filled:
                  type: boolean
                  example: false
                avgPrice:
                  type: number
                  example: 0
                status:
                  type: string
                  example: pending
      400:
        description: Validation error or not connected
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Missing symbol
    """
    try:
        client = _get_client()
        if not client.connected:
            return jsonify({
                "success": False,
                "error": "Not connected to IBKR"
            }), 400
        
        data = request.get_json() or {}
        
        # Validate parameters
        symbol = data.get('symbol')
        side = data.get('side')
        quantity = data.get('quantity')
        
        if not symbol:
            return jsonify({"success": False, "error": "Missing symbol"}), 400
        if not side or side.lower() not in ('buy', 'sell'):
            return jsonify({"success": False, "error": "side must be buy or sell"}), 400
        if not quantity or float(quantity) <= 0:
            return jsonify({"success": False, "error": "quantity must be > 0"}), 400
        
        market_type = data.get('marketType', 'USStock')
        order_type = data.get('orderType', 'market').lower()
        
        # Place order
        if order_type == 'limit':
            price = data.get('price')
            if not price or float(price) <= 0:
                return jsonify({"success": False, "error": "Limit order requires price"}), 400
            
            result = client.place_limit_order(
                symbol=symbol,
                side=side,
                quantity=float(quantity),
                price=float(price),
                market_type=market_type
            )
        else:
            result = client.place_market_order(
                symbol=symbol,
                side=side,
                quantity=float(quantity),
                market_type=market_type
            )
        
        if result.success:
            return jsonify({
                "success": True,
                "message": result.message,
                "data": {
                    "orderId": result.order_id,
                    "filled": result.filled,
                    "avgPrice": result.avg_price,
                    "status": result.status,
                    "raw": result.raw
                }
            })
        else:
            return jsonify({
                "success": False,
                "error": result.message
            }), 400
            
    except Exception as e:
        logger.error(f"Place order failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@ibkr_bp.route('/order/<int:order_id>', methods=['DELETE'])
def cancel_order(order_id: int):
    """
    Cancel an order.
    ---
    tags:
      - ibkr
    parameters:
      - in: path
        name: order_id
        type: integer
        required: true
        description: Order ID
        example: 123
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: Order 123 cancelled
      404:
        description: Order not found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Order 123 not found
    """
    try:
        client = _get_client()
        if not client.connected:
            return jsonify({
                "success": False,
                "error": "Not connected to IBKR"
            }), 400
        
        success = client.cancel_order(order_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Order {order_id} cancelled"
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Order {order_id} not found"
            }), 404
            
    except Exception as e:
        logger.error(f"Cancel order failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==================== Market Data ====================

@ibkr_bp.route('/quote', methods=['GET'])
def get_quote():
    """
    Get real-time quote.
    ---
    tags:
      - ibkr
    parameters:
      - in: query
        name: symbol
        type: string
        required: true
        description: Stock symbol
        example: AAPL
      - in: query
        name: marketType
        type: string
        required: false
        description: Market type
        example: USStock
    responses:
      200:
        description: Success
        schema:
          type: object
      400:
        description: Missing symbol
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Missing symbol
    """
    try:
        client = _get_client()
        if not client.connected:
            return jsonify({
                "success": False,
                "error": "Not connected to IBKR"
            }), 400
        
        symbol = request.args.get('symbol')
        market_type = request.args.get('marketType', 'USStock')
        
        if not symbol:
            return jsonify({"success": False, "error": "Missing symbol"}), 400
        
        quote = client.get_quote(symbol, market_type)
        return jsonify(quote)
        
    except Exception as e:
        logger.error(f"Get quote failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
