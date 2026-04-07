"""
Community APIs - 指标社区接口

提供指标市场、购买、评论等功能的 REST API。
"""

from flask import Blueprint, jsonify, request, g

from app.utils.auth import login_required
from app.utils.logger import get_logger
from app.services.community_service import get_community_service

logger = get_logger(__name__)

community_bp = Blueprint("community", __name__)


# ==========================================
# 策略分享 (Strategy Sharing)
# ==========================================

@community_bp.route("/strategies", methods=["GET"])
def get_shared_strategies():
    """
    Get shared strategies list with pagination and filtering.

    ---
    tags:
      - community
    parameters:
      - in: query
        name: sortBy
        type: string
        default: popular
        enum: [popular, recent, most_liked]
        description: Sort order
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: pageSize
        type: integer
        default: 20
    responses:
      200:
        description: List of shared strategies
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
                data:
                  type: object
                  properties:
                    items:
                      type: array
                      items:
                        type: object
                        properties:
                          id:
                            type: integer
                          strategyName:
                            type: string
                          userName:
                            type: string
                          description:
                            type: string
                          views:
                            type: integer
                          likes:
                            type: integer
                          commentCount:
                            type: integer
                          isLiked:
                            type: boolean
                          strategyCode:
                            type: string
    """
    try:
        sort_by = request.args.get('sortBy', 'popular')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 20, type=int)
        
        # Return mock data - frontend handles empty state gracefully
        # Can be implemented later with actual strategy sharing feature
        strategies = []
        
        return jsonify({
            "code": 1,
            "msg": "success",
            "data": {
                "data": {
                    "items": strategies
                }
            }
        })
    
    except Exception as e:
        logger.error(f"Community strategies API failed: {e}", exc_info=True)
        return jsonify({
            "code": 0,
            "msg": str(e),
            "data": None
        }), 500


@community_bp.route("/strategies/<int:strategy_id>", methods=["GET"])
def get_strategy_detail(strategy_id: int):
    """
    Get strategy detail by ID.
    ---
    tags:
      - community
    responses:
      200:
        description: Strategy detail
    """
    try:
        # Return mock empty data
        return jsonify({
            "code": 1,
            "msg": "success",
            "data": None
        })
    except Exception as e:
        logger.error(f"Community strategy detail API failed: {e}", exc_info=True)
        return jsonify({
            "code": 0,
            "msg": str(e),
            "data": None
        }), 500


@community_bp.route("/strategies/<int:strategy_id>/comments", methods=["GET"])
def get_strategy_comments(strategy_id: int):
    """
    Get comments for a strategy.
    ---
    tags:
      - community
    responses:
      200:
        description: List of comments
        schema:
          type: object
          properties:
            code:
              type: integer
            msg:
              type: string
            data:
              type: object
              properties:
                data:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      userName:
                        type: string
                      content:
                        type: string
    """
    try:
        # Return mock empty data
        return jsonify({
            "code": 1,
            "msg": "success",
            "data": {
                "data": []
            }
        })
    except Exception as e:
        logger.error(f"Community strategy comments API failed: {e}", exc_info=True)
        return jsonify({
            "code": 0,
            "msg": str(e),
            "data": None
        }), 500


# ==========================================
# 指标市场
# ==========================================

@community_bp.route("/indicators", methods=["GET"])
@login_required
def get_market_indicators():
    """
    Get market indicators list with pagination and filtering.

    ---
    tags:
      - community
    parameters:
      - in: query
        name: page
        required: false
        type: integer
        description: Page number
        default: 1
        example: 1
      - in: query
        name: page_size
        required: false
        type: integer
        description: Items per page (max 50)
        default: 12
        example: 12
      - in: query
        name: keyword
        required: false
        type: string
        description: Search keyword
        example: MACD
      - in: query
        name: pricing_type
        required: false
        type: string
        description: Filter by pricing type
        enum: [free, paid]
        example: free
      - in: query
        name: sort_by
        required: false
        type: string
        description: Sort order
        enum: [newest, hot, price_asc, price_desc, rating]
        default: newest
        example: newest
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
    security:
      - Bearer: []
    """
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 12))
        keyword = request.args.get('keyword', '').strip()
        pricing_type = request.args.get('pricing_type', '').strip() or None
        sort_by = request.args.get('sort_by', 'newest').strip()
        
        # 限制每页数量
        page_size = min(max(page_size, 1), 50)
        
        service = get_community_service()
        result = service.get_market_indicators(
            page=page,
            page_size=page_size,
            keyword=keyword if keyword else None,
            pricing_type=pricing_type,
            sort_by=sort_by,
            user_id=g.user_id
        )
        
        return jsonify({'code': 1, 'msg': 'success', 'data': result})
        
    except Exception as e:
        logger.error(f"get_market_indicators failed: {e}")
        return jsonify({'code': 0, 'msg': str(e), 'data': None}), 500


