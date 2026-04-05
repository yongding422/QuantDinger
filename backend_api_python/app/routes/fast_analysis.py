"""
Fast Analysis API Routes

New high-performance analysis endpoints that replace the slow multi-agent system.
"""
from flask import Blueprint, request, jsonify, g
import threading
import time

from app.utils.auth import login_required
from app.utils.logger import get_logger
from app.services.fast_analysis import get_fast_analysis_service
from app.services.analysis_memory import get_analysis_memory
from app.services.billing_service import get_billing_service

logger = get_logger(__name__)

fast_analysis_bp = Blueprint('fast_analysis', __name__)

# In-memory in-flight guard to avoid duplicate analysis charges caused by rapid repeated clicks.
_analysis_inflight_lock = threading.Lock()
_analysis_inflight = {}  # key -> expire_ts


def _try_refund_credits(user_id: int, amount: int, remark: str):
    """Best-effort async refund when task fails after pre-charge."""
    try:
        if int(amount or 0) <= 0:
            return
        billing = get_billing_service()
        billing.add_credits(
            user_id=int(user_id),
            amount=int(amount),
            action='refund',
            remark=remark
        )
    except Exception as e:
        logger.error(f"Async auto refund failed: {e}", exc_info=True)


def _run_async_analysis_task(task_memory_id: int, market: str, symbol: str, language: str,
                             model: str, timeframe: str, user_id: int, inflight_key: str,
                             credits_charged: int = 0):
    """
    Background worker: execute analysis and update pending history record.
    """
    try:
        service = get_fast_analysis_service()
        memory = get_analysis_memory()
        result = service.analyze(
            market=market,
            symbol=symbol,
            language=language,
            model=model,
            timeframe=timeframe,
            user_id=user_id
        )
        memory.finalize_pending_task(task_memory_id, result)
        if result.get("error"):
            _try_refund_credits(
                user_id=int(user_id),
                amount=int(credits_charged or 0),
                remark=f'Auto refund: async fast-analysis failed ({market}:{symbol}:{timeframe})'
            )

        # analyze() already stores a separate memory row; remove it to avoid duplicates.
        auto_memory_id = result.get("memory_id")
        if auto_memory_id and int(auto_memory_id) != int(task_memory_id):
            try:
                memory.delete_history(int(auto_memory_id), user_id=user_id)
            except Exception:
                pass
    except Exception as e:
        logger.error(f"Async analysis task failed: {e}", exc_info=True)
        _try_refund_credits(
            user_id=int(user_id),
            amount=int(credits_charged or 0),
            remark=f'Auto refund: async fast-analysis exception ({market}:{symbol}:{timeframe})'
        )
        try:
            get_analysis_memory().fail_pending_task(task_memory_id, str(e))
        except Exception:
            pass
    finally:
        try:
            _release_inflight(inflight_key)
        except Exception:
            pass


def _build_inflight_key(user_id: int, market: str, symbol: str, timeframe: str) -> str:
    return f"{int(user_id)}|{str(market or '').strip().upper()}|{str(symbol or '').strip().upper()}|{str(timeframe or '').strip().upper()}"


def _acquire_inflight(key: str, ttl_sec: int = 90) -> bool:
    now = time.time()
    with _analysis_inflight_lock:
        # Cleanup stale entries
        stale = [k for k, exp in _analysis_inflight.items() if float(exp) <= now]
        for k in stale[:1024]:
            _analysis_inflight.pop(k, None)
        if key in _analysis_inflight and float(_analysis_inflight.get(key) or 0) > now:
            return False
        _analysis_inflight[key] = now + int(ttl_sec)
        return True


def _release_inflight(key: str):
    with _analysis_inflight_lock:
        _analysis_inflight.pop(key, None)


