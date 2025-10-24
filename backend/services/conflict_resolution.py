#!/usr/bin/env python3
"""
时间块冲突检测和解决建议服务
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta, time
from models.time_block import TimeBlock, BlockType
from models.task import Task
from models.task_category import TaskCategory
from services.category_timeblock_matching import category_timeblock_matcher


class ConflictType:
    """冲突类型常量"""
    TIME_OVERLAP = "time_overlap"
    TASK_DURATION = "task_duration"
    TASK_TYPE_MISMATCH = "task_type_mismatch"
    RESOURCE_OVERLOAD = "resource_overload"
    SCHEDULE_VIOLATION = "schedule_violation"


class ConflictSeverity:
    """冲突严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TimeBlockConflict:
    """时间块冲突对象"""
    def __init__(self, conflict_type: str, severity: str, message: str,
                 affected_blocks: List[TimeBlock] = None, affected_tasks: List[Task] = None,
                 suggestions: List[str] = None, auto_fixable: bool = False):
        self.conflict_type = conflict_type
        self.severity = severity
        self.message = message
        self.affected_blocks = affected_blocks or []
        self.affected_tasks = affected_tasks or []
        self.suggestions = suggestions or []
        self.auto_fixable = auto_fixable
        self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'conflict_type': self.conflict_type,
            'severity': self.severity,
            'message': self.message,
            'affected_blocks': [block.to_dict() for block in self.affected_blocks],
            'affected_tasks': [task.to_dict() for task in self.affected_tasks],
            'suggestions': self.suggestions,
            'auto_fixable': self.auto_fixable,
            'created_at': self.created_at.isoformat()
        }


