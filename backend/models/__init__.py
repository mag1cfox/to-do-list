from app import db
from datetime import datetime
from typing import Optional
import uuid


class BaseModel(db.Model):
    """基础模型类"""
    __abstract__ = True

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# 导入所有模型
from .user import User
from .task import Task
from .task_category import TaskCategory
from .time_block import TimeBlock
from .time_block_template import TimeBlockTemplate
from .pomodoro_session import PomodoroSession
# from .time_log import TimeLog
# from .recommendation import Recommendation
# from .daily_stats import DailyStats
# from .daily_review import DailyReview
# from .review_template import ReviewTemplate
# from .review_section import ReviewSection
from .project import Project
from .tag import Tag