@fast_analysis_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    """
    Perform fast AI analysis for any symbol.

    ---
    tags:
      - fast-analysis
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - market
            - symbol
          properties:
            market:
              type: string
              description: Market type (Crypto, USStock, Forex, etc.)
              example: Crypto
            symbol:
              type: string
              description: Symbol to analyze (e.g., BTC/USDT, AAPL)
              example: BTC/USDT
            language:
              type: string
              description: Response language
              example: en-US
            model:
              type: string
              description: AI model to use
              example: openai/gpt-4o
            timeframe:
              type: string
              description: Timeframe for analysis
              example: 1D
            async_submit:
              type: boolean
              description: Submit analysis asynchronously
              example: false
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
                analysis:
                  type: string
                  example: Bullish trend detected...
                memory_id:
                  type: integer
                  example: 123
                credits_charged:
                  type: integer
                  example: 10
                remaining_credits:
                  type: number
                  example: 90.0
      400:
        description: Missing required fields or insufficient credits
      401:
        description: Unauthorized
      429:
        description: Analysis already in progress
      500:
        description: Analysis error
    security:
      - Bearer: []
    """
    try:
        data = request.get_json() or {}
        
        market = (data.get('market') or '').strip()
        symbol = (data.get('symbol') or '').strip()
        language = data.get('language', 'en-US')
        model = data.get('model')
        timeframe = data.get('timeframe', '1D')
        async_submit = bool(data.get('async_submit', False))
        
        if not market or not symbol:
            return jsonify({
                'code': 0,
                'msg': 'market and symbol are required',
                'data': None
            }), 400
        
        # Get current user's ID to associate analysis with user
        user_id = getattr(g, 'user_id', None)
        if not user_id:
            return jsonify({'code': 0, 'msg': 'Unauthorized', 'data': None}), 401

        inflight_key = _build_inflight_key(user_id, market, symbol, timeframe)
        if not _acquire_inflight(inflight_key, ttl_sec=90):
            return jsonify({
                'code': 0,
                'msg': 'Analysis already in progress for this symbol/timeframe. Please wait.',
                'data': {'in_progress': True}
            }), 429

        # Billing / credits (best-effort, consistent with polymarket deep analysis)
        credits_charged = 0
        remaining_credits = None
        billing_consumed = False
        billing = None
        try:
            billing = get_billing_service()
            if billing.is_billing_enabled():
                credits_charged = int(billing.get_feature_cost('ai_analysis') or 0)
                if credits_charged > 0:
                    ok, msg = billing.check_and_consume(
                        user_id=int(user_id),
                        feature='ai_analysis',
                        reference_id=f"fast_analysis_{market}:{symbol}:{timeframe}"
                    )
                    if not ok:
                        # Standardize insufficient credits message
                        if str(msg or "").startswith('insufficient_credits'):
                            # Format: insufficient_credits:<current>:<cost>
                            parts = str(msg).split(':')
                            cur = float(parts[1]) if len(parts) >= 2 else 0.0
                            req = float(parts[2]) if len(parts) >= 3 else float(credits_charged)
                            return jsonify({
                                'code': 0,
                                'msg': 'Insufficient credits',
                                'data': {
                                    'required': req,
                                    'current': cur,
                                    'shortage': max(0.0, req - cur),
                                }
                            }), 400
                        return jsonify({'code': 0, 'msg': f'Failed to deduct credits: {msg}', 'data': None}), 500
                    billing_consumed = True
                    # Query remaining credits after successful consumption
                    try:
                        remaining_credits = float(billing.get_user_credits(int(user_id)))
                    except Exception:
                        remaining_credits = None
        except Exception as e:
            # Billing failure should not crash analysis by default, but should be visible in logs.
            logger.warning(f"Billing check failed (skipped): {e}", exc_info=True)
        
        service = get_fast_analysis_service()

        # Async submit mode: record "processing" immediately and return task id.
        if async_submit:
            memory = get_analysis_memory()
            pending_id = memory.create_pending_task(
                market=market,
                symbol=symbol,
                language=language,
                model=model or "",
                timeframe=timeframe,
                user_id=user_id
            )
            if not pending_id:
                return jsonify({'code': 0, 'msg': 'Failed to create analysis task', 'data': None}), 500

            t = threading.Thread(
                target=_run_async_analysis_task,
                args=(int(pending_id), market, symbol, language, model, timeframe, int(user_id), inflight_key, int(credits_charged or 0)),
                daemon=True
            )
            t.start()
            # worker owns inflight release
            inflight_key = None

            return jsonify({
                'code': 1,
                'msg': 'submitted',
                'data': {
                    'task_id': int(pending_id),
                    'memory_id': int(pending_id),
                    'status': 'processing',
                    'market': market,
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'credits_charged': credits_charged,
                    'remaining_credits': remaining_credits,
                }
            })

        result = service.analyze(
            market=market,
            symbol=symbol,
            language=language,
            model=model,
            timeframe=timeframe,
            user_id=user_id
        )
        
        if result.get('error'):
            # Best-effort refund if we already charged but analysis failed.
            if billing_consumed and billing and credits_charged > 0:
                try:
                    billing.add_credits(
                        user_id=int(user_id),
                        amount=int(credits_charged),
                        action='refund',
                        remark=f'Auto refund: fast-analysis failed ({market}:{symbol}:{timeframe})'
                    )
                    remaining_credits = float(billing.get_user_credits(int(user_id)))
                except Exception as re:
                    logger.error(f"Auto refund failed: {re}", exc_info=True)
            return jsonify({
                'code': 0,
                'msg': result['error'],
                'data': result
            }), 500
        
        # memory_id is already set in service.analyze() -> _store_analysis_memory()
        # No need to store again here (would create duplicates)
        
        return jsonify({
            'code': 1,
            'msg': 'success',
            'data': {
                **(result or {}),
                'credits_charged': credits_charged,
                'remaining_credits': remaining_credits,
            }
        })
        
    except Exception as e:
        # Best-effort refund on unexpected error after charge.
        try:
            if 'billing_consumed' in locals() and billing_consumed and 'billing' in locals() and billing and credits_charged > 0 and 'user_id' in locals() and user_id:
                billing.add_credits(
                    user_id=int(user_id),
                    amount=int(credits_charged),
                    action='refund',
                    remark=f'Auto refund: fast-analysis exception ({market}:{symbol}:{timeframe})'
                )
        except Exception:
            pass
        logger.error(f"Fast analysis API failed: {e}", exc_info=True)
        return jsonify({
            'code': 0,
            'msg': str(e),
            'data': None
        }), 500
    finally:
        try:
            if 'inflight_key' in locals() and inflight_key:
                _release_inflight(inflight_key)
        except Exception:
            pass


