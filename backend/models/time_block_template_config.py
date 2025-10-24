from app import db
from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from typing import Dict, Any
from datetime import datetime, time
import uuid


class TimeBlockTemplateConfig(db.Model):
    """时间块模板配置表"""
    __tablename__ = 'time_block_template_configs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = db.Column(db.String(36), ForeignKey('time_block_templates.id'), nullable=False)

    # 时间块配置
    name = db.Column(String(100), nullable=False)  # 时间块名称
    start_time = db.Column(db.String(5), nullable=False)  # 开始时间 HH:MM
    end_time = db.Column(db.String(5), nullable=False)    # 结束时间 HH:MM
    block_type = db.Column(db.String(20), nullable=False)  # 时间块类型
    color = db.Column(db.String(7), nullable=False)        # 颜色
    order_index = db.Column(db.Integer, default=0)         # 排序索引

    # 扩展配置
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    template = relationship('TimeBlockTemplate', back_populates='configurations')

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'template_id': self.template_id,
            'name': self.name,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'block_type': self.block_type,
            'color': self.color,
            'order_index': self.order_index,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_duration_minutes(self) -> int:
        """获取持续时间（分钟）"""
        try:
            start = datetime.strptime(self.start_time, '%H:%M')
            end = datetime.strptime(self.end_time, '%H:%M')
            duration = (end - start).total_seconds() / 60
            return int(duration)
        except (ValueError, TypeError):
            return 0

    def get_start_time_object(self) -> time:
        """获取开始时间对象"""
        try:
            return datetime.strptime(self.start_time, '%H:%M').time()
        except (ValueError, TypeError):
            return time(9, 0)  # 默认9:00

    def get_end_time_object(self) -> time:
        """获取结束时间对象"""
        try:
            return datetime.strptime(self.end_time, '%H:%M').time()
        except (ValueError, TypeError):
            return time(17, 0)  # 默认17:00