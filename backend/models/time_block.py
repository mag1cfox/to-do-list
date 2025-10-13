from . import BaseModel, db
from sqlalchemy import String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from typing import Dict, Any
import enum


class BlockType(enum.Enum):
    """时间块类型枚举"""
    RESEARCH = 'RESEARCH'        # 科研
    GROWTH = 'GROWTH'           # 成长
    REST = 'REST'               # 休息
    ENTERTAINMENT = 'ENTERTAINMENT'  # 娱乐
    REVIEW = 'REVIEW'           # 复盘


class TimeBlock(BaseModel):
    """时间块模型"""
    __tablename__ = 'time_blocks'

    user_id = db.Column(String(36), ForeignKey('users.id'), nullable=False)
    date = db.Column(DateTime, nullable=False)  # 所属日期
    start_time = db.Column(DateTime, nullable=False)
    end_time = db.Column(DateTime, nullable=False)
    block_type = db.Column(Enum(BlockType), nullable=False)
    color = db.Column(String(7), nullable=False)  # HEX颜色值
    is_recurring = db.Column(Boolean, default=False)
    recurrence_pattern = db.Column(String(100))

    # 模板关联
    template_id = db.Column(String(36), ForeignKey('time_block_templates.id'))

    # 关联关系
    user = relationship('User', back_populates='time_blocks')
    template = relationship('TimeBlockTemplate', back_populates='time_blocks')
    scheduled_tasks = relationship('Task', back_populates='scheduled_time_block')

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base_dict = super().to_dict()
        base_dict.update({
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'block_type': self.block_type.value,
            'color': self.color,
            'is_recurring': self.is_recurring,
            'recurrence_pattern': self.recurrence_pattern,
            'template_id': self.template_id
        })
        return base_dict