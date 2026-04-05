"""
MetaTrader 5 Trading API Routes

Provides REST API for MT5 trading operations.
"""

from flask import Blueprint, request, jsonify

from app.utils.logger import get_logger

logger = get_logger(__name__)

mt5_bp = Blueprint("mt5", __name__)

# Lazy import MT5 client to avoid errors if not installed
MT5Client = None
MT5Config = None
_client = None


def _ensure_mt5_imports():
    """Ensure MT5 modules are imported."""
    global MT5Client, MT5Config
    if MT5Client is None or MT5Config is None:
        try:
            from app.services.mt5_trading import MT5Client as _MT5Client, MT5Config as _MT5Config
            MT5Client = _MT5Client
            MT5Config = _MT5Config
        except ImportError as e:
            raise ImportError(
                "MT5 trading requires MetaTrader5 library. "
                "Run: pip install MetaTrader5\n"
                "Note: This library only works on Windows."
            ) from e


def _get_client():
    """Get or create MT5 client instance."""
    global _client
    if _client is None:
        _ensure_mt5_imports()
        _client = MT5Client()
    return _client


# ==================== Connection Management ====================

@mt5_bp.route("/status", methods=["GET"])
def get_status():
    """
    Get MT5 connection status.
    ---
    tags:
      - mt5
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            connected:
              type: boolean
              example: true
            error:
              type: string
              example: ""
    """
    try:
        _ensure_mt5_imports()
        client = _get_client()
        status = client.get_connection_status()
        return jsonify(status)
    except ImportError as e:
        return jsonify({
            "connected": False,
            "error": str(e),
            "hint": "MetaTrader5 library is not installed or not on Windows"
        })
    except Exception as e:
        logger.error(f"Get MT5 status failed: {e}")
        return jsonify({"connected": False, "error": str(e)})