class ConflictResolutionService:
    """冲突检测和解决服务"""

    def __init__(self):
        self.conflict_resolvers = {
            ConflictType.TIME_OVERLAP: self._resolve_time_overlap,
            ConflictType.TASK_DURATION: self._resolve_task_duration,
            ConflictType.TASK_TYPE_MISMATCH: self._resolve_task_type_mismatch,
            ConflictType.RESOURCE_OVERLOAD: self._resolve_resource_overload,
            ConflictType.SCHEDULE_VIOLATION: self._resolve_schedule_violation
        }

    def detect_conflicts(self, user_id: str, date: datetime) -> List[TimeBlockConflict]:
        """检测指定日期的所有冲突"""
        conflicts = []

        # 获取当天所有时间块
        time_blocks = TimeBlock.query.filter_by(
            user_id=user_id,
            date=date
        ).all()

        # 1. 检测时间重叠冲突
        conflicts.extend(self._detect_time_overlaps(time_blocks))

        # 2. 检测任务时长冲突
        conflicts.extend(self._detect_task_duration_conflicts(time_blocks))

        # 3. 检测任务类型不匹配
        conflicts.extend(self._detect_task_type_mismatches(time_blocks))

        # 4. 检测资源过载
        conflicts.extend(self._detect_resource_overloads(time_blocks))

        # 5. 检测日程违规
        conflicts.extend(self._detect_schedule_violations(time_blocks))

        # 按严重程度排序
        conflicts.sort(key=lambda x: self._get_severity_priority(x.severity), reverse=True)

        return conflicts

    def _detect_time_overlaps(self, time_blocks: List[TimeBlock]) -> List[TimeBlockConflict]:
        """检测时间重叠冲突"""
        conflicts = []

        for i in range(len(time_blocks)):
            for j in range(i + 1, len(time_blocks)):
                block1 = time_blocks[i]
                block2 = time_blocks[j]

                if block1.overlaps_with(block2):
                    # 计算重叠时间
                    overlap_start = max(block1.start_time, block2.start_time)
                    overlap_end = min(block1.end_time, block2.end_time)
                    overlap_duration = (overlap_end - overlap_start).total_seconds() / 60

                    severity = self._calculate_overlap_severity(overlap_duration)

                    suggestions = [
                        f"调整 {block1.block_type.value} 时间块到 {block2.start_time.strftime('%H:%m')} 之前",
                        f"调整 {block2.block_type.value} 时间块到 {block1.end_time.strftime('%H:%m')} 之后",
                        f"合并两个时间块为一个更大的时间块",
                        f"删除优先级较低的时间块"
                    ]

                    conflict = TimeBlockConflict(
                        conflict_type=ConflictType.TIME_OVERLAP,
                        severity=severity,
                        message=f"{block1.block_type.value} 时间块与 {block2.block_type.value} 时间块重叠 {int(overlap_duration)} 分钟",
                        affected_blocks=[block1, block2],
                        suggestions=suggestions,
                        auto_fixable=overlap_duration < 30  # 小于30分钟可以自动修复
                    )
                    conflicts.append(conflict)

        return conflicts

    def _detect_task_duration_conflicts(self, time_blocks: List[TimeBlock]) -> List[TimeBlockConflict]:
        """检测任务时长冲突"""
        conflicts = []

        for block in time_blocks:
            if not block.scheduled_tasks:
                continue

            for task in block.scheduled_tasks:
                task_duration = (task.estimated_pomodoros or 1) * 25
                block_duration = block.get_duration()

                if task_duration > block_duration:
                    overflow = task_duration - block_duration
                    severity = ConflictSeverity.HIGH if overflow > 60 else ConflictSeverity.MEDIUM

                    suggestions = [
                        f"将任务 '{task.title}' 拆分为多个时间块",
                        f"延长 {block.block_type.value} 时间块 {int(overflow)} 分钟",
                        f"减少任务 '{task.title}' 的预估番茄钟数",
                        f"将任务移动到更大的时间块"
                    ]

                    conflict = TimeBlockConflict(
                        conflict_type=ConflictType.TASK_DURATION,
                        severity=severity,
                        message=f"任务 '{task.title}' 的预估时间 ({task_duration}分钟) 超过时间块时长 ({block_duration}分钟) {int(overflow)}分钟",
                        affected_blocks=[block],
                        affected_tasks=[task],
                        suggestions=suggestions,
                        auto_fixable=overflow < 45
                    )
                    conflicts.append(conflict)

        return conflicts

    def _detect_task_type_mismatches(self, time_blocks: List[TimeBlock]) -> List[TimeBlockConflict]:
        """检测任务类型不匹配"""
        conflicts = []

        for block in time_blocks:
            if not block.scheduled_tasks:
                continue

            for task in block.scheduled_tasks:
                match_score = category_timeblock_matcher.calculate_match_score(task, block)

                if match_score < 0.5:  # 匹配分数低于0.5认为是严重不匹配
                    severity = ConflictSeverity.MEDIUM if match_score >= 0.3 else ConflictSeverity.HIGH

                    category = TaskCategory.query.get(task.category_id) if task.category_id else None
                    category_name = category.name if category else "未分类"

                    suggestions = [
                        f"将任务 '{task.title}' 移动到更匹配的时间块类型",
                        f"修改时间块 '{block.block_type.value}' 的类型",
                        f"调整任务 '{task.title}' 的类别",
                        f"保持当前安排（任务仍可在此时间块执行）"
                    ]

                    conflict = TimeBlockConflict(
                        conflict_type=ConflictType.TASK_TYPE_MISMATCH,
                        severity=severity,
                        message=f"任务 '{task.title}' ({category_name}) 与时间块 '{block.block_type.value}' 类型不匹配",
                        affected_blocks=[block],
                        affected_tasks=[task],
                        suggestions=suggestions,
                        auto_fixable=False
                    )
                    conflicts.append(conflict)

        return conflicts

    def _detect_resource_overloads(self, time_blocks: List[TimeBlock]) -> List[TimeBlockConflict]:
        """检测资源过载"""
        conflicts = []

        for block in time_blocks:
            if not block.scheduled_tasks:
                continue

            task_count = len(block.scheduled_tasks)
            if task_count > 3:  # 超过3个任务认为是过载
                severity = ConflictSeverity.HIGH if task_count > 5 else ConflictSeverity.MEDIUM

                task_names = [task.title for task in block.scheduled_tasks[:3]]
                if task_count > 3:
                    task_names.append(f"等{task_count}个任务")

                suggestions = [
                    f"将部分任务移动到其他时间块",
                    f"延长 {block.block_type.value} 时间块",
                    f"优先完成最重要的任务",
                    f"考虑删除一些低优先级任务"
                ]

                conflict = TimeBlockConflict(
                    conflict_type=ConflictType.RESOURCE_OVERLOAD,
                    severity=severity,
                    message=f"{block.block_type.value} 时间块包含 {task_count} 个任务，可能过载",
                    affected_blocks=[block],
                    affected_tasks=block.scheduled_tasks,
                    suggestions=suggestions,
                    auto_fixable=task_count <= 4
                )
                conflicts.append(conflict)

        return conflicts

    def _detect_schedule_violations(self, time_blocks: List[TimeBlock]) -> List[TimeBlockConflict]:
        """检测日程违规"""
        conflicts = []

        # 检查是否有连续工作时间过长
        work_blocks = [block for block in time_blocks
                      if block.block_type in [BlockType.RESEARCH, BlockType.GROWTH]]

        if len(work_blocks) >= 3:
            work_blocks.sort(key=lambda x: x.start_time)

            for i in range(len(work_blocks) - 2):
                # 检查连续3个工作时间块
                block1, block2, block3 = work_blocks[i:i+3]

                # 检查是否有足够休息
                if (block2.start_time - block1.end_time).total_seconds() < 15 * 60:  # 少于15分钟休息
                    total_work_time = (block3.end_time - block1.start_time).total_seconds() / 60

                    if total_work_time > 180:  # 超过3小时连续工作
                        suggestions = [
                            f"在 {block1.end_time.strftime('%H:%m')} 后添加休息时间",
                            f"将 {block2.block_type.value} 时间块推迟到 {block1.end_time + timedelta(minutes=15)}",
                            f"拆分长时间工作块，添加休息间隙"
                        ]

                        conflict = TimeBlockConflict(
                            conflict_type=ConflictType.SCHEDULE_VIOLATION,
                            severity=ConflictSeverity.MEDIUM,
                            message=f"连续工作 {int(total_work_time)} 分钟，缺少休息时间",
                            affected_blocks=[block1, block2, block3],
                            suggestions=suggestions,
                            auto_fixable=True
                        )
                        conflicts.append(conflict)

        return conflicts

    def _calculate_overlap_severity(self, overlap_duration: float) -> str:
        """计算重叠严重程度"""
        if overlap_duration >= 60:
            return ConflictSeverity.CRITICAL
        elif overlap_duration >= 30:
            return ConflictSeverity.HIGH
        elif overlap_duration >= 15:
            return ConflictSeverity.MEDIUM
        else:
            return ConflictSeverity.LOW

    def _get_severity_priority(self, severity: str) -> int:
        """获取严重程度优先级"""
        priority_map = {
            ConflictSeverity.CRITICAL: 4,
            ConflictSeverity.HIGH: 3,
            ConflictSeverity.MEDIUM: 2,
            ConflictSeverity.LOW: 1
        }
        return priority_map.get(severity, 0)

    def auto_fix_conflicts(self, conflicts: List[TimeBlockConflict]) -> List[Dict]:
        """自动修复可修复的冲突"""
        fixed_conflicts = []

        for conflict in conflicts:
            if conflict.auto_fixable and conflict.conflict_type in self.conflict_resolvers:
                try:
                    fix_result = self.conflict_resolvers[conflict.conflict_type](conflict)
                    if fix_result.get('success'):
                        fixed_conflicts.append({
                            'conflict': conflict.to_dict(),
                            'fix_result': fix_result,
                            'message': f"自动修复成功: {conflict.message}"
                        })
                except Exception as e:
                    fixed_conflicts.append({
                        'conflict': conflict.to_dict(),
                        'fix_result': {'success': False, 'error': str(e)},
                        'message': f"自动修复失败: {conflict.message}"
                    })

        return fixed_conflicts

    def _resolve_time_overlap(self, conflict: TimeBlockConflict) -> Dict:
        """解决时间重叠冲突"""
        if len(conflict.affected_blocks) != 2:
            return {'success': False, 'error': '需要恰好2个时间块'}

        block1, block2 = conflict.affected_blocks

        # 简单策略：将较晚开始的时间块向后移动
        if block1.start_time < block2.start_time:
            earlier, later = block1, block2
        else:
            earlier, later = block2, block1

        # 移动较晚的时间块
        gap = later.start_time - earlier.end_time
        if gap.total_seconds() < 0:  # 有重叠
            later.start_time = earlier.end_time + timedelta(minutes=5)
            later.end_time = later.start_time + timedelta(minutes=later.get_duration())

            return {
                'success': True,
                'action': '调整时间块时间',
                'details': f"将 {later.block_type.value} 时间块移动到 {later.start_time.strftime('%H:%m')}"
            }

        return {'success': False, 'error': '无重叠或已解决'}

    def _resolve_task_duration(self, conflict: TimeBlockConflict) -> Dict:
        """解决任务时长冲突"""
        # 这里可以实现自动延长时间块或减少任务预估时间的逻辑
        return {'success': False, 'error': '需要手动处理任务时长冲突'}

    def _resolve_task_type_mismatch(self, conflict: TimeBlockConflict) -> Dict:
        """解决任务类型不匹配"""
        # 类型不匹配通常需要用户决定，不建议自动修复
        return {'success': False, 'error': '任务类型不匹配需要用户确认'}

    def _resolve_resource_overload(self, conflict: TimeBlockConflict) -> Dict:
        """解决资源过载"""
        # 可以实现自动移动部分任务到其他时间块
        return {'success': False, 'error': '资源过载需要手动处理'}

    def _resolve_schedule_violation(self, conflict: TimeBlockConflict) -> Dict:
        """解决日程违规"""
        # 可以自动添加休息时间块
        return {'success': False, 'error': '日程违规需要手动处理'}


# 全局冲突解决服务实例
conflict_resolution_service = ConflictResolutionService()