@community_bp.route("/indicators/<int:indicator_id>", methods=["GET"])
@login_required
def get_indicator_detail(indicator_id: int):
    """
    Get indicator detail by ID.

    ---
    tags:
      - community
    parameters:
      - in: path
        name: indicator_id
        required: true
        type: integer
        description: Indicator ID
        example: 123
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
      404:
        description: Indicator not found
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 0
            msg:
              type: string
              example: indicator_not_found
    security:
      - Bearer: []
    """
    try:
        service = get_community_service()
        result = service.get_indicator_detail(indicator_id, user_id=g.user_id)
        
        if not result:
            return jsonify({'code': 0, 'msg': 'indicator_not_found', 'data': None}), 404
        
        return jsonify({'code': 1, 'msg': 'success', 'data': result})
        
    except Exception as e:
        logger.error(f"get_indicator_detail failed: {e}")
        return jsonify({'code': 0, 'msg': str(e), 'data': None}), 500


# ==========================================
# 购买功能
# ==========================================

@community_bp.route("/indicators/<int:indicator_id>/purchase", methods=["POST"])
@login_required
def purchase_indicator(indicator_id: int):
    """
    Purchase an indicator (deducts credits, copies to buyer account).

    ---
    tags:
      - community
    parameters:
      - in: path
        name: indicator_id
        required: true
        type: integer
        description: Indicator ID to purchase
        example: 123
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
    security:
      - Bearer: []
    """
    try:
        service = get_community_service()
        success, message, data = service.purchase_indicator(
            buyer_id=g.user_id,
            indicator_id=indicator_id
        )
        
        if success:
            return jsonify({'code': 1, 'msg': message, 'data': data})
        else:
            return jsonify({'code': 0, 'msg': message, 'data': data}), 400
            
    except Exception as e:
        logger.error(f"purchase_indicator failed: {e}")
        return jsonify({'code': 0, 'msg': str(e), 'data': None}), 500


@community_bp.route("/my-purchases", methods=["GET"])
@login_required
def get_my_purchases():
    """
    Get list of indicators purchased by current user.

    ---
    tags:
      - community
    parameters:
      - in: query
        name: page
        required: false
        type: integer
        description: Page number
        default: 1
        example: 1
      - in: query
        name: page_size
        required: false
        type: integer
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
    security:
      - Bearer: []
    """
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        page_size = min(max(page_size, 1), 50)
        
        service = get_community_service()
        result = service.get_my_purchases(
            user_id=g.user_id,
            page=page,
            page_size=page_size
        )
        
        return jsonify({'code': 1, 'msg': 'success', 'data': result})
        
    except Exception as e:
        logger.error(f"get_my_purchases failed: {e}")
        return jsonify({'code': 0, 'msg': str(e), 'data': None}), 500


# ==========================================
# 评论功能
# ==========================================

@community_bp.route("/indicators/<int:indicator_id>/comments", methods=["GET"])
@login_required
def get_comments(indicator_id: int):
    """
    Get comments for an indicator.

    ---
    tags:
      - community
    parameters:
      - in: path
        name: indicator_id
        required: true
        type: integer
        description: Indicator ID
        example: 123
      - in: query
        name: page
        required: false
        type: integer
        description: Page number
        default: 1
        example: 1
      - in: query
        name: page_size
        required: false
        type: integer
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
              type: array
    security:
      - Bearer: []
    """
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        page_size = min(max(page_size, 1), 50)
        
        service = get_community_service()
        result = service.get_comments(
            indicator_id=indicator_id,
            page=page,
            page_size=page_size
        )
        
        return jsonify({'code': 1, 'msg': 'success', 'data': result})
        
    except Exception as e:
        logger.error(f"get_comments failed: {e}")
        return jsonify({'code': 0, 'msg': str(e), 'data': None}), 500


@community_bp.route("/indicators/<int:indicator_id>/comments", methods=["POST"])
@login_required
def add_comment(indicator_id: int):
    """
    Add a comment to an indicator (only purchasers can comment, once per indicator).

    ---
    tags:
      - community
    parameters:
      - in: path
        name: indicator_id
        required: true
        type: integer
        description: Indicator ID
        example: 123
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - rating
          properties:
            rating:
              type: integer
              description: Rating 1-5 stars
              minimum: 1
              maximum: 5
              example: 5
            content:
              type: string
              description: Comment content (max 500 chars)
              example: Great indicator!
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
    security:
      - Bearer: []
    """
    try:
        data = request.get_json() or {}
        rating = int(data.get('rating', 5))
        content = (data.get('content') or '').strip()
        
        service = get_community_service()
        success, message, result = service.add_comment(
            user_id=g.user_id,
            indicator_id=indicator_id,
            rating=rating,
            content=content
        )
        
        if success:
            return jsonify({'code': 1, 'msg': message, 'data': result})
        else:
            return jsonify({'code': 0, 'msg': message, 'data': result}), 400
            
    except Exception as e:
        logger.error(f"add_comment failed: {e}")
        return jsonify({'code': 0, 'msg': str(e), 'data': None}), 500


