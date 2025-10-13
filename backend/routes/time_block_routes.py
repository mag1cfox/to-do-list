from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.time_block import TimeBlock, BlockType
from datetime import datetime

bp = Blueprint('time_block', __name__, url_prefix='/api/time-blocks')


@bp.route('/', methods=['GET'])
@jwt_required()
def get_time_blocks():
    """获取用户的所有时间块"""
    current_user_id = get_jwt_identity()

    # 支持按日期过滤
    date_str = request.args.get('date')
    if date_str:
        try:
            target_date = datetime.fromisoformat(date_str)
            time_blocks = TimeBlock.query.filter_by(
                user_id=current_user_id,
                date=target_date
            ).all()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
    else:
        time_blocks = TimeBlock.query.filter_by(user_id=current_user_id).all()

    return jsonify([time_block.to_dict() for time_block in time_blocks])


@bp.route('/', methods=['POST'])
@jwt_required()
def create_time_block():
    """创建新时间块"""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    # 验证必填字段
    required_fields = ['date', 'start_time', 'end_time', 'block_type', 'color']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # 验证时间格式和逻辑
    try:
        date = datetime.fromisoformat(data['date'])
        start_time = datetime.fromisoformat(data['start_time'])
        end_time = datetime.fromisoformat(data['end_time'])
    except ValueError:
        return jsonify({'error': 'Invalid date/time format'}), 400

    # 验证开始时间早于结束时间
    if start_time >= end_time:
        return jsonify({'error': 'Start time must be before end time'}), 400

    # 验证时间块类型
    try:
        block_type = BlockType(data['block_type'])
    except ValueError:
        return jsonify({'error': 'Invalid block type'}), 400

    # 检查时间重叠
    overlapping_blocks = TimeBlock.query.filter_by(
        user_id=current_user_id,
        date=date
    ).filter(
        TimeBlock.start_time < end_time,
        TimeBlock.end_time > start_time
    ).all()

    if overlapping_blocks:
        return jsonify({'error': 'Time block overlaps with existing blocks'}), 400

    # 创建新时间块
    time_block = TimeBlock(
        user_id=current_user_id,
        date=date,
        start_time=start_time,
        end_time=end_time,
        block_type=block_type,
        color=data['color'],
        is_recurring=data.get('is_recurring', False),
        recurrence_pattern=data.get('recurrence_pattern'),
        template_id=data.get('template_id')
    )

    db.session.add(time_block)
    db.session.commit()

    return jsonify({
        'message': 'Time block created successfully',
        'time_block': time_block.to_dict()
    }), 201


@bp.route('/<string:time_block_id>', methods=['GET'])
@jwt_required()
def get_time_block(time_block_id):
    """获取特定时间块"""
    current_user_id = get_jwt_identity()

    time_block = TimeBlock.query.filter_by(
        id=time_block_id,
        user_id=current_user_id
    ).first()

    if not time_block:
        return jsonify({'error': 'Time block not found'}), 404

    return jsonify(time_block.to_dict())


@bp.route('/<string:time_block_id>', methods=['PUT'])
@jwt_required()
def update_time_block(time_block_id):
    """更新时间块"""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    time_block = TimeBlock.query.filter_by(
        id=time_block_id,
        user_id=current_user_id
    ).first()

    if not time_block:
        return jsonify({'error': 'Time block not found'}), 404

    # 验证时间格式和逻辑
    if 'start_time' in data or 'end_time' in data:
        try:
            new_start_time = datetime.fromisoformat(data.get('start_time', time_block.start_time.isoformat()))
            new_end_time = datetime.fromisoformat(data.get('end_time', time_block.end_time.isoformat()))
        except ValueError:
            return jsonify({'error': 'Invalid date/time format'}), 400

        # 验证开始时间早于结束时间
        if new_start_time >= new_end_time:
            return jsonify({'error': 'Start time must be before end time'}), 400

        # 检查时间重叠（排除当前时间块）
        overlapping_blocks = TimeBlock.query.filter_by(
            user_id=current_user_id,
            date=data.get('date', time_block.date)
        ).filter(
            TimeBlock.id != time_block_id,
            TimeBlock.start_time < new_end_time,
            TimeBlock.end_time > new_start_time
        ).all()

        if overlapping_blocks:
            return jsonify({'error': 'Time block overlaps with existing blocks'}), 400

    # 更新时间块类型
    if 'block_type' in data:
        try:
            time_block.block_type = BlockType(data['block_type'])
        except ValueError:
            return jsonify({'error': 'Invalid block type'}), 400

    # 更新其他字段
    if 'date' in data:
        time_block.date = datetime.fromisoformat(data['date'])
    if 'start_time' in data:
        time_block.start_time = datetime.fromisoformat(data['start_time'])
    if 'end_time' in data:
        time_block.end_time = datetime.fromisoformat(data['end_time'])
    if 'color' in data:
        time_block.color = data['color']
    if 'is_recurring' in data:
        time_block.is_recurring = data['is_recurring']
    if 'recurrence_pattern' in data:
        time_block.recurrence_pattern = data['recurrence_pattern']
    if 'template_id' in data:
        time_block.template_id = data['template_id']

    db.session.commit()

    return jsonify({
        'message': 'Time block updated successfully',
        'time_block': time_block.to_dict()
    })


@bp.route('/<string:time_block_id>', methods=['DELETE'])
@jwt_required()
def delete_time_block(time_block_id):
    """删除时间块"""
    current_user_id = get_jwt_identity()

    time_block = TimeBlock.query.filter_by(
        id=time_block_id,
        user_id=current_user_id
    ).first()

    if not time_block:
        return jsonify({'error': 'Time block not found'}), 404

    # 检查是否有任务排布到此时间块
    if time_block.scheduled_tasks:
        return jsonify({
            'error': 'Cannot delete time block with scheduled tasks. Please remove tasks first.'
        }), 400

    db.session.delete(time_block)
    db.session.commit()

    return jsonify({'message': 'Time block deleted successfully'})