@mt5_bp.route("/connect", methods=["POST"])
def connect():
    """
    Connect to MT5 terminal.
    ---
    tags:
      - mt5
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - login
            - password
            - server
          properties:
            login:
              type: integer
              description: MT5 account number
              example: 12345678
            password:
              type: string
              description: MT5 password
              example: "xxx"
            server:
              type: string
              description: Broker server
              example: ICMarkets-Demo
            terminal_path:
              type: string
              description: Path to terminal64.exe
              example: ""
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
              example: Connected to MT5
            account:
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
              example: Failed to connect to MT5
    """
    global _client
    
    try:
        _ensure_mt5_imports()
        
        data = request.get_json() or {}
        
        login = data.get("login") or data.get("mt5_login")
        password = data.get("password") or data.get("mt5_password")
        server = data.get("server") or data.get("mt5_server")
        terminal_path = data.get("terminal_path") or data.get("mt5_terminal_path") or ""
        
        if not login or not password or not server:
            return jsonify({
                "success": False,
                "error": "Missing required fields: login, password, server"
            }), 400
        
        config = MT5Config(
            login=int(login),
            password=str(password),
            server=str(server),
            terminal_path=str(terminal_path),
        )
        
        # Create new client with config
        _client = MT5Client(config)
        
        if _client.connect():
            account_info = _client.get_account_info()
            return jsonify({
                "success": True,
                "message": "Connected to MT5",
                "account": account_info
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to connect to MT5. Check credentials and ensure terminal is running."
            }), 400
            
    except ImportError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    except Exception as e:
        logger.error(f"MT5 connect failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@mt5_bp.route("/disconnect", methods=["POST"])
def disconnect():
    """
    Disconnect from MT5 terminal.
    ---
    tags:
      - mt5
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
        return jsonify({"success": True, "message": "Disconnected"})
    except Exception as e:
        logger.error(f"MT5 disconnect failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== Account Queries ====================

@mt5_bp.route("/account", methods=["GET"])
def get_account():
    """
    Get account information.
    ---
    tags:
      - mt5
    responses:
      200:
        description: Success
        schema:
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
              example: Not connected to MT5
    """
    try:
        client = _get_client()
        if not client.connected:
            return jsonify({"success": False, "error": "Not connected to MT5"}), 400
        
        info = client.get_account_info()
        return jsonify(info)
    except Exception as e:
        logger.error(f"Get MT5 account failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@mt5_bp.route("/positions", methods=["GET"])
def get_positions():
    """
    Get open positions.
    ---
    tags:
      - mt5
    parameters:
      - in: query
        name: symbol
        type: string
        required: false
        description: Filter by symbol
        example: EURUSD
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            positions:
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
              example: Not connected to MT5
    """
    try:
        client = _get_client()
        if not client.connected:
            return jsonify({"success": False, "error": "Not connected to MT5"}), 400
        
        symbol = request.args.get("symbol")
        positions = client.get_positions(symbol=symbol)
        return jsonify({"success": True, "positions": positions})
    except Exception as e:
        logger.error(f"Get MT5 positions failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@mt5_bp.route("/orders", methods=["GET"])
def get_orders():
    """
    Get pending orders.
    ---
    tags:
      - mt5
    parameters:
      - in: query
        name: symbol
        type: string
        required: false
        description: Filter by symbol
        example: EURUSD
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            orders:
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
              example: Not connected to MT5
    """
    try:
        client = _get_client()
        if not client.connected:
            return jsonify({"success": False, "error": "Not connected to MT5"}), 400
        
        symbol = request.args.get("symbol")
        orders = client.get_orders(symbol=symbol)
        return jsonify({"success": True, "orders": orders})
    except Exception as e:
        logger.error(f"Get MT5 orders failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@mt5_bp.route("/symbols", methods=["GET"])
def get_symbols():
    """
    Get available symbols.
    ---
    tags:
      - mt5
    parameters:
      - in: query
        name: group
        type: string
        required: false
        description: Symbol group filter
        example: "*"
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            symbols:
              type: array
              items:
                type: string
    """
    try:
        client = _get_client()
        if not client.connected:
            return jsonify({"success": False, "error": "Not connected to MT5"}), 400
        
        group = request.args.get("group", "*")
        symbols = client.get_symbols(group=group)
        return jsonify({"success": True, "symbols": symbols})
    except Exception as e:
        logger.error(f"Get MT5 symbols failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== Trading ====================

@mt5_bp.route("/order", methods=["POST"])
def place_order():
    """
    Place an order.
    ---
    tags:
      - mt5
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - symbol
            - side
            - volume
          properties:
            symbol:
              type: string
              description: Trading symbol
              example: EURUSD
            side:
              type: string
              enum: [buy, sell]
              description: Order side
              example: buy
            volume:
              type: number
              description: Lot size
              example: 0.1
            orderType:
              type: string
              enum: [market, limit]
              description: Order type
              example: market
            price:
              type: number
              description: Limit price (required for limit orders)
              example: 1.0800
            comment:
              type: string
              description: Order comment
              example: QuantDinger
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            order_id:
              type: integer
              example: 123
            deal_id:
              type: integer
              example: 0
            filled:
              type: boolean
              example: false
            price:
              type: number
              example: 0
            status:
              type: string
              example: pending
            message:
              type: string
              example: Order placed
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
              example: Missing required fields
    """
    try:
        client = _get_client()
        if not client.connected:
            return jsonify({"success": False, "error": "Not connected to MT5"}), 400
        
        data = request.get_json() or {}
        
        symbol = data.get("symbol")
        side = data.get("side")
        volume = data.get("volume") or data.get("quantity")
        order_type = data.get("orderType", "market").lower()
        price = data.get("price")
        comment = data.get("comment", "QuantDinger")
        
        if not symbol or not side or not volume:
            return jsonify({
                "success": False,
                "error": "Missing required fields: symbol, side, volume"
            }), 400
        
        if order_type == "limit":
            if not price:
                return jsonify({
                    "success": False,
                    "error": "Limit order requires price"
                }), 400
            result = client.place_limit_order(
                symbol=symbol,
                side=side,
                volume=float(volume),
                price=float(price),
                comment=comment,
            )
        else:
            result = client.place_market_order(
                symbol=symbol,
                side=side,
                volume=float(volume),
                comment=comment,
            )
        
        if result.success:
            return jsonify({
                "success": True,
                "order_id": result.order_id,
                "deal_id": result.deal_id,
                "filled": result.filled,
                "price": result.price,
                "status": result.status,
                "message": result.message,
            })
        else:
            return jsonify({
                "success": False,
                "error": result.message
            }), 400
            
    except Exception as e:
        logger.error(f"MT5 place order failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@mt5_bp.route("/close", methods=["POST"])
def close_position():
    """
    Close a position.
    ---
    tags:
      - mt5
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - ticket
          properties:
            ticket:
              type: integer
              description: Position ticket
              example: 123456789
            volume:
              type: number
              description: Partial close volume (optional)
              example: 0.1
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            order_id:
              type: integer
              example: 123
            deal_id:
              type: integer
              example: 456
            filled:
              type: boolean
              example: true
            price:
              type: number
              example: 1.0800
            message:
              type: string
              example: Position closed
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
              example: Missing required field: ticket
    """
    try:
        client = _get_client()
        if not client.connected:
            return jsonify({"success": False, "error": "Not connected to MT5"}), 400
        
        data = request.get_json() or {}
        
        ticket = data.get("ticket")
        volume = data.get("volume")
        
        if not ticket:
            return jsonify({
                "success": False,
                "error": "Missing required field: ticket"
            }), 400
        
        result = client.close_position(
            ticket=int(ticket),
            volume=float(volume) if volume else None,
        )
        
        if result.success:
            return jsonify({
                "success": True,
                "order_id": result.order_id,
                "deal_id": result.deal_id,
                "filled": result.filled,
                "price": result.price,
                "message": result.message,
            })
        else:
            return jsonify({
                "success": False,
                "error": result.message
            }), 400
            
    except Exception as e:
        logger.error(f"MT5 close position failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@mt5_bp.route("/order/<int:ticket>", methods=["DELETE"])
def cancel_order(ticket: int):
    """
    Cancel a pending order.
    ---
    tags:
      - mt5
    parameters:
      - in: path
        name: ticket
        type: integer
        required: true
        description: Order ticket
        example: 123456789
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
              example: Order 123456789 cancelled
      400:
        description: Failed to cancel
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: Failed to cancel order
    """
    try:
        client = _get_client()
        if not client.connected:
            return jsonify({"success": False, "error": "Not connected to MT5"}), 400
        
        if client.cancel_order(ticket):
            return jsonify({"success": True, "message": f"Order {ticket} cancelled"})
        else:
            return jsonify({"success": False, "error": "Failed to cancel order"}), 400
            
    except Exception as e:
        logger.error(f"MT5 cancel order failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== Market Data ====================

@mt5_bp.route("/quote", methods=["GET"])
def get_quote():
    """
    Get real-time quote.
    ---
    tags:
      - mt5
    parameters:
      - in: query
        name: symbol
        type: string
        required: true
        description: Trading symbol
        example: EURUSD
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
              example: Missing symbol parameter
    """
    try:
        client = _get_client()
        if not client.connected:
            return jsonify({"success": False, "error": "Not connected to MT5"}), 400
        
        symbol = request.args.get("symbol")
        if not symbol:
            return jsonify({"success": False, "error": "Missing symbol parameter"}), 400
        
        quote = client.get_quote(symbol)
        return jsonify(quote)
        
    except Exception as e:
        logger.error(f"MT5 get quote failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
