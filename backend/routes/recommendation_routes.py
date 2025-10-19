"""
推荐引擎API路由
提供智能任务推荐功能
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from services.recommendation_service import RecommendationService

bp = Blueprint('recommendations', __name__, url_prefix='/api/recommendations')


@bp.route('/current', methods=['GET'])
@jwt_required()
def get_current_recommendation():
    """获取当前最应该执行的任务推荐"""
    current_user_id = get_jwt_identity()

    try:
        # 获取查询参数中的时间，如果没有则使用当前时间
        current_time_str = request.args.get('current_time')
        current_time = None

        if current_time_str:
            try:
                current_time = datetime.fromisoformat(current_time_str)
            except ValueError:
                return jsonify({'error': 'Invalid time format'}), 400

        # 创建推荐服务
        recommendation_service = RecommendationService(db.session)

        # 获取当前推荐
        recommendation = recommendation_service.get_current_recommendation(
            current_user_id,
            current_time
        )

        if recommendation:
            return jsonify({
                'recommendation': recommendation,
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                'message': '暂无待处理任务',
                'timestamp': datetime.utcnow().isoformat()
            })

    except Exception as e:
        return jsonify({'error': f'获取推荐失败: {str(e)}'}), 500


@bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_task_recommendations():
    """获取任务推荐列表"""
    current_user_id = get_jwt_identity()

    try:
        # 获取查询参数
        limit = request.args.get('limit', 5, type=int)
        current_time_str = request.args.get('current_time')
        current_time = None

        if current_time_str:
            try:
                current_time = datetime.fromisoformat(current_time_str)
            except ValueError:
                return jsonify({'error': 'Invalid time format'}), 400

        # 验证limit参数
        if limit < 1 or limit > 20:
            return jsonify({'error': 'Limit must be between 1 and 20'}), 400

        # 创建推荐服务
        recommendation_service = RecommendationService(db.session)

        # 获取推荐列表
        recommendations = recommendation_service.get_task_recommendations(
            current_user_id,
            current_time,
            limit
        )

        return jsonify({
            'recommendations': recommendations,
            'count': len(recommendations),
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({'error': f'获取推荐失败: {str(e)}'}), 500


@bp.route('/schedule', methods=['GET'])
@jwt_required()
def get_time_based_suggestions():
    """获取基于时间的任务安排建议"""
    current_user_id = get_jwt_identity()

    try:
        # 获取查询参数
        date_str = request.args.get('date')
        target_date = None

        if date_str:
            try:
                target_date = datetime.fromisoformat(date_str)
            except ValueError:
                return jsonify({'error': 'Invalid date format'}), 400

        # 创建推荐服务
        recommendation_service = RecommendationService(db.session)

        # 获取时间安排建议
        suggestions = recommendation_service.get_time_based_suggestions(
            current_user_id,
            target_date
        )

        return jsonify({
            'schedule_suggestions': suggestions,
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({'error': f'获取时间安排建议失败: {str(e)}'}), 500


@bp.route('/summary', methods=['GET'])
@jwt_required()
def get_recommendation_summary():
    """获取推荐摘要信息"""
    current_user_id = get_jwt_identity()

    try:
        # 创建推荐服务
        recommendation_service = RecommendationService(db.session)

        # 获取当前推荐
        current_recommendation = recommendation_service.get_current_recommendation(current_user_id)

        # 获取前5个推荐
        top_recommendations = recommendation_service.get_task_recommendations(current_user_id, limit=5)

        # 统计不同优先级的任务数量
        priority_stats = {}
        for rec in top_recommendations:
            priority = rec['priority_level']
            priority_stats[priority] = priority_stats.get(priority, 0) + 1

        return jsonify({
            'current_recommendation': current_recommendation,
            'top_recommendations_count': len(top_recommendations),
            'priority_distribution': priority_stats,
            'has_recommendations': current_recommendation is not None,
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({'error': f'获取推荐摘要失败: {str(e)}'}), 500