@community_bp.route("/indicators/<int:indicator_id>/comments/<int:comment_id>", methods=["PUT"])
@login_required
def update_comment(indicator_id: int, comment_id: int):
    """
    Update a comment (only the author can update their own comment).

    ---
    tags:
      - community
    parameters:
      - in: path
        name: indicator_id
        required: true
        type: integer
        description: Indicator ID
        example: 123
      - in: path
        name: comment_id
        required: true
        type: integer
        description: Comment ID
        example: 456
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            rating:
              type: integer
              description: Rating 1-5 stars
              minimum: 1
              maximum: 5
              example: 4
            content:
              type: string
              description: Comment content (max 500 chars)
              example: Updated review
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
    security:
      - Bearer: []
    """
    try:
        data = request.get_json() or {}
        rating = int(data.get('rating', 5))
        content = (data.get('content') or '').strip()
        
        service = get_community_service()
        success, message, result = service.update_comment(
            user_id=g.user_id,
            comment_id=comment_id,
            indicator_id=indicator_id,
            rating=rating,
            content=content
        )
        
        if success:
            return jsonify({'code': 1, 'msg': message, 'data': result})
        else:
            return jsonify({'code': 0, 'msg': message, 'data': result}), 400
            
    except Exception as e:
        logger.error(f"update_comment failed: {e}")
        return jsonify({'code': 0, 'msg': str(e), 'data': None}), 500


@community_bp.route("/indicators/<int:indicator_id>/my-comment", methods=["GET"])
@login_required
def get_my_comment(indicator_id: int):
    """
    Get current user comment for an indicator (for editing).

    ---
    tags:
      - community
    parameters:
      - in: path
        name: indicator_id
        required: true
        type: integer
        description: Indicator ID
        example: 123
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
    security:
      - Bearer: []
    """
    try:
        service = get_community_service()
        result = service.get_user_comment(
            user_id=g.user_id,
            indicator_id=indicator_id
        )
        
        return jsonify({'code': 1, 'msg': 'success', 'data': result})
        
    except Exception as e:
        logger.error(f"get_my_comment failed: {e}")
        return jsonify({'code': 0, 'msg': str(e), 'data': None}), 500


# ==========================================
# 实盘表现
# ==========================================

@community_bp.route("/indicators/<int:indicator_id>/performance", methods=["GET"])
@login_required
def get_indicator_performance(indicator_id: int):
    """
    Get live performance statistics for an indicator.

    ---
    tags:
      - community
    parameters:
      - in: path
        name: indicator_id
        required: true
        type: integer
        description: Indicator ID
        example: 123
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
    security:
      - Bearer: []
    """
    try:
        service = get_community_service()
        result = service.get_indicator_performance(indicator_id)
        
        return jsonify({'code': 1, 'msg': 'success', 'data': result})
        
    except Exception as e:
        logger.error(f"get_indicator_performance failed: {e}")
        return jsonify({'code': 0, 'msg': str(e), 'data': None}), 500


# ==========================================
# 管理员审核功能
# ==========================================

def _is_admin():
    """检查当前用户是否是管理员"""
    role = getattr(g, 'user_role', None)
    return role == 'admin'


@community_bp.route("/admin/pending-indicators", methods=["GET"])
@login_required
def get_pending_indicators():
    """
    Get pending indicators list for review (admin only).

    ---
    tags:
      - community
    parameters:
      - in: query
        name: page
        required: false
        type: integer
        description: Page number
        default: 1
        example: 1
      - in: query
        name: page_size
        required: false
        type: integer
        description: Items per page (max 100)
        default: 20
        example: 20
      - in: query
        name: review_status
        required: false
        type: string
        description: Filter by review status
        enum: [pending, approved, rejected, all]
        default: pending
        example: pending
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
      403:
        description: Admin required
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 0
            msg:
              type: string
              example: admin_required
    security:
      - Bearer: []
    """
    try:
        if not _is_admin():
            return jsonify({'code': 0, 'msg': 'admin_required', 'data': None}), 403
        
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        review_status = request.args.get('review_status', 'pending').strip() or 'pending'
        page_size = min(max(page_size, 1), 100)
        
        service = get_community_service()
        result = service.get_pending_indicators(
            page=page,
            page_size=page_size,
            review_status=review_status
        )
        
        return jsonify({'code': 1, 'msg': 'success', 'data': result})
        
    except Exception as e:
        logger.error(f"get_pending_indicators failed: {e}")
        return jsonify({'code': 0, 'msg': str(e), 'data': None}), 500


