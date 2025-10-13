from . import BaseModel, db
from sqlalchemy import String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from typing import Dict, Any
import enum
from datetime import datetime


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
            'template_id': self.template_id,
            'duration': self.get_duration(),
            'is_active': self.is_active()
        })
        return base_dict

    def get_duration(self) -> int:
        """获取时间块持续时间（分钟）"""
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds() / 60
            return int(duration)
        return 0

    def is_active(self) -> bool:
        """检查时间块是否处于活跃状态"""
        now = datetime.utcnow()
        return self.start_time <= now <= self.end_time if self.start_time and self.end_time else False

    def overlaps_with(self, other: 'TimeBlock') -> bool:
        """检查与另一个时间块是否重叠"""
        if not self.start_time or not self.end_time or not other.start_time or not other.end_time:
            return False
        return self.start_time < other.end_time and other.start_time < self.end_time

    def can_accommodate_task(self, task_duration: int) -> bool:
        """检查时间块是否能容纳指定时长的任务"""
        block_duration = self.get_duration()
        return block_duration >= task_duration