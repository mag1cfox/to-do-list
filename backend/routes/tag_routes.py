from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.tag import Tag

bp = Blueprint('tag', __name__, url_prefix='/api/tags')


@bp.route('/', methods=['GET'])
@jwt_required()
def get_tags():
    """获取用户的所有标签"""
    current_user_id = get_jwt_identity()

    tags = Tag.query.filter_by(user_id=current_user_id).all()
    return jsonify([tag.to_dict() for tag in tags])


@bp.route('/', methods=['POST'])
@jwt_required()
def create_tag():
    """创建新标签"""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    # 验证必填字段
    if not data.get('name'):
        return jsonify({'error': 'Missing required field: name'}), 400

    # 检查标签名称是否重复
    existing_tag = Tag.query.filter_by(
        user_id=current_user_id,
        name=data['name']
    ).first()

    if existing_tag:
        return jsonify({'error': 'Tag with this name already exists'}), 400

    # 创建新标签
    tag = Tag(
        name=data['name'],
        user_id=current_user_id,
        color=data.get('color')
    )

    db.session.add(tag)
    db.session.commit()

    return jsonify({
        'message': 'Tag created successfully',
        'tag': tag.to_dict()
    }), 201


@bp.route('/<string:tag_id>', methods=['GET'])
@jwt_required()
def get_tag(tag_id):
    """获取特定标签"""
    current_user_id = get_jwt_identity()

    tag = Tag.query.filter_by(
        id=tag_id,
        user_id=current_user_id
    ).first()

    if not tag:
        return jsonify({'error': 'Tag not found'}), 404

    return jsonify(tag.to_dict())


@bp.route('/<string:tag_id>', methods=['PUT'])
@jwt_required()
def update_tag(tag_id):
    """更新标签"""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    tag = Tag.query.filter_by(
        id=tag_id,
        user_id=current_user_id
    ).first()

    if not tag:
        return jsonify({'error': 'Tag not found'}), 404

    # 检查名称是否重复（排除当前标签）
    if 'name' in data and data['name'] != tag.name:
        existing_tag = Tag.query.filter_by(
            user_id=current_user_id,
            name=data['name']
        ).filter(Tag.id != tag_id).first()

        if existing_tag:
            return jsonify({'error': 'Tag with this name already exists'}), 400

    # 更新字段
    if 'name' in data:
        tag.name = data['name']
    if 'color' in data:
        tag.color = data['color']

    db.session.commit()

    return jsonify({
        'message': 'Tag updated successfully',
        'tag': tag.to_dict()
    })


@bp.route('/<string:tag_id>', methods=['DELETE'])
@jwt_required()
def delete_tag(tag_id):
    """删除标签"""
    current_user_id = get_jwt_identity()

    tag = Tag.query.filter_by(
        id=tag_id,
        user_id=current_user_id
    ).first()

    if not tag:
        return jsonify({'error': 'Tag not found'}), 404

    # 检查是否有任务使用此标签
    if tag.tasks:
        return jsonify({
            'error': 'Cannot delete tag with associated tasks. Please remove the tag from tasks first.'
        }), 400

    db.session.delete(tag)
    db.session.commit()

    return jsonify({'message': 'Tag deleted successfully'})