@community_bp.route("/admin/review-stats", methods=["GET"])
@login_required
def get_review_stats():
    """
    Get review statistics (admin only).

    ---
    tags:
      - community
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
      403:
        description: Admin required
    security:
      - Bearer: []
    """
    try:
        if not _is_admin():
            return jsonify({'code': 0, 'msg': 'admin_required', 'data': None}), 403
        
        service = get_community_service()
        result = service.get_review_stats()
        
        return jsonify({'code': 1, 'msg': 'success', 'data': result})
        
    except Exception as e:
        logger.error(f"get_review_stats failed: {e}")
        return jsonify({'code': 0, 'msg': str(e), 'data': None}), 500


@community_bp.route("/admin/indicators/<int:indicator_id>/review", methods=["POST"])
@login_required
def review_indicator(indicator_id: int):
    """
    Review/approve or reject an indicator (admin only).

    ---
    tags:
      - community
    parameters:
      - in: path
        name: indicator_id
        required: true
        type: integer
        description: Indicator ID
        example: 123
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - action
          properties:
            action:
              type: string
              description: Review action
              enum: [approve, reject]
              example: approve
            note:
              type: string
              description: Review note
              example: Approved for quality
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
      403:
        description: Admin required
    security:
      - Bearer: []
    """
    try:
        if not _is_admin():
            return jsonify({'code': 0, 'msg': 'admin_required', 'data': None}), 403
        
        data = request.get_json() or {}
        action = data.get('action', '').strip()
        note = data.get('note', '').strip()
        
        if action not in ('approve', 'reject'):
            return jsonify({'code': 0, 'msg': 'invalid_action', 'data': None}), 400
        
        service = get_community_service()
        success, message = service.review_indicator(
            admin_id=g.user_id,
            indicator_id=indicator_id,
            action=action,
            note=note
        )
        
        if success:
            return jsonify({'code': 1, 'msg': message, 'data': None})
        else:
            return jsonify({'code': 0, 'msg': message, 'data': None}), 400
            
    except Exception as e:
        logger.error(f"review_indicator failed: {e}")
        return jsonify({'code': 0, 'msg': str(e), 'data': None}), 500


@community_bp.route("/admin/indicators/<int:indicator_id>/unpublish", methods=["POST"])
@login_required
def unpublish_indicator(indicator_id: int):
    """
    Unpublish/remove an indicator from the market (admin only).

    ---
    tags:
      - community
    parameters:
      - in: path
        name: indicator_id
        required: true
        type: integer
        description: Indicator ID
        example: 123
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            note:
              type: string
              description: Reason for unpublishing
              example: Violates terms
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
      403:
        description: Admin required
    security:
      - Bearer: []
    """
    try:
        if not _is_admin():
            return jsonify({'code': 0, 'msg': 'admin_required', 'data': None}), 403
        
        data = request.get_json() or {}
        note = data.get('note', '').strip()
        
        service = get_community_service()
        success, message = service.unpublish_indicator(
            admin_id=g.user_id,
            indicator_id=indicator_id,
            note=note
        )
        
        if success:
            return jsonify({'code': 1, 'msg': message, 'data': None})
        else:
            return jsonify({'code': 0, 'msg': message, 'data': None}), 400
            
    except Exception as e:
        logger.error(f"unpublish_indicator failed: {e}")
        return jsonify({'code': 0, 'msg': str(e), 'data': None}), 500


@community_bp.route("/admin/indicators/<int:indicator_id>", methods=["DELETE"])
@login_required
def admin_delete_indicator(indicator_id: int):
    """
    Delete an indicator permanently (admin only).

    ---
    tags:
      - community
    parameters:
      - in: path
        name: indicator_id
        required: true
        type: integer
        description: Indicator ID
        example: 123
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
      403:
        description: Admin required
    security:
      - Bearer: []
    """
    try:
        if not _is_admin():
            return jsonify({'code': 0, 'msg': 'admin_required', 'data': None}), 403
        
        service = get_community_service()
        success, message = service.admin_delete_indicator(
            admin_id=g.user_id,
            indicator_id=indicator_id
        )
        
        if success:
            return jsonify({'code': 1, 'msg': message, 'data': None})
        else:
            return jsonify({'code': 0, 'msg': message, 'data': None}), 400
            
    except Exception as e:
        logger.error(f"admin_delete_indicator failed: {e}")
        return jsonify({'code': 0, 'msg': str(e), 'data': None}), 500
