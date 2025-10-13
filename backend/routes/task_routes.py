from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.task import Task, TaskStatus

bp = Blueprint('tasks', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    """获取用户任务列表"""
    current_user_id = get_jwt_identity()

    # 获取查询参数
    status = request.args.get('status')
    category_id = request.args.get('category_id')

    # 构建查询
    query = Task.query.filter_by(user_id=current_user_id)

    if status:
        query = query.filter_by(status=TaskStatus(status))
    if category_id:
        query = query.filter_by(category_id=category_id)

    tasks = query.all()

    return jsonify({
        'tasks': [task.to_dict() for task in tasks],
        'count': len(tasks),
        'message': 'Tasks retrieved successfully'
    }), 200


@bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    """创建新任务"""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # 检查必填字段
    required_fields = ['title', 'planned_start_time', 'category_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # 创建任务
    task = Task(
        title=data['title'],
        description=data.get('description'),
        user_id=current_user_id,
        planned_start_time=data['planned_start_time'],
        estimated_pomodoros=data.get('estimated_pomodoros', 1),
        task_type=data.get('task_type', 'FLEXIBLE'),
        category_id=data['category_id'],
        priority=data.get('priority', 'MEDIUM'),
        project_id=data.get('project_id')
    )

    db.session.add(task)
    db.session.commit()

    return jsonify({
        'task': task.to_dict(),
        'message': 'Task created successfully'
    }), 201


@bp.route('/<task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """获取单个任务详情"""
    current_user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    return jsonify({
        'task': task.to_dict(),
        'message': 'Task retrieved successfully'
    }), 200


@bp.route('/<task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """更新任务"""
    current_user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # 更新任务字段
    update_fields = ['title', 'description', 'planned_start_time', 'estimated_pomodoros',
                    'task_type', 'category_id', 'priority', 'status', 'project_id']

    for field in update_fields:
        if field in data:
            setattr(task, field, data[field])

    db.session.commit()

    return jsonify({
        'task': task.to_dict(),
        'message': 'Task updated successfully'
    }), 200


@bp.route('/<task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """删除任务"""
    current_user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({
        'message': 'Task deleted successfully'
    }), 200