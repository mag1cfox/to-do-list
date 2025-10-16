#!/usr/bin/env python3
"""
简化的模型导入文件，用于测试
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from typing import Optional
import uuid

# 创建独立的数据库实例用于测试
test_db = SQLAlchemy()


class BaseModel(test_db.Model):
    """基础模型类"""
    __abstract__ = True

    id = test_db.Column(test_db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = test_db.Column(test_db.DateTime, default=datetime.utcnow)
    updated_at = test_db.Column(test_db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# 只导入测试需要的模型
from models.user import User
from models.task import Task
from models.task_category import TaskCategory