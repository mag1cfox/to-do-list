#!/usr/bin/env python3
"""
任务类别与时间块类型匹配服务
"""

from typing import Dict, List, Optional, Tuple
from models.task_category import TaskCategory
from models.time_block import TimeBlock, BlockType
from models.task import Task


class CategoryTimeBlockMatcher:
    """任务类别与时间块类型匹配器"""

    # 预定义的匹配规则
    DEFAULT_MATCHING_RULES = {
        # 任务类别 -> [时间块类型, 优先级]
        '科研': [(BlockType.RESEARCH, 1.0), (BlockType.GROWTH, 0.8), (BlockType.REVIEW, 0.6)],
        '学习': [(BlockType.GROWTH, 1.0), (BlockType.RESEARCH, 0.8), (BlockType.REVIEW, 0.6)],
        '工作': [(BlockType.RESEARCH, 1.0), (BlockType.GROWTH, 0.8)],
        '阅读': [(BlockType.GROWTH, 1.0), (BlockType.REST, 0.7)],
        '运动': [(BlockType.REST, 1.0), (BlockType.ENTERTAINMENT, 0.8)],
        '娱乐': [(BlockType.ENTERTAINMENT, 1.0), (BlockType.REST, 0.8)],
        '休息': [(BlockType.REST, 1.0)],
        '总结': [(BlockType.REVIEW, 1.0), (BlockType.GROWTH, 0.8)],
        '规划': [(BlockType.REVIEW, 1.0), (BlockType.RESEARCH, 0.8)],
        '其他': [(BlockType.GROWTH, 0.8), (BlockType.RESEARCH, 0.7), (BlockType.REST, 0.6)]
    }

    def __init__(self):
        self.matching_rules = self.DEFAULT_MATCHING_RULES.copy()
        self.user_custom_rules = {}  # 用户自定义规则 {user_id: {category_name: [(block_type, score), ...]}}

    def set_user_custom_rules(self, user_id: str, rules: Dict[str, List[Tuple[BlockType, float]]]):
        """设置用户自定义匹配规则"""
        self.user_custom_rules[user_id] = rules

    def get_matching_rules(self, user_id: str, category_name: str) -> List[Tuple[BlockType, float]]:
        """获取匹配规则，优先使用用户自定义规则"""
        user_rules = self.user_custom_rules.get(user_id, {})
        if category_name in user_rules:
            return user_rules[category_name]
        return self.matching_rules.get(category_name, self.matching_rules['其他'])

    def calculate_match_score(self, task: Task, time_block: TimeBlock) -> float:
        """计算任务与时间块的匹配分数"""
        if not task.category_id:
            # 没有类别，返回中等匹配分数
            return 0.5

        # 获取任务类别
        category = TaskCategory.query.get(task.category_id)
        if not category:
            return 0.5

        # 获取匹配规则
        matching_rules = self.get_matching_rules(task.user_id, category.name)

        # 查找匹配的时间块类型
        for block_type, score in matching_rules:
            if time_block.block_type == block_type:
                return score

        return 0.0

    def find_best_time_blocks(self, task: Task, available_time_blocks: List[TimeBlock],
                            top_k: int = 5) -> List[Tuple[TimeBlock, float]]:
        """为任务找到最佳时间块"""
        scored_blocks = []

        for time_block in available_time_blocks:
            # 计算基础匹配分数
            match_score = self.calculate_match_score(task, time_block)

            # 检查时间容量
            if not time_block.can_accommodate_task(task.estimated_pomodoros * 25):
                match_score *= 0.1  # 大幅降低分数，但仍保留

            # 考虑时间匹配度（任务计划时间与时间块开始时间的接近程度）
            if task.planned_start_time:
                time_diff = abs((time_block.start_time - task.planned_start_time).total_seconds())
                # 时间差越小，分数越高
                time_score = max(0, 1 - time_diff / (4 * 3600))  # 4小时内为满分
                match_score *= time_score

            # 考虑当前时间块已有任务数量
            existing_tasks = len(time_block.scheduled_tasks or [])
            task_penalty = max(0, 1 - existing_tasks * 0.2)  # 每个已调度任务减少20%分数
            match_score *= task_penalty

            scored_blocks.append((time_block, match_score))

        # 按分数排序并返回前top_k个
        scored_blocks.sort(key=lambda x: x[1], reverse=True)
        return scored_blocks[:top_k]

    def suggest_time_blocks_for_task(self, task: Task, date,
                                   top_k: int = 3) -> List[Dict]:
        """为任务建议时间块"""
        # 获取指定日期的时间块
        from datetime import datetime
        target_date = datetime.combine(date, datetime.min.time())

        time_blocks = TimeBlock.query.filter_by(
            user_id=task.user_id,
            date=target_date
        ).all()

        # 找到最佳匹配
        best_matches = self.find_best_time_blocks(task, time_blocks, top_k)

        suggestions = []
        for time_block, score in best_matches:
            suggestion = {
                'time_block': time_block.to_dict(),
                'match_score': score,
                'match_reason': self._get_match_reason(task, time_block, score),
                'suitability': self._get_suitability_level(score)
            }
            suggestions.append(suggestion)

        return suggestions

    def _get_match_reason(self, task: Task, time_block: TimeBlock, score: float) -> str:
        """获取匹配原因"""
        if score >= 0.9:
            return "完美匹配：任务类别与时间块类型高度契合"
        elif score >= 0.7:
            return "良好匹配：任务适合在此时间块执行"
        elif score >= 0.5:
            return "一般匹配：可以执行，但不是最佳选择"
        elif score >= 0.3:
            return "勉强匹配：时间块可能不够理想"
        else:
            return "不推荐：建议寻找其他时间块"

    def _get_suitability_level(self, score: float) -> str:
        """获取适合度级别"""
        if score >= 0.9:
            return "优秀"
        elif score >= 0.7:
            return "良好"
        elif score >= 0.5:
            return "一般"
        elif score >= 0.3:
            return "较差"
        else:
            return "不推荐"

    def auto_assign_task_to_best_block(self, task: Task) -> Optional[TimeBlock]:
        """自动将任务分配到最佳时间块"""
        if not task.planned_start_time:
            return None

        date = task.planned_start_time.date()
        suggestions = self.suggest_time_blocks_for_task(task, date, 1)

        if suggestions and suggestions[0]['match_score'] >= 0.6:
            return suggestions[0]['time_block']

        return None


# 全局匹配器实例
category_timeblock_matcher = CategoryTimeBlockMatcher()