from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.time_block import TimeBlock, BlockType
from datetime import datetime, timedelta
from typing import List, Dict

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

    # 使用增强的冲突检测服务
    from services.conflict_resolution import conflict_resolution_service

    try:
        conflicts = conflict_resolution_service.detect_conflicts(current_user_id, target_date)
        conflict_dicts = [conflict.to_dict() for conflict in conflicts]

        # 尝试自动修复可修复的冲突
        auto_fixes = conflict_resolution_service.auto_fix_conflicts(conflicts)

        return jsonify({
            'conflicts': conflict_dicts,
            'conflict_count': len(conflicts),
            'auto_fixes': auto_fixes,
            'date': date_str,
            'severity_summary': _get_severity_summary(conflicts)
        })

    except Exception as e:
        # 降级到原有逻辑
        return _fallback_conflict_detection(current_user_id, target_date, date_str)


def _get_severity_summary(conflicts: List) -> Dict:
    """获取严重程度统计"""
    summary = {
        'critical': 0,
        'high': 0,
        'medium': 0,
        'low': 0
    }

    for conflict in conflicts:
        severity = conflict.severity
        if severity in summary:
            summary[severity] += 1

    return summary


def _fallback_conflict_detection(user_id: str, target_date: datetime, date_str: str):
    """降级冲突检测逻辑"""
    # 获取指定日期的所有时间块
    time_blocks = TimeBlock.query.filter_by(
        user_id=user_id,
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
                    'message': f"Time block {block1.id} overlaps with time block {block2.id}",
                    'severity': 'medium'
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
                        'message': f"Task '{task.title}' duration ({task_duration}min) exceeds time block duration ({block_duration}min)",
                        'severity': 'high'
                    })

    return jsonify({
        'conflicts': conflicts,
        'conflict_count': len(conflicts),
        'date': date_str,
        'severity_summary': {'medium': len(conflicts)}
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

    try:
        # 使用增强的匹配服务
        from services.category_timeblock_matching import category_timeblock_matcher
        suggestions = category_timeblock_matcher.suggest_time_blocks_for_task(task, target_date.date())

        return jsonify({
            'suggestions': suggestions,
            'task': task.to_dict(),
            'task_duration': (task.estimated_pomodoros or 1) * 25,
            'enhanced_matching': True
        })

    except Exception as e:
        # 降级到原有逻辑
        return _fallback_time_slot_suggestions(task, target_date, current_user_id)


def _fallback_time_slot_suggestions(task, target_date, user_id):
    """降级时间槽建议逻辑"""
    task_duration = (task.estimated_pomodoros or 1) * 25

    # 获取当天所有时间块
    time_blocks = TimeBlock.query.filter_by(
        user_id=user_id,
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
        'task_duration': task_duration,
        'enhanced_matching': False
    })


@bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_time_block_statistics():
    """获取时间块统计数据"""
    current_user_id = get_jwt_identity()

    # 支持按日期范围过滤
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    try:
        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str)
        else:
            # 默认显示最近30天
            start_date = datetime.utcnow() - timedelta(days=30)

        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str)
        else:
            end_date = datetime.utcnow()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    # 获取指定时间范围内的时间块
    time_blocks = TimeBlock.query.filter(
        TimeBlock.user_id == current_user_id,
        TimeBlock.date >= start_date,
        TimeBlock.date <= end_date
    ).all()

    if not time_blocks:
        return jsonify({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': (end_date - start_date).days
            },
            'total_blocks': 0,
            'total_minutes': 0,
            'statistics': {}
        })

    # 基础统计
    total_blocks = len(time_blocks)
    total_minutes = sum(block.get_duration() for block in time_blocks)
    total_hours = total_minutes / 60

    # 按类型统计
    type_stats = {}
    for block_type in BlockType:
        blocks_of_type = [block for block in time_blocks if block.block_type == block_type]
        type_minutes = sum(block.get_duration() for block in blocks_of_type)
        type_stats[block_type.value] = {
            'count': len(blocks_of_type),
            'minutes': type_minutes,
            'hours': round(type_minutes / 60, 2),
            'percentage': round((type_minutes / total_minutes) * 100, 2) if total_minutes > 0 else 0
        }

    # 按日期统计
    daily_stats = {}
    for block in time_blocks:
        date_key = block.date.date().isoformat()
        if date_key not in daily_stats:
            daily_stats[date_key] = {
                'count': 0,
                'minutes': 0,
                'types': {}
            }

        daily_stats[date_key]['count'] += 1
        daily_stats[date_key]['minutes'] += block.get_duration()

        block_type = block.block_type.value
        if block_type not in daily_stats[date_key]['types']:
            daily_stats[date_key]['types'][block_type] = 0
        daily_stats[date_key]['types'][block_type] += block.get_duration()

    # 转换分钟为小时
    for date_data in daily_stats.values():
        date_data['hours'] = round(date_data['minutes'] / 60, 2)

    # 按星期统计
    weekday_stats = {}
    weekday_names = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']

    for block in time_blocks:
        weekday = block.date.weekday()  # 0=Monday, 6=Sunday
        weekday_name = weekday_names[weekday]

        if weekday_name not in weekday_stats:
            weekday_stats[weekday_name] = {
                'count': 0,
                'minutes': 0,
                'hours': 0
            }

        weekday_stats[weekday_name]['count'] += 1
        weekday_stats[weekday_name]['minutes'] += block.get_duration()

    for weekday_data in weekday_stats.values():
        weekday_data['hours'] = round(weekday_data['minutes'] / 60, 2)

    # 按时间段统计（小时）
    hourly_stats = {}
    for i in range(24):
        hourly_stats[f"{i:02d}:00"] = {
            'count': 0,
            'minutes': 0
        }

    for block in time_blocks:
        start_hour = block.start_time.hour
        end_hour = block.end_time.hour

        # 计算每个小时的时间块时长
        current_hour = start_hour
        current_time = block.start_time

        while current_time < block.end_time and current_hour < 24:
            hour_end = current_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            hour_end = min(hour_end, block.end_time)

            hour_minutes = (hour_end - current_time).total_seconds() / 60
            hourly_stats[f"{current_hour:02d}:00"]['count'] += 1
            hourly_stats[f"{current_hour:02d}:00"]['minutes'] += hour_minutes

            current_time = hour_end
            current_hour = current_time.hour

    # 计算平均值
    days_in_period = max(1, (end_date - start_date).days)
    avg_blocks_per_day = round(total_blocks / days_in_period, 2)
    avg_hours_per_day = round(total_hours / days_in_period, 2)

    # 找出最常用的时间块类型
    most_used_type = max(type_stats.items(), key=lambda x: x[1]['count'])[0] if type_stats else None

    # 找出最忙碌的一天
    busiest_day = max(daily_stats.items(), key=lambda x: x[1]['minutes'])[0] if daily_stats else None

    # 找出最常用的时间段
    most_active_hour = max(hourly_stats.items(), key=lambda x: x[1]['minutes'])[0] if hourly_stats else None

    return jsonify({
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'days': days_in_period
        },
        'summary': {
            'total_blocks': total_blocks,
            'total_minutes': total_minutes,
            'total_hours': round(total_hours, 2),
            'avg_blocks_per_day': avg_blocks_per_day,
            'avg_hours_per_day': avg_hours_per_day,
            'most_used_type': most_used_type,
            'busiest_day': busiest_day,
            'most_active_hour': most_active_hour
        },
        'by_type': type_stats,
        'by_date': daily_stats,
        'by_weekday': weekday_stats,
        'by_hour': hourly_stats
    })


