from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.project import Project

bp = Blueprint('project', __name__, url_prefix='/api/projects')


@bp.route('/', methods=['GET'])
@jwt_required()
def get_projects():
    """获取用户的所有项目"""
    current_user_id = get_jwt_identity()

    projects = Project.query.filter_by(user_id=current_user_id).all()
    return jsonify([project.to_dict() for project in projects])


@bp.route('/', methods=['POST'])
@jwt_required()
def create_project():
    """创建新项目"""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    # 验证必填字段
    required_fields = ['name', 'color']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # 检查项目名称是否重复
    existing_project = Project.query.filter_by(
        user_id=current_user_id,
        name=data['name']
    ).first()

    if existing_project:
        return jsonify({'error': 'Project with this name already exists'}), 400

    # 创建新项目
    project = Project(
        name=data['name'],
        color=data['color'],
        user_id=current_user_id,
        description=data.get('description')
    )

    db.session.add(project)
    db.session.commit()

    return jsonify({
        'message': 'Project created successfully',
        'project': project.to_dict()
    }), 201


@bp.route('/<string:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """获取特定项目"""
    current_user_id = get_jwt_identity()

    project = Project.query.filter_by(
        id=project_id,
        user_id=current_user_id
    ).first()

    if not project:
        return jsonify({'error': 'Project not found'}), 404

    return jsonify(project.to_dict())


@bp.route('/<string:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    """更新项目"""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    project = Project.query.filter_by(
        id=project_id,
        user_id=current_user_id
    ).first()

    if not project:
        return jsonify({'error': 'Project not found'}), 404

    # 检查名称是否重复（排除当前项目）
    if 'name' in data and data['name'] != project.name:
        existing_project = Project.query.filter_by(
            user_id=current_user_id,
            name=data['name']
        ).filter(Project.id != project_id).first()

        if existing_project:
            return jsonify({'error': 'Project with this name already exists'}), 400

    # 更新字段
    if 'name' in data:
        project.name = data['name']
    if 'color' in data:
        project.color = data['color']
    if 'description' in data:
        project.description = data['description']

    db.session.commit()

    return jsonify({
        'message': 'Project updated successfully',
        'project': project.to_dict()
    })


@bp.route('/<string:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """删除项目"""
    current_user_id = get_jwt_identity()

    project = Project.query.filter_by(
        id=project_id,
        user_id=current_user_id
    ).first()

    if not project:
        return jsonify({'error': 'Project not found'}), 404

    # 检查是否有任务使用此项目
    if project.tasks:
        return jsonify({
            'error': 'Cannot delete project with associated tasks. Please reassign or delete the tasks first.'
        }), 400

    db.session.delete(project)
    db.session.commit()

    return jsonify({'message': 'Project deleted successfully'})