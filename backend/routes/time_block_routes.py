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


@bp.route('/<string:time_block_id>/schedule-task', methods=['POST'])
@jwt_required()
def schedule_task_to_time_block(time_block_id):
    """将任务调度到时间块"""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    task_id = data.get('task_id')
    if not task_id:
        return jsonify({'error': 'Task ID is required'}), 400

    # 获取时间块
    time_block = TimeBlock.query.filter_by(
        id=time_block_id,
        user_id=current_user_id
    ).first()

    if not time_block:
        return jsonify({'error': 'Time block not found'}), 404

    # 获取任务
    from models.task import Task
    task = Task.query.filter_by(
        id=task_id,
        user_id=current_user_id
    ).first()

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    # 检查任务是否已调度到其他时间块
    if task.scheduled_time_block_id:
        return jsonify({'error': 'Task is already scheduled to another time block'}), 400

    # 检查任务时长是否适合时间块
    task_duration = (task.estimated_pomodoros or 1) * 25  # 25分钟每个番茄钟
    block_duration = time_block.get_duration()

    if task_duration > block_duration:
        return jsonify({
            'error': f'Task duration ({task_duration} minutes) exceeds time block duration ({block_duration} minutes)'
        }), 400

    # 将任务调度到时间块
    task.scheduled_time_block_id = time_block_id
    db.session.commit()

    return jsonify({
        'message': 'Task scheduled successfully',
        'task': task.to_dict(),
        'time_block': time_block.to_dict()
    })


@bp.route('/<string:time_block_id>/unschedule-task', methods=['POST'])
@jwt_required()
def unschedule_task_from_time_block(time_block_id):
    """将任务从时间块中移除"""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    task_id = data.get('task_id')
    if not task_id:
        return jsonify({'error': 'Task ID is required'}), 400

    # 获取时间块
    time_block = TimeBlock.query.filter_by(
        id=time_block_id,
        user_id=current_user_id
    ).first()

    if not time_block:
        return jsonify({'error': 'Time block not found'}), 404

    # 获取任务
    from models.task import Task
    task = Task.query.filter_by(
        id=task_id,
        user_id=current_user_id
    ).first()

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    # 检查任务是否调度到这个时间块
    if task.scheduled_time_block_id != time_block_id:
        return jsonify({'error': 'Task is not scheduled to this time block'}), 400

    # 将任务从时间块中移除
    task.scheduled_time_block_id = None
    db.session.commit()

    return jsonify({
        'message': 'Task unscheduled successfully',
        'task': task.to_dict()
    })


@bp.route('/check-conflicts', methods=['POST'])
@jwt_required()
def check_time_block_conflicts():
    """检查时间块冲突"""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    date_str = data.get('date')
    if not date_str:
        return jsonify({'error': 'Date is required'}), 400

    try:
        target_date = datetime.fromisoformat(date_str)
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    # 获取指定日期的所有时间块
    time_blocks = TimeBlock.query.filter_by(
        user_id=current_user_id,
        date=target_date
    ).all()

    conflicts = []

    # 检查时间块之间的重叠
    for i in range(len(time_blocks)):
        for j in range(i + 1, len(time_blocks)):
            block1 = time_blocks[i]
            block2 = time_blocks[j]

            if block1.overlaps_with(block2):
                conflicts.append({
                    'type': 'time_overlap',
                    'block1': block1.to_dict(),
                    'block2': block2.to_dict(),
                    'message': f"Time block {block1.id} overlaps with time block {block2.id}"
                })

    # 检查任务与时间块的时间匹配
    from models.task import Task
    for block in time_blocks:
        if block.scheduled_tasks:
            for task in block.scheduled_tasks:
                task_duration = (task.estimated_pomodoros or 1) * 25
                block_duration = block.get_duration()

                if task_duration > block_duration:
                    conflicts.append({
                        'type': 'task_duration',
                        'time_block': block.to_dict(),
                        'task': task.to_dict(),
                        'message': f"Task '{task.title}' duration ({task_duration}min) exceeds time block duration ({block_duration}min)"
                    })

    return jsonify({
        'conflicts': conflicts,
        'conflict_count': len(conflicts),
        'date': date_str
    })


@bp.route('/suggest-time-slots', methods=['POST'])
@jwt_required()
def suggest_time_slots():
    """为任务建议合适的时间块"""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    task_id = data.get('task_id')
    date_str = data.get('date')

    if not task_id or not date_str:
        return jsonify({'error': 'Task ID and date are required'}), 400

    try:
        target_date = datetime.fromisoformat(date_str)
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    # 获取任务
    from models.task import Task
    task = Task.query.filter_by(
        id=task_id,
        user_id=current_user_id
    ).first()

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    task_duration = (task.estimated_pomodoros or 1) * 25

    # 获取当天所有时间块
    time_blocks = TimeBlock.query.filter_by(
        user_id=current_user_id,
        date=target_date
    ).all()

    suggestions = []

    for block in time_blocks:
        block_duration = block.get_duration()

        # 检查时间块是否能容纳任务
        if block_duration >= task_duration:
            # 检查任务类别是否匹配时间块类型
            category_match = True
            if task.category_id:
                from models.task_category import TaskCategory
                category = TaskCategory.query.get(task.category_id)
                if category:
                    # 简单的类别匹配逻辑
                    category_match = True  # 可以根据需要扩展

            suggestions.append({
                'time_block': block.to_dict(),
                'suitability_score': min(100, (block_duration - task_duration) / task_duration * 100),
                'category_match': category_match,
                'message': f"Time block {block.start_time.strftime('%H:%m')} - {block.end_time.strftime('%H:%m')} can accommodate the task"
            })

    # 按适合度排序
    suggestions.sort(key=lambda x: x['suitability_score'], reverse=True)

    return jsonify({
        'suggestions': suggestions,
        'task': task.to_dict(),
        'task_duration': task_duration
    })