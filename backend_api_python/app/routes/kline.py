"""
K线数据 API 路由
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import traceback

from app.services.kline import KlineService
from app.utils.logger import get_logger

logger = get_logger(__name__)

kline_bp = Blueprint('kline', __name__)
kline_service = KlineService()


@kline_bp.route('/kline', methods=['GET'])
def get_kline():
    """
    Get K-line (candlestick) data.

    ---
    tags:
      - indicator
    parameters:
      - in: query
        name: market
        required: false
        type: string
        description: Market type (Crypto, USStock, Forex, Futures)
        default: USStock
      - in: query
        name: symbol
        required: true
        type: string
        description: Symbol/ticker
        example: AAPL
      - in: query
        name: timeframe
        required: false
        type: string
        description: Timeframe (1m, 5m, 15m, 30m, 1H, 4H, 1D, 1W)
        default: 1D
      - in: query
        name: limit
        required: false
        type: integer
        description: Number of data points
        default: 300
      - in: query
        name: before_time
        required: false
        type: integer
        description: Get data before this Unix timestamp
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
                properties:
                  timestamp:
                    type: integer
                  open:
                    type: number
                  high:
                    type: number
                  low:
                    type: number
                  close:
                    type: number
                  volume:
                    type: number
      400:
        description: Missing symbol parameter
    """
    try:
        # 强制 GET, 使用 request.args
        market = request.args.get('market', 'USStock')
        symbol = request.args.get('symbol', '')
        timeframe = request.args.get('timeframe', '1D')
        limit = int(request.args.get('limit', 300))
        before_time = request.args.get('before_time') or request.args.get('beforeTime')
        
        if before_time:
            before_time = int(before_time)
        
        if not symbol:
            return jsonify({
                'code': 0,
                'msg': 'Missing symbol parameter',
                'data': None
            }), 400
        
        logger.info(f"Requesting K-lines: {market}:{symbol}, timeframe={timeframe}, limit={limit}")
        
        klines = kline_service.get_kline(
            market=market,
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
            before_time=before_time
        )
        
        if not klines:
            # 针对特定情况给出更详细的提示
            msg = 'No data found'
            if market == 'Forex' and timeframe == '1m':
                msg = 'Forex 1-minute data requires Tiingo paid subscription'
            elif market == 'Forex' and timeframe in ('1W', '1M'):
                msg = 'No weekly/monthly data available for this period'
            return jsonify({
                'code': 0,
                'msg': msg,
                'data': [],
                'hint': 'tiingo_subscription' if (market == 'Forex' and timeframe == '1m') else None
            })
        
        return jsonify({
            'code': 1,
            'msg': 'success',
            'data': klines
        })
        
    except Exception as e:
        logger.error(f"Failed to fetch K-lines: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'code': 0,
            'msg': f'Failed to fetch kline data: {str(e)}',
            'data': None
        }), 500


@kline_bp.route('/price', methods=['GET'])
def get_price():
    """
    Get latest price for a symbol.

    ---
    tags:
      - indicator
    parameters:
      - in: query
        name: market
        required: false
        type: string
        description: Market type
        default: USStock
      - in: query
        name: symbol
        required: true
        type: string
        description: Symbol/ticker
        example: AAPL
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
                price:
                  type: number
                change:
                  type: number
                changePercent:
                  type: number
      400:
        description: Missing symbol parameter
    """
    try:
        market = request.args.get('market', 'USStock')
        symbol = request.args.get('symbol', '')
        
        if not symbol:
            return jsonify({
                'code': 0,
                'msg': 'Missing symbol parameter',
                'data': None
            }), 400
        
        price_data = kline_service.get_latest_price(market, symbol)
        
        if not price_data:
            return jsonify({
                'code': 0,
                'msg': 'No price data found',
                'data': None
            })
        
        return jsonify({
            'code': 1,
            'msg': 'success',
            'data': price_data
        })
        
    except Exception as e:
        logger.error(f"Failed to fetch price: {str(e)}")
        return jsonify({
            'code': 0,
            'msg': f'Failed to fetch price: {str(e)}',
            'data': None
        }), 500

