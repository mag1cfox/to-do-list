from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.pomodoro_session import PomodoroSession, SessionStatus, SessionType
from models.task import Task
from datetime import datetime

pomodoro_session_bp = Blueprint('pomodoro_sessions', __name__)

@pomodoro_session_bp.route('/', methods=['GET'])
@jwt_required()
def get_pomodoro_sessions():
    """获取用户的番茄钟会话列表"""
    user_id = get_jwt_identity()

    # 查询参数
    task_id = request.args.get('task_id')
    status = request.args.get('status')
    session_type = request.args.get('session_type')
    date = request.args.get('date')

    query = PomodoroSession.query.filter_by(user_id=user_id)

    if task_id:
        query = query.filter_by(task_id=task_id)

    if status:
        try:
            status_enum = SessionStatus(status)
            query = query.filter_by(status=status_enum)
        except ValueError:
            return jsonify({'error': '无效的状态值'}), 400

    if session_type:
        try:
            type_enum = SessionType(session_type)
            query = query.filter_by(session_type=type_enum)
        except ValueError:
            return jsonify({'error': '无效的会话类型'}), 400

    if date:
        try:
            target_date = datetime.fromisoformat(date).date()
            query = query.filter(db.func.date(PomodoroSession.created_at) == target_date)
        except ValueError:
            return jsonify({'error': '无效的日期格式'}), 400

    # 按创建时间倒序排列
    pomodoro_sessions = query.order_by(PomodoroSession.created_at.desc()).all()

    return jsonify({
        'pomodoro_sessions': [session.to_dict() for session in pomodoro_sessions]
    })

@pomodoro_session_bp.route('/', methods=['POST'])
@jwt_required()
def create_pomodoro_session():
    """创建新的番茄钟会话"""
    user_id = get_jwt_identity()
    data = request.get_json()

    # 验证必需字段
    if not data or 'task_id' not in data:
        return jsonify({'error': '必须提供task_id'}), 400

    task_id = data['task_id']

    # 验证任务存在且属于当前用户
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({'error': '任务不存在或无权限访问'}), 404

    # 检查是否有活跃的会话
    active_session = PomodoroSession.query.filter_by(
        user_id=user_id,
        status=SessionStatus.IN_PROGRESS
    ).first()

    if active_session:
        return jsonify({
            'error': '已有活跃的番茄钟会话',
            'active_session_id': active_session.id
        }), 400

    # 创建新的番茄钟会话
    planned_duration = data.get('planned_duration', 25)
    session_type = data.get('session_type', 'FOCUS')

    try:
        session_type_enum = SessionType(session_type)
    except ValueError:
        return jsonify({'error': '无效的会话类型'}), 400

    pomodoro_session = PomodoroSession(
        task_id=task_id,
        user_id=user_id,
        planned_duration=planned_duration,
        session_type=session_type_enum
    )

    db.session.add(pomodoro_session)
    db.session.commit()

    return jsonify({
        'message': '番茄钟会话创建成功',
        'pomodoro_session': pomodoro_session.to_dict()
    }), 201

@pomodoro_session_bp.route('/<int:session_id>/start', methods=['POST'])
@jwt_required()
def start_pomodoro_session(session_id):
    """开始番茄钟会话"""
    user_id = get_jwt_identity()

    pomodoro_session = PomodoroSession.query.filter_by(
        id=session_id,
        user_id=user_id
    ).first()

    if not pomodoro_session:
        return jsonify({'error': '番茄钟会话不存在或无权限访问'}), 404

    try:
        pomodoro_session.start()
        db.session.commit()

        return jsonify({
            'message': '番茄钟会话已开始',
            'pomodoro_session': pomodoro_session.to_dict()
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@pomodoro_session_bp.route('/<int:session_id>/complete', methods=['POST'])
@jwt_required()
def complete_pomodoro_session(session_id):
    """完成番茄钟会话"""
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    pomodoro_session = PomodoroSession.query.filter_by(
        id=session_id,
        user_id=user_id
    ).first()

    if not pomodoro_session:
        return jsonify({'error': '番茄钟会话不存在或无权限访问'}), 404

    try:
        summary = data.get('completion_summary')
        pomodoro_session.complete(summary)
        db.session.commit()

        return jsonify({
            'message': '番茄钟会话已完成',
            'pomodoro_session': pomodoro_session.to_dict()
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@pomodoro_session_bp.route('/<int:session_id>/interrupt', methods=['POST'])
@jwt_required()
def interrupt_pomodoro_session(session_id):
    """中断番茄钟会话"""
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    pomodoro_session = PomodoroSession.query.filter_by(
        id=session_id,
        user_id=user_id
    ).first()

    if not pomodoro_session:
        return jsonify({'error': '番茄钟会话不存在或无权限访问'}), 404

    try:
        reason = data.get('interruption_reason')
        pomodoro_session.interrupt(reason)
        db.session.commit()

        return jsonify({
            'message': '番茄钟会话已中断',
            'pomodoro_session': pomodoro_session.to_dict()
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@pomodoro_session_bp.route('/active', methods=['GET'])
@jwt_required()
def get_active_pomodoro_session():
    """获取当前活跃的番茄钟会话"""
    user_id = get_jwt_identity()

    active_session = PomodoroSession.query.filter_by(
        user_id=user_id,
        status=SessionStatus.IN_PROGRESS
    ).first()

    if active_session:
        return jsonify({
            'active_session': active_session.to_dict()
        })
    else:
        return jsonify({'message': '没有活跃的番茄钟会话'})

@pomodoro_session_bp.route('/<int:session_id>', methods=['GET'])
@jwt_required()
def get_pomodoro_session(session_id):
    """获取特定的番茄钟会话"""
    user_id = get_jwt_identity()

    pomodoro_session = PomodoroSession.query.filter_by(
        id=session_id,
        user_id=user_id
    ).first()

    if not pomodoro_session:
        return jsonify({'error': '番茄钟会话不存在或无权限访问'}), 404

    return jsonify({
        'pomodoro_session': pomodoro_session.to_dict()
    })

@pomodoro_session_bp.route('/<int:session_id>', methods=['DELETE'])
@jwt_required()
def delete_pomodoro_session(session_id):
    """删除番茄钟会话"""
    user_id = get_jwt_identity()

    pomodoro_session = PomodoroSession.query.filter_by(
        id=session_id,
        user_id=user_id
    ).first()

    if not pomodoro_session:
        return jsonify({'error': '番茄钟会话不存在或无权限访问'}), 404

    # 不能删除活跃的会话
    if pomodoro_session.status == SessionStatus.IN_PROGRESS:
        return jsonify({'error': '不能删除活跃的番茄钟会话'}), 400

    db.session.delete(pomodoro_session)
    db.session.commit()

    return jsonify({'message': '番茄钟会话已删除'})