from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.task_category import TaskCategory

bp = Blueprint('task_category', __name__, url_prefix='/api/task-categories')


@bp.route('/', methods=['GET'])
@jwt_required()
def get_task_categories():
    """获取用户的所有任务类别"""
    current_user_id = get_jwt_identity()

    categories = TaskCategory.query.filter_by(user_id=current_user_id).all()
    return jsonify([category.to_dict() for category in categories])


@bp.route('/', methods=['POST'])
@jwt_required()
def create_task_category():
    """创建新的任务类别"""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    # 验证必填字段
    required_fields = ['name', 'color']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # 检查类别名称是否重复
    existing_category = TaskCategory.query.filter_by(
        user_id=current_user_id,
        name=data['name']
    ).first()

    if existing_category:
        return jsonify({'error': 'Task category with this name already exists'}), 400

    # 创建新类别
    category = TaskCategory(
        name=data['name'],
        color=data['color'],
        user_id=current_user_id,
        icon=data.get('icon'),
        description=data.get('description')
    )

    db.session.add(category)
    db.session.commit()

    return jsonify({
        'message': 'Task category created successfully',
        'category': category.to_dict()
    }), 201


@bp.route('/<string:category_id>', methods=['GET'])
@jwt_required()
def get_task_category(category_id):
    """获取特定任务类别"""
    current_user_id = get_jwt_identity()

    category = TaskCategory.query.filter_by(
        id=category_id,
        user_id=current_user_id
    ).first()

    if not category:
        return jsonify({'error': 'Task category not found'}), 404

    return jsonify(category.to_dict())


@bp.route('/<string:category_id>', methods=['PUT'])
@jwt_required()
def update_task_category(category_id):
    """更新任务类别"""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    category = TaskCategory.query.filter_by(
        id=category_id,
        user_id=current_user_id
    ).first()

    if not category:
        return jsonify({'error': 'Task category not found'}), 404

    # 检查名称是否重复（排除当前类别）
    if 'name' in data and data['name'] != category.name:
        existing_category = TaskCategory.query.filter_by(
            user_id=current_user_id,
            name=data['name']
        ).filter(TaskCategory.id != category_id).first()

        if existing_category:
            return jsonify({'error': 'Task category with this name already exists'}), 400

    # 更新字段
    if 'name' in data:
        category.name = data['name']
    if 'color' in data:
        category.color = data['color']
    if 'icon' in data:
        category.icon = data['icon']
    if 'description' in data:
        category.description = data['description']

    db.session.commit()

    return jsonify({
        'message': 'Task category updated successfully',
        'category': category.to_dict()
    })


@bp.route('/<string:category_id>', methods=['DELETE'])
@jwt_required()
def delete_task_category(category_id):
    """删除任务类别"""
    current_user_id = get_jwt_identity()

    category = TaskCategory.query.filter_by(
        id=category_id,
        user_id=current_user_id
    ).first()

    if not category:
        return jsonify({'error': 'Task category not found'}), 404

    # 检查是否有任务使用此类别
    if category.tasks:
        return jsonify({
            'error': 'Cannot delete category with associated tasks. Please reassign or delete the tasks first.'
        }), 400

    db.session.delete(category)
    db.session.commit()

    return jsonify({'message': 'Task category deleted successfully'})