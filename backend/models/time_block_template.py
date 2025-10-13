from . import BaseModel, db
from sqlalchemy import String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from typing import Dict, Any


class TimeBlockTemplate(BaseModel):
    """时间块模板模型"""
    __tablename__ = 'time_block_templates'

    name = db.Column(String(100), nullable=False)
    user_id = db.Column(String(36), ForeignKey('users.id'), nullable=False)
    description = db.Column(Text)
    is_default = db.Column(Boolean, default=False)

    # 关联关系
    user = relationship('User', back_populates='time_block_templates')

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'user_id': self.user_id,
            'description': self.description,
            'is_default': self.is_default
        })
        return base_dict