@fast_analysis_bp.route('/analyze-legacy', methods=['POST'])
@login_required
def analyze_legacy():
    """
    Fast analysis with legacy format output (backward compatibility).

    ---
    tags:
      - fast-analysis
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - market
            - symbol
          properties:
            market:
              type: string
              description: Market type (Crypto, USStock, Forex, etc.)
              example: Crypto
            symbol:
              type: string
              description: Symbol to analyze (e.g., BTC/USDT, AAPL)
              example: BTC/USDT
            language:
              type: string
              description: Response language
              example: en-US
            model:
              type: string
              description: AI model to use
              example: openai/gpt-4o
            timeframe:
              type: string
              description: Timeframe for analysis
              example: 1D
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
                analysis:
                  type: string
                  example: Multi-agent analysis result...
                credits_charged:
                  type: integer
                  example: 10
                remaining_credits:
                  type: number
                  example: 90.0
      400:
        description: Missing required fields or insufficient credits
      401:
        description: Unauthorized
      429:
        description: Analysis already in progress
      500:
        description: Analysis error
    security:
      - Bearer: []
    """
    try:
        data = request.get_json() or {}
        
        market = (data.get('market') or '').strip()
        symbol = (data.get('symbol') or '').strip()
        language = data.get('language', 'en-US')
        model = data.get('model')
        timeframe = data.get('timeframe', '1D')
        
        if not market or not symbol:
            return jsonify({
                'code': 0,
                'msg': 'market and symbol are required',
                'data': None
            }), 400

        # Billing / credits (same behavior as /analyze)
        user_id = getattr(g, 'user_id', None)
        if not user_id:
            return jsonify({'code': 0, 'msg': 'Unauthorized', 'data': None}), 401

        inflight_key = _build_inflight_key(user_id, market, symbol, timeframe)
        if not _acquire_inflight(inflight_key, ttl_sec=90):
            return jsonify({
                'code': 0,
                'msg': 'Analysis already in progress for this symbol/timeframe. Please wait.',
                'data': {'in_progress': True}
            }), 429

        credits_charged = 0
        remaining_credits = None
        billing_consumed = False
        billing = None
        try:
            billing = get_billing_service()
            if billing.is_billing_enabled():
                credits_charged = int(billing.get_feature_cost('ai_analysis') or 0)
                if credits_charged > 0:
                    ok, msg = billing.check_and_consume(
                        user_id=int(user_id),
                        feature='ai_analysis',
                        reference_id=f"fast_analysis_legacy_{market}:{symbol}:{timeframe}"
                    )
                    if not ok:
                        if str(msg or "").startswith('insufficient_credits'):
                            parts = str(msg).split(':')
                            cur = float(parts[1]) if len(parts) >= 2 else 0.0
                            req = float(parts[2]) if len(parts) >= 3 else float(credits_charged)
                            return jsonify({
                                'code': 0,
                                'msg': 'Insufficient credits',
                                'data': {
                                    'required': req,
                                    'current': cur,
                                    'shortage': max(0.0, req - cur),
                                }
                            }), 400
                        return jsonify({'code': 0, 'msg': f'Failed to deduct credits: {msg}', 'data': None}), 500
                    billing_consumed = True
                    try:
                        remaining_credits = float(billing.get_user_credits(int(user_id)))
                    except Exception:
                        remaining_credits = None
        except Exception as e:
            logger.warning(f"Billing check failed (skipped): {e}", exc_info=True)
        
        service = get_fast_analysis_service()
        result = service.analyze_legacy_format(
            market=market,
            symbol=symbol,
            language=language,
            model=model,
            timeframe=timeframe
        )
        
        if result.get('error'):
            if billing_consumed and billing and credits_charged > 0:
                try:
                    billing.add_credits(
                        user_id=int(user_id),
                        amount=int(credits_charged),
                        action='refund',
                        remark=f'Auto refund: fast-analysis-legacy failed ({market}:{symbol}:{timeframe})'
                    )
                    remaining_credits = float(billing.get_user_credits(int(user_id)))
                except Exception as re:
                    logger.error(f"Auto refund failed (legacy): {re}", exc_info=True)
            return jsonify({
                'code': 0,
                'msg': result['error'],
                'data': result
            }), 500
        
        return jsonify({
            'code': 1,
            'msg': 'success',
            'data': {
                **(result or {}),
                'credits_charged': credits_charged,
                'remaining_credits': remaining_credits,
            }
        })
        
    except Exception as e:
        try:
            if 'billing_consumed' in locals() and billing_consumed and 'billing' in locals() and billing and credits_charged > 0 and 'user_id' in locals() and user_id:
                billing.add_credits(
                    user_id=int(user_id),
                    amount=int(credits_charged),
                    action='refund',
                    remark=f'Auto refund: fast-analysis-legacy exception ({market}:{symbol}:{timeframe})'
                )
        except Exception:
            pass
        logger.error(f"Fast analysis legacy API failed: {e}", exc_info=True)
        return jsonify({
            'code': 0,
            'msg': str(e),
            'data': None
        }), 500
    finally:
        try:
            if 'inflight_key' in locals() and inflight_key:
                _release_inflight(inflight_key)
        except Exception:
            pass


