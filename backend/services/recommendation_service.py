"""
智能推荐引擎服务
根据当前时间和用户任务状态，智能推荐应该执行的任务
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from models.task import Task, TaskStatus, TaskType, PriorityLevel
from models.time_block import TimeBlock


class RecommendationService:
    """智能推荐服务类"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_task_recommendations(self, user_id: str, current_time: datetime = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        获取任务推荐列表

        Args:
            user_id: 用户ID
            current_time: 当前时间，默认为系统时间
            limit: 返回推荐数量限制

        Returns:
            推荐任务列表，按优先级排序
        """
        if current_time is None:
            current_time = datetime.utcnow()

        # 获取用户的所有待处理任务
        pending_tasks = self._get_pending_tasks(user_id)

        if not pending_tasks:
            return []

        # 按推荐优先级对任务进行评分和排序
        scored_tasks = []
        for task in pending_tasks:
            score = self._calculate_task_score(task, current_time)
            scored_tasks.append((task, score))

        # 按分数降序排序
        scored_tasks.sort(key=lambda x: x[1], reverse=True)

        # 返回格式化的推荐列表
        recommendations = []
        for task, score in scored_tasks[:limit]:
            recommendations.append({
                'task': task.to_dict(),
                'score': score,
                'reason': self._generate_recommendation_reason(task, current_time),
                'priority_level': self._get_priority_level(score)
            })

        return recommendations

    def get_current_recommendation(self, user_id: str, current_time: datetime = None) -> Optional[Dict[str, Any]]:
        """
        获取当前最应该执行的任务推荐

        Args:
            user_id: 用户ID
            current_time: 当前时间，默认为系统时间

        Returns:
            当前推荐的任务信息，如果没有则返回None
        """
        recommendations = self.get_task_recommendations(user_id, current_time, limit=1)
        return recommendations[0] if recommendations else None

    def _get_pending_tasks(self, user_id: str) -> List[Task]:
        """获取用户的待处理任务"""
        return self.db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                Task.status == TaskStatus.PENDING
            )
        ).all()

    def _calculate_task_score(self, task: Task, current_time: datetime) -> float:
        """
        计算任务的推荐分数

        分数计算规则：
        - 刚性任务且已过计划时间：100分 + 优先级加成
        - 柔性任务且已过计划时间：80分 + 优先级加成
        - 未过计划时间的刚性任务：60分 + 优先级加成
        - 未过计划时间的柔性任务：40分 + 优先级加成
        - 优先级加成：HIGH=+20, MEDIUM=+10, LOW=+0
        """
        base_score = 0

        # 检查是否已过计划时间
        is_overdue = current_time >= task.planned_start_time

        # 根据任务类型和时间状态计算基础分数
        if task.task_type == TaskType.RIGID:
            if is_overdue:
                base_score = 100  # 刚性任务已过时间，最高优先级
            else:
                base_score = 60   # 刚性任务未过时间
        else:  # FLEXIBLE
            if is_overdue:
                base_score = 80   # 柔性任务已过时间
            else:
                base_score = 40   # 柔性任务未过时间

        # 优先级加成
        priority_bonus = {
            PriorityLevel.HIGH: 20,
            PriorityLevel.MEDIUM: 10,
            PriorityLevel.LOW: 0
        }

        final_score = base_score + priority_bonus.get(task.priority, 0)

        # 时间紧迫性调整（距离计划时间越近，分数越高）
        if not is_overdue:
            time_diff = task.planned_start_time - current_time
            hours_until_due = time_diff.total_seconds() / 3600

            if hours_until_due <= 1:  # 1小时内
                final_score += 15
            elif hours_until_due <= 3:  # 3小时内
                final_score += 10
            elif hours_until_due <= 6:  # 6小时内
                final_score += 5

        return final_score

    def _generate_recommendation_reason(self, task: Task, current_time: datetime) -> str:
        """生成推荐原因"""
        reasons = []

        # 时间相关原因
        if current_time >= task.planned_start_time:
            if task.task_type == TaskType.RIGID:
                reasons.append("刚性任务已到计划时间")
            else:
                reasons.append("任务已到计划时间")
        else:
            time_diff = task.planned_start_time - current_time
            hours_until = time_diff.total_seconds() / 3600

            if hours_until <= 1:
                reasons.append("即将到达计划时间")
            elif task.task_type == TaskType.RIGID:
                reasons.append("刚性任务需要提前准备")

        # 优先级相关原因
        if task.priority == PriorityLevel.HIGH:
            reasons.append("高优先级任务")
        elif task.priority == PriorityLevel.MEDIUM:
            reasons.append("中等优先级任务")

        # 类型相关原因
        if task.task_type == TaskType.RIGID:
            reasons.append("需要准时完成")

        return "、".join(reasons) if reasons else "建议执行此任务"

    def _get_priority_level(self, score: float) -> str:
        """根据分数获取优先级等级"""
        if score >= 90:
            return "紧急"
        elif score >= 70:
            return "高"
        elif score >= 50:
            return "中"
        else:
            return "低"

    def get_time_based_suggestions(self, user_id: str, target_date: datetime = None) -> Dict[str, Any]:
        """
        基于时间的任务安排建议

        Args:
            user_id: 用户ID
            target_date: 目标日期，默认为今天

        Returns:
            时间安排建议
        """
        if target_date is None:
            target_date = datetime.utcnow()

        # 获取当天所有任务
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        day_tasks = self.db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                Task.planned_start_time >= start_of_day,
                Task.planned_start_time < end_of_day,
                Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
            )
        ).all()

        # 按时间分组任务
        time_slots = {}
        for task in day_tasks:
            hour_key = task.planned_start_time.hour
            if hour_key not in time_slots:
                time_slots[hour_key] = []
            time_slots[hour_key].append(task)

        # 生成时间安排建议
        suggestions = {
            'date': target_date.date().isoformat(),
            'total_tasks': len(day_tasks),
            'time_slots': [],
            'recommendations': []
        }

        for hour in sorted(time_slots.keys()):
            hour_tasks = time_slots[hour]
            slot_suggestion = {
                'hour': hour,
                'time_range': f"{hour:02d}:00-{hour+1:02d}:00",
                'tasks': [task.to_dict() for task in hour_tasks],
                'count': len(hour_tasks),
                'recommended_task': None
            }

            # 为这个时间段推荐最合适的任务
            if hour_tasks:
                current_slot_time = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                best_task = max(hour_tasks, key=lambda t: self._calculate_task_score(t, current_slot_time))
                slot_suggestion['recommended_task'] = best_task.to_dict()

            suggestions['time_slots'].append(slot_suggestion)

        # 生成总体建议
        if day_tasks:
            urgent_tasks = [t for t in day_tasks if t.priority == PriorityLevel.HIGH]
            rigid_overdue = [t for t in day_tasks
                           if t.task_type == TaskType.RIGID and target_date >= t.planned_start_time]

            if rigid_overdue:
                suggestions['recommendations'].append("有刚性任务已过期，建议立即处理")
            if urgent_tasks:
                suggestions['recommendations'].append(f"今日有{len(urgent_tasks)}个高优先级任务需要关注")
            if len(day_tasks) > 8:
                suggestions['recommendations'].append("任务较多，建议合理安排时间")
        else:
            suggestions['recommendations'].append("今日暂无计划任务")

        return suggestions