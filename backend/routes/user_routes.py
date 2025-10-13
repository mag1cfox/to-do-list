from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User

bp = Blueprint('users', __name__)


@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """获取用户个人资料"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'user': user.to_dict(),
        'message': 'User profile retrieved successfully'
    }), 200


@bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_user_preferences():
    """获取用户偏好设置"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'preferences': user.preferences,
        'message': 'User preferences retrieved successfully'
    }), 200