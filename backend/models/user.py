from . import BaseModel, db
from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import relationship
from typing import Dict, Any
import bcrypt
import json


class User(BaseModel):
    """用户模型"""
    __tablename__ = 'users'

    username = db.Column(String(50), unique=True, nullable=False)
    email = db.Column(String(100), unique=True, nullable=False)
    password_hash = db.Column(String(255), nullable=False)

    # 用户偏好设置（JSON格式存储）
    preferences = db.Column(Text, default='{}')

    # 关联关系
    tasks = relationship('Task', back_populates='user', cascade='all, delete-orphan')
    task_categories = relationship('TaskCategory', back_populates='user', cascade='all, delete-orphan')
    projects = relationship('Project', back_populates='user', cascade='all, delete-orphan')
    time_blocks = relationship('TimeBlock', back_populates='user', cascade='all, delete-orphan')
    time_block_templates = relationship('TimeBlockTemplate', back_populates='user', cascade='all, delete-orphan')
    pomodoro_sessions = relationship('PomodoroSession', back_populates='user', cascade='all, delete-orphan')
    time_logs = relationship('TimeLog', back_populates='user', cascade='all, delete-orphan')
    recommendations = relationship('Recommendation', back_populates='user', cascade='all, delete-orphan')
    daily_stats = relationship('DailyStats', back_populates='user', cascade='all, delete-orphan')
    daily_reviews = relationship('DailyReview', back_populates='user', cascade='all, delete-orphan')
    review_templates = relationship('ReviewTemplate', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password: str):
        """设置密码（加密存储）"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def get_preferences(self) -> Dict[str, Any]:
        """获取用户偏好设置"""
        try:
            return json.loads(self.preferences)
        except json.JSONDecodeError:
            return {}

    def set_preferences(self, preferences: Dict[str, Any]):
        """设置用户偏好"""
        self.preferences = json.dumps(preferences)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（不包含敏感信息）"""
        base_dict = super().to_dict()
        base_dict.update({
            'username': self.username,
            'email': self.email,
            'preferences': self.get_preferences()
        })
        return base_dict