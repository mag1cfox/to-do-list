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
            'description': self.description
        })
        return base_dict