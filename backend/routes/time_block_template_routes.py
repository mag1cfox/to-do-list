from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.time_block_template import TimeBlockTemplate
from datetime import datetime

bp = Blueprint('time_block_template', __name__, url_prefix='/api/time-block-templates')


@bp.route('/', methods=['GET'])
@jwt_required()
def get_time_block_templates():
    """获取用户的所有时间块模板"""
    current_user_id = get_jwt_identity()

    templates = TimeBlockTemplate.query.filter_by(user_id=current_user_id).all()
    return jsonify([template.to_dict() for template in templates])


@bp.route('/', methods=['POST'])
@jwt_required()
def create_time_block_template():
    """创建新时间块模板"""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    # 验证必填字段
    if not data.get('name'):
        return jsonify({'error': 'Missing required field: name'}), 400

    # 检查模板名称是否重复
    existing_template = TimeBlockTemplate.query.filter_by(
        user_id=current_user_id,
        name=data['name']
    ).first()

    if existing_template:
        return jsonify({'error': 'Template with this name already exists'}), 400

    # 如果设置为默认模板，需要取消其他模板的默认状态
    if data.get('is_default'):
        TimeBlockTemplate.query.filter_by(
            user_id=current_user_id,
            is_default=True
        ).update({'is_default': False})

    # 创建新模板
    template = TimeBlockTemplate(
        name=data['name'],
        user_id=current_user_id,
        description=data.get('description'),
        is_default=data.get('is_default', False)
    )

    db.session.add(template)
    db.session.commit()

    return jsonify({
        'message': 'Time block template created successfully',
        'template': template.to_dict()
    }), 201


@bp.route('/<string:template_id>', methods=['GET'])
@jwt_required()
def get_time_block_template(template_id):
    """获取特定时间块模板"""
    current_user_id = get_jwt_identity()

    template = TimeBlockTemplate.query.filter_by(
        id=template_id,
        user_id=current_user_id
    ).first()

    if not template:
        return jsonify({'error': 'Time block template not found'}), 404

    return jsonify(template.to_dict())


@bp.route('/<string:template_id>', methods=['PUT'])
@jwt_required()
def update_time_block_template(template_id):
    """更新时间块模板"""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    template = TimeBlockTemplate.query.filter_by(
        id=template_id,
        user_id=current_user_id
    ).first()

    if not template:
        return jsonify({'error': 'Time block template not found'}), 404

    # 检查名称是否重复（排除当前模板）
    if 'name' in data and data['name'] != template.name:
        existing_template = TimeBlockTemplate.query.filter_by(
            user_id=current_user_id,
            name=data['name']
        ).filter(TimeBlockTemplate.id != template_id).first()

        if existing_template:
            return jsonify({'error': 'Template with this name already exists'}), 400

    # 如果设置为默认模板，需要取消其他模板的默认状态
    if 'is_default' in data and data['is_default']:
        TimeBlockTemplate.query.filter_by(
            user_id=current_user_id,
            is_default=True
        ).filter(TimeBlockTemplate.id != template_id).update({'is_default': False})

    # 更新字段
    if 'name' in data:
        template.name = data['name']
    if 'description' in data:
        template.description = data['description']
    if 'is_default' in data:
        template.is_default = data['is_default']

    db.session.commit()

    return jsonify({
        'message': 'Time block template updated successfully',
        'template': template.to_dict()
    })


@bp.route('/<string:template_id>', methods=['DELETE'])
@jwt_required()
def delete_time_block_template(template_id):
    """删除时间块模板"""
    current_user_id = get_jwt_identity()

    template = TimeBlockTemplate.query.filter_by(
        id=template_id,
        user_id=current_user_id
    ).first()

    if not template:
        return jsonify({'error': 'Time block template not found'}), 404

    # 检查是否是默认模板
    if template.is_default:
        return jsonify({
            'error': 'Cannot delete default template. Please set another template as default first.'
        }), 400

    # 检查是否有时间块使用此模板
    if template.time_blocks:
        return jsonify({
            'error': 'Cannot delete template with associated time blocks. Please delete the time blocks first.'
        }), 400

    db.session.delete(template)
    db.session.commit()

    return jsonify({'message': 'Time block template deleted successfully'})


@bp.route('/<string:template_id>/apply', methods=['POST'])
@jwt_required()
def apply_time_block_template(template_id):
    """将模板应用到指定日期"""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    # 验证必填字段
    if not data.get('date'):
        return jsonify({'error': 'Missing required field: date'}), 400

    template = TimeBlockTemplate.query.filter_by(
        id=template_id,
        user_id=current_user_id
    ).first()

    if not template:
        return jsonify({'error': 'Time block template not found'}), 404

    # 验证日期格式
    try:
        target_date = datetime.fromisoformat(data['date'])
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    # 应用模板生成时间块
    try:
        generated_time_blocks = template.apply_to_date(target_date)

        # 保存生成的时间块到数据库
        for time_block in generated_time_blocks:
            db.session.add(time_block)

        db.session.commit()

        return jsonify({
            'message': 'Template applied successfully',
            'generated_time_blocks': [block.to_dict() for block in generated_time_blocks]
        }), 201

    except Exception as e:
        return jsonify({'error': f'Failed to apply template: {str(e)}'}), 500


@bp.route('/<string:template_id>/clone', methods=['POST'])
@jwt_required()
def clone_time_block_template(template_id):
    """克隆时间块模板"""
    current_user_id = get_jwt_identity()

    template = TimeBlockTemplate.query.filter_by(
        id=template_id,
        user_id=current_user_id
    ).first()

    if not template:
        return jsonify({'error': 'Time block template not found'}), 404

    # 克隆模板
    cloned_template = template.clone()
    db.session.add(cloned_template)
    db.session.commit()

    return jsonify({
        'message': 'Template cloned successfully',
        'template': cloned_template.to_dict()
    }), 201