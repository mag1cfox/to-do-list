from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from app import db

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


@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    """更新用户个人资料"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # 更新允许的字段
    if 'email' in data:
        # 检查邮箱是否已被其他用户使用
        existing_user = User.query.filter(
            User.email == data['email'],
            User.id != current_user_id
        ).first()
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 400
        user.email = data['email']

    if 'username' in data:
        # 检查用户名是否已被其他用户使用
        existing_user = User.query.filter(
            User.username == data['username'],
            User.id != current_user_id
        ).first()
        if existing_user:
            return jsonify({'error': 'Username already exists'}), 400
        user.username = data['username']

    db.session.commit()

    return jsonify({
        'user': user.to_dict(),
        'message': 'User profile updated successfully'
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
        'preferences': user.get_preferences(),
        'message': 'User preferences retrieved successfully'
    }), 200


@bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_user_preferences():
    """更新用户偏好设置"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data or 'preferences' not in data:
        return jsonify({'error': 'Preferences data is required'}), 400

    try:
        user.set_preferences(data['preferences'])
        db.session.commit()

        return jsonify({
            'preferences': user.get_preferences(),
            'message': 'User preferences updated successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to update preferences: {str(e)}'}), 400


@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改用户密码"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_password or not new_password:
        return jsonify({'error': 'Current password and new password are required'}), 400

    # 验证当前密码
    if not user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 400

    # 设置新密码
    try:
        user.set_password(new_password)
        db.session.commit()

        return jsonify({
            'message': 'Password changed successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to change password: {str(e)}'}), 400


@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """获取用户统计数据"""
    current_user_id = get_jwt_identity()

    try:
        from models.task import Task, TaskStatus
        from models.project import Project
        from models.time_block import TimeBlock
        from models.pomodoro_session import PomodoroSession

        # 任务统计
        total_tasks = Task.query.filter_by(user_id=current_user_id).count()
        completed_tasks = Task.query.filter_by(
            user_id=current_user_id,
            status=TaskStatus.COMPLETED
        ).count()
        pending_tasks = Task.query.filter_by(
            user_id=current_user_id,
            status=TaskStatus.PENDING
        ).count()

        # 项目统计
        total_projects = Project.query.filter_by(user_id=current_user_id).count()

        # 时间块统计
        total_time_blocks = TimeBlock.query.filter_by(user_id=current_user_id).count()

        # 番茄钟统计
        total_pomodoro_sessions = PomodoroSession.query.filter_by(user_id=current_user_id).count()

        return jsonify({
            'stats': {
                'tasks': {
                    'total': total_tasks,
                    'completed': completed_tasks,
                    'pending': pending_tasks,
                    'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2)
                },
                'projects': {
                    'total': total_projects
                },
                'time_blocks': {
                    'total': total_time_blocks
                },
                'pomodoro_sessions': {
                    'total': total_pomodoro_sessions
                }
            },
            'message': 'User stats retrieved successfully'
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get user stats: {str(e)}'}), 500


@bp.route('/delete-account', methods=['DELETE'])
@jwt_required()
def delete_account():
    """删除用户账户"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data or 'password' not in data:
        return jsonify({'error': 'Password confirmation is required'}), 400

    # 验证密码
    if not user.check_password(data['password']):
        return jsonify({'error': 'Password is incorrect'}), 400

    try:
        # 删除用户（会级联删除所有相关数据）
        db.session.delete(user)
        db.session.commit()

        return jsonify({
            'message': 'Account deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete account: {str(e)}'}), 500