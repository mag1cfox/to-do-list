from . import BaseModel, db
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import relationship
from typing import Dict, Any


class TaskCategory(BaseModel):
    """任务类别模型"""
    __tablename__ = 'task_categories'

    name = db.Column(String(50), nullable=False)
    user_id = db.Column(String(36), ForeignKey('users.id'), nullable=False)
    color = db.Column(String(7), nullable=False)  # HEX颜色值
    icon = db.Column(String(50))
    description = db.Column(Text)

    # 关联关系
    user = relationship('User', back_populates='task_categories')
    tasks = relationship('Task', back_populates='category', cascade='all, delete-orphan')

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'user_id': self.user_id,
            'color': self.color,
            'icon': self.icon,
            'description': self.description,
            'task_count': self.get_task_count(),
            'total_time_spent': self.get_total_time_spent()
        })
        return base_dict

    def get_task_count(self) -> int:
        """获取任务数量"""
        return len(self.tasks) if self.tasks else 0

    def get_total_time_spent(self) -> int:
        """获取总时间花费（分钟）"""
        if not self.tasks:
            return 0

        total_time = 0
        for task in self.tasks:
            # 这里需要实现获取任务实际时间的方法
            # 暂时返回0，后续可以集成TimeLog数据
            total_time += 0
        return total_time