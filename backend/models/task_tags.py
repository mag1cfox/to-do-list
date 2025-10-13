from app import db
from sqlalchemy import Table, Column, String, ForeignKey

# 任务标签关联表
task_tags = Table(
    'task_tags',
    db.metadata,
    Column('task_id', String(36), ForeignKey('tasks.id'), primary_key=True),
    Column('tag_id', String(36), ForeignKey('tags.id'), primary_key=True)
)