@bp.route('/search', methods=['GET'])
@jwt_required()
def search_time_blocks():
    """搜索时间块"""
    current_user_id = get_jwt_identity()

    # 获取搜索参数
    keyword = request.args.get('keyword', '').strip()
    block_type = request.args.get('type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    has_tasks = request.args.get('has_tasks')  # 'true' 或 'false'
    min_duration = request.args.get('min_duration', type=int)
    max_duration = request.args.get('max_duration', type=int)

    # 构建查询
    query = TimeBlock.query.filter_by(user_id=current_user_id)

    # 关键词搜索（搜索描述和关联的任务）
    if keyword:
        # 这里可以扩展搜索逻辑，目前搜索时间块类型
        query = query.filter(
            db.or_(
                TimeBlock.block_type.like(f"%{keyword}%"),
                # 如果有描述字段，也可以搜索描述
            )
        )

    # 按类型过滤
    if block_type:
        try:
            block_type_enum = BlockType(block_type)
            query = query.filter(TimeBlock.block_type == block_type_enum)
        except ValueError:
            return jsonify({'error': 'Invalid block type'}), 400

    # 按日期范围过滤
    if start_date:
        try:
            start_datetime = datetime.fromisoformat(start_date)
            query = query.filter(TimeBlock.date >= start_datetime)
        except ValueError:
            return jsonify({'error': 'Invalid start_date format'}), 400

    if end_date:
        try:
            end_datetime = datetime.fromisoformat(end_date)
            query = query.filter(TimeBlock.date <= end_datetime)
        except ValueError:
            return jsonify({'error': 'Invalid end_date format'}), 400

    # 按是否有任务过滤
    if has_tasks:
        has_tasks_bool = has_tasks.lower() == 'true'
        if has_tasks_bool:
            query = query.filter(TimeBlock.scheduled_tasks.any())
        else:
            query = query.filter(~TimeBlock.scheduled_tasks.any())

    # 按时长过滤
    if min_duration is not None:
        # 这里需要使用计算字段，暂时跳过实现
        pass

    if max_duration is not None:
        # 这里需要使用计算字段，暂时跳过实现
        pass

    # 排序
    sort_by = request.args.get('sort_by', 'date')
    sort_order = request.args.get('sort_order', 'desc')

    if sort_by == 'date':
        if sort_order == 'desc':
            query = query.order_by(TimeBlock.date.desc(), TimeBlock.start_time.desc())
        else:
            query = query.order_by(TimeBlock.date.asc(), TimeBlock.start_time.asc())
    elif sort_by == 'duration':
        # 需要计算时长，这里简化处理
        query = query.order_by(TimeBlock.start_time.desc())

    # 限制结果数量
    limit = request.args.get('limit', type=int)
    if limit:
        query = query.limit(limit)

    time_blocks = query.all()

    # 补充搜索结果信息
    results = []
    for block in time_blocks:
        block_dict = block.to_dict()
        # 添加关联任务信息
        if block.scheduled_tasks:
            block_dict['scheduled_tasks'] = [task.to_dict() for task in block.scheduled_tasks]
        results.append(block_dict)

    return jsonify({
        'results': results,
        'count': len(results),
        'search_params': {
            'keyword': keyword,
            'type': block_type,
            'start_date': start_date,
            'end_date': end_date,
            'has_tasks': has_tasks,
            'min_duration': min_duration,
            'max_duration': max_duration,
            'sort_by': sort_by,
            'sort_order': sort_order,
            'limit': limit
        }
    })


@bp.route('/batch', methods=['POST'])
@jwt_required()
def batch_create_time_blocks():
    """批量创建时间块"""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data.get('time_blocks') or not isinstance(data['time_blocks'], list):
        return jsonify({'error': 'time_blocks array is required'}), 400

    created_blocks = []
    errors = []

    for i, block_data in enumerate(data['time_blocks']):
        try:
            # 验证必填字段
            required_fields = ['date', 'start_time', 'end_time', 'block_type', 'color']
            for field in required_fields:
                if not block_data.get(field):
                    errors.append(f'Time block {i+1}: Missing required field: {field}')
                    continue

            # 验证时间格式和逻辑
            date = datetime.fromisoformat(block_data['date'])
            start_time = datetime.fromisoformat(block_data['start_time'])
            end_time = datetime.fromisoformat(block_data['end_time'])

            if start_time >= end_time:
                errors.append(f'Time block {i+1}: Start time must be before end time')
                continue

            # 验证时间块类型
            block_type = BlockType(block_data['block_type'])

            # 检查时间重叠
            overlapping_blocks = TimeBlock.query.filter_by(
                user_id=current_user_id,
                date=date
            ).filter(
                TimeBlock.start_time < end_time,
                TimeBlock.end_time > start_time
            ).all()

            if overlapping_blocks:
                errors.append(f'Time block {i+1}: Overlaps with existing blocks')
                continue

            # 创建时间块
            time_block = TimeBlock(
                user_id=current_user_id,
                date=date,
                start_time=start_time,
                end_time=end_time,
                block_type=block_type,
                color=block_data['color'],
                is_recurring=block_data.get('is_recurring', False),
                recurrence_pattern=block_data.get('recurrence_pattern'),
                template_id=block_data.get('template_id')
            )

            db.session.add(time_block)
            created_blocks.append(time_block)

        except ValueError as e:
            errors.append(f'Time block {i+1}: Invalid data format - {str(e)}')
        except Exception as e:
            errors.append(f'Time block {i+1}: {str(e)}')

    # 提交所有成功的时间块
    if created_blocks:
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to save time blocks: {str(e)}'}), 500

    return jsonify({
        'message': f'Created {len(created_blocks)} time blocks successfully',
        'created_count': len(created_blocks),
        'error_count': len(errors),
        'created_blocks': [block.to_dict() for block in created_blocks],
        'errors': errors
    }), 201 if created_blocks else 400


@bp.route('/batch', methods=['DELETE'])
@jwt_required()
def batch_delete_time_blocks():
    """批量删除时间块"""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data.get('time_block_ids') or not isinstance(data['time_block_ids'], list):
        return jsonify({'error': 'time_block_ids array is required'}), 400

    deleted_count = 0
    errors = []

    for time_block_id in data['time_block_ids']:
        try:
            time_block = TimeBlock.query.filter_by(
                id=time_block_id,
                user_id=current_user_id
            ).first()

            if not time_block:
                errors.append(f'Time block {time_block_id}: Not found')
                continue

            # 检查是否有任务排布到此时间块
            if time_block.scheduled_tasks:
                errors.append(f'Time block {time_block_id}: Has scheduled tasks')
                continue

            db.session.delete(time_block)
            deleted_count += 1

        except Exception as e:
            errors.append(f'Time block {time_block_id}: {str(e)}')

    # 提交删除
    if deleted_count > 0:
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to delete time blocks: {str(e)}'}), 500

    return jsonify({
        'message': f'Deleted {deleted_count} time blocks successfully',
        'deleted_count': deleted_count,
        'error_count': len(errors),
        'errors': errors
    })