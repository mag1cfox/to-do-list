from . import BaseModel, db
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import relationship
from typing import Dict, Any


class Tag(BaseModel):
    """标签模型"""
    __tablename__ = 'tags'

    name = db.Column(String(50), nullable=False)
    user_id = db.Column(String(36), ForeignKey('users.id'), nullable=False)
    color = db.Column(String(7))  # HEX颜色值

    # 多对多关联
    tasks = relationship('Task', secondary='task_tags', back_populates='tags')

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'user_id': self.user_id,
            'color': self.color
        })
        return base_dict