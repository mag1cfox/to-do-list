from . import BaseModel, db
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import relationship
from typing import Dict, Any


class Project(BaseModel):
    """项目模型"""
    __tablename__ = 'projects'

    name = db.Column(String(100), nullable=False)
    description = db.Column(Text)
    user_id = db.Column(String(36), ForeignKey('users.id'), nullable=False)
    color = db.Column(String(7), nullable=False)  # 项目颜色标识

    # 关联关系
    user = relationship('User', back_populates='projects')
    tasks = relationship('Task', back_populates='project', cascade='all, delete-orphan')

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'color': self.color,
            'task_count': self.get_task_count(),
            'total_estimated_time': self.get_total_estimated_time(),
            'total_actual_time': self.get_total_actual_time(),
            'completion_progress': self.get_completion_progress()
        })
        return base_dict

    def get_task_count(self) -> int:
        """获取项目中的任务数量"""
        return len(self.tasks) if self.tasks else 0

    def get_total_estimated_time(self) -> int:
        """获取项目总预估时间（分钟）"""
        if not self.tasks:
            return 0

        total_time = 0
        for task in self.tasks:
            # 假设每个番茄钟25分钟
            total_time += task.estimated_pomodoros * 25 if task.estimated_pomodoros else 0
        return total_time

    def get_total_actual_time(self) -> int:
        """获取项目总实际花费时间（分钟）"""
        if not self.tasks:
            return 0

        total_time = 0
        for task in self.tasks:
            # 这里需要实现获取任务实际时间的方法
            # 暂时返回0，后续可以集成TimeLog数据
            total_time += 0
        return total_time

    def get_completion_progress(self) -> float:
        """获取项目完成进度（0-1）"""
        if not self.tasks:
            return 0.0

        completed_tasks = [task for task in self.tasks if task.status == 'COMPLETED']
        return len(completed_tasks) / len(self.tasks)