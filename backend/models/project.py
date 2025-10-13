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
            'color': self.color
        })
        return base_dict