@fast_analysis_bp.route('/history', methods=['GET'])
@login_required
def get_history():
    """
    Get analysis history for a specific symbol.

    ---
    tags:
      - fast-analysis
    parameters:
      - in: query
        name: market
        type: string
        required: true
        description: Market type
        example: Crypto
      - in: query
        name: symbol
        type: string
        required: true
        description: Symbol
        example: BTC/USDT
      - in: query
        name: days
        type: integer
        required: false
        description: Number of days to look back
        default: 7
        example: 7
      - in: query
        name: limit
        type: integer
        required: false
        description: Maximum number of results (max 50)
        default: 10
        example: 10
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
                items:
                  type: array
                  items:
                    type: object
                total:
                  type: integer
                  example: 5
      400:
        description: Missing required query parameters
      401:
        description: Unauthorized
      500:
        description: Server error
    security:
      - Bearer: []
    """
    try:
        market = request.args.get('market', '').strip()
        symbol = request.args.get('symbol', '').strip()
        days = int(request.args.get('days', 7))
        limit = min(int(request.args.get('limit', 10)), 50)
        
        if not market or not symbol:
            return jsonify({
                'code': 0,
                'msg': 'market and symbol are required',
                'data': None
            }), 400
        
        memory = get_analysis_memory()
        history = memory.get_recent(market, symbol, days, limit)
        
        return jsonify({
            'code': 1,
            'msg': 'success',
            'data': {
                'items': history,
                'total': len(history)
            }
        })
        
    except Exception as e:
        logger.error(f"Get history failed: {e}")
        return jsonify({
            'code': 0,
            'msg': str(e),
            'data': None
        }), 500


