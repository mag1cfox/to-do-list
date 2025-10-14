#!/usr/bin/env python3
"""
数据库初始化脚本
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

def init_database():
    """初始化数据库表"""
    app = create_app()

    with app.app_context():
        print("正在创建数据库表...")

        # 创建所有表
        db.create_all()

        print("数据库表创建完成！")

        # 检查表是否创建成功
        from models import User, Project, Task, TaskCategory, Tag, TimeBlock, TimeBlockTemplate, PomodoroSession

        tables = [
            'users', 'projects', 'tasks', 'task_categories', 'tags',
            'time_blocks', 'time_block_templates', 'pomodoro_sessions', 'task_tags'
        ]

        print("已创建的表:")
        for table in tables:
            print(f"  - {table}")

if __name__ == "__main__":
    try:
        init_database()
        print("数据库初始化成功！")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        sys.exit(1)