@fast_analysis_bp.route('/history/all', methods=['GET'])
@login_required
def get_all_history():
    """
    Get all analysis history with pagination.

    ---
    tags:
      - fast-analysis
    parameters:
      - in: query
        name: page
        type: integer
        required: false
        description: Page number (1-indexed)
        default: 1
        example: 1
      - in: query
        name: pagesize
        type: integer
        required: false
        description: Items per page (max 50)
        default: 20
        example: 20
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
                list:
                  type: array
                  items:
                    type: object
                total:
                  type: integer
                  example: 100
                page:
                  type: integer
                  example: 1
                pagesize:
                  type: integer
                  example: 20
      401:
        description: Unauthorized
      500:
        description: Server error
    security:
      - Bearer: []
    """
    try:
        page = int(request.args.get('page', 1))
        pagesize = min(int(request.args.get('pagesize', 20)), 50)
        
        # Get current user's ID to filter history
        user_id = getattr(g, 'user_id', None)
        
        memory = get_analysis_memory()
        result = memory.get_all_history(user_id=user_id, page=page, page_size=pagesize)
        
        return jsonify({
            'code': 1,
            'msg': 'success',
            'data': {
                'list': result['items'],
                'total': result['total'],
                'page': result['page'],
                'pagesize': result['page_size']
            }
        })
        
    except Exception as e:
        logger.error(f"Get all history failed: {e}")
        return jsonify({
            'code': 0,
            'msg': str(e),
            'data': None
        }), 500


@fast_analysis_bp.route('/history/<int:memory_id>', methods=['DELETE'])
@login_required
def delete_history(memory_id: int):
    """
    Delete a specific analysis history record.

    ---
    tags:
      - fast-analysis
    parameters:
      - in: path
        name: memory_id
        type: integer
        required: true
        description: ID of the history record to delete
        example: 123
    responses:
      200:
        description: Deleted successfully
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 1
            msg:
              type: string
              example: Deleted successfully
            data:
              type: string
              example: null
      401:
        description: Unauthorized
      404:
        description: Record not found or no permission
      500:
        description: Server error
    security:
      - Bearer: []
    """
    try:
        # Get current user's ID to ensure they can only delete their own records
        user_id = getattr(g, 'user_id', None)
        
        memory = get_analysis_memory()
        success = memory.delete_history(memory_id, user_id=user_id)
        
        if success:
            return jsonify({
                'code': 1,
                'msg': 'Deleted successfully',
                'data': None
            })
        else:
            return jsonify({
                'code': 0,
                'msg': 'Record not found or no permission',
                'data': None
            }), 404
        
    except Exception as e:
        logger.error(f"Delete history failed: {e}")
        return jsonify({
            'code': 0,
            'msg': str(e),
            'data': None
        }), 500


@fast_analysis_bp.route('/feedback', methods=['POST'])
@login_required
def submit_feedback():
    """
    Submit user feedback on an analysis.

    ---
    tags:
      - fast-analysis
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - memory_id
            - feedback
          properties:
            memory_id:
              type: integer
              description: ID of the analysis record
              example: 123
            feedback:
              type: string
              description: Feedback type
              enum:
                - helpful
                - not_helpful
                - accurate
                - inaccurate
              example: helpful
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
      400:
        description: Missing required fields or invalid feedback type
      401:
        description: Unauthorized
      500:
        description: Server error
    security:
      - Bearer: []
    """
    try:
        data = request.get_json() or {}
        
        memory_id = int(data.get('memory_id', 0))
        feedback = (data.get('feedback') or '').strip()
        
        if not memory_id or not feedback:
            return jsonify({
                'code': 0,
                'msg': 'memory_id and feedback are required',
                'data': None
            }), 400
        
        valid_feedback = ['helpful', 'not_helpful', 'accurate', 'inaccurate']
        if feedback not in valid_feedback:
            return jsonify({
                'code': 0,
                'msg': f'feedback must be one of: {valid_feedback}',
                'data': None
            }), 400
        
        memory = get_analysis_memory()
        success = memory.record_feedback(memory_id, feedback)
        
        return jsonify({
            'code': 1 if success else 0,
            'msg': 'success' if success else 'failed',
            'data': None
        })
        
    except Exception as e:
        logger.error(f"Submit feedback failed: {e}")
        return jsonify({
            'code': 0,
            'msg': str(e),
            'data': None
        }), 500


@fast_analysis_bp.route('/performance', methods=['GET'])
@login_required
def get_performance():
    """
    Get AI analysis performance statistics.

    ---
    tags:
      - fast-analysis
    parameters:
      - in: query
        name: market
        type: string
        required: false
        description: Filter by market type
        example: Crypto
      - in: query
        name: symbol
        type: string
        required: false
        description: Filter by symbol
        example: BTC/USDT
      - in: query
        name: days
        type: integer
        required: false
        description: Number of days to analyze
        default: 30
        example: 30
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
                total_analyses:
                  type: integer
                  example: 150
                accuracy_rate:
                  type: number
                  example: 0.75
      401:
        description: Unauthorized
      500:
        description: Server error
    security:
      - Bearer: []
    """
    try:
        market = request.args.get('market', '').strip() or None
        symbol = request.args.get('symbol', '').strip() or None
        days = int(request.args.get('days', 30))
        
        memory = get_analysis_memory()
        stats = memory.get_performance_stats(market, symbol, days)
        
        return jsonify({
            'code': 1,
            'msg': 'success',
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Get performance failed: {e}")
        return jsonify({
            'code': 0,
            'msg': str(e),
            'data': None
        }), 500


@fast_analysis_bp.route('/similar-patterns', methods=['GET'])
@login_required
def get_similar_patterns():
    """
    Get similar historical patterns for current market conditions.

    ---
    tags:
      - fast-analysis
    parameters:
      - in: query
        name: market
        type: string
        required: true
        description: Market type
        example: Crypto
      - in: query
        name: symbol
        type: string
        required: true
        description: Symbol
        example: BTC/USDT
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
                patterns:
                  type: array
                  items:
                    type: object
                current_indicators:
                  type: object
                  properties:
                    rsi:
                      type: number
                      example: 65.5
                    macd_signal:
                      type: string
                      example: bullish
                    trend:
                      type: string
                      example: uptrend
      400:
        description: Missing required query parameters
      401:
        description: Unauthorized
      500:
        description: Server error
    security:
      - Bearer: []
    """
    try:
        market = request.args.get('market', '').strip()
        symbol = request.args.get('symbol', '').strip()
        
        if not market or not symbol:
            return jsonify({
                'code': 0,
                'msg': 'market and symbol are required',
                'data': None
            }), 400
        
        # Get current indicators
        service = get_fast_analysis_service()
        data = service._collect_market_data(market, symbol)
        indicators = data.get('indicators', {})
        
        # Find similar patterns
        memory = get_analysis_memory()
        patterns = memory.get_similar_patterns(market, symbol, indicators)
        
        return jsonify({
            'code': 1,
            'msg': 'success',
            'data': {
                'patterns': patterns,
                'current_indicators': {
                    'rsi': indicators.get('rsi', {}).get('value'),
                    'macd_signal': indicators.get('macd', {}).get('signal'),
                    'trend': indicators.get('moving_averages', {}).get('trend'),
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Get similar patterns failed: {e}")
        return jsonify({
            'code': 0,
            'msg': str(e),
            'data': None
        }), 500
