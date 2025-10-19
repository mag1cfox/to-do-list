#!/usr/bin/env python3
"""
初始化示例数据脚本
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models.user import User
from models.task_category import TaskCategory
from models.project import Project

def init_sample_data():
    """初始化示例数据"""
    app = create_app()

    with app.app_context():
        print("正在初始化示例数据...")

        # 查找第一个用户（如果没有用户则创建一个示例用户）
        user = User.query.first()
        if not user:
            user = User(
                username="demo",
                email="demo@example.com"
            )
            user.set_password("demo123")
            db.session.add(user)
            db.session.commit()
            print(f"创建了示例用户: {user.username}")

        # 创建默认任务类别
        default_categories = [
            {"name": "科研", "color": "blue", "description": "学术研究和开发工作"},
            {"name": "成长", "color": "green", "description": "个人学习和技能提升"},
            {"name": "休息", "color": "gray", "description": "休息和放松时间"},
            {"name": "娱乐", "color": "orange", "description": "娱乐和休闲活动"},
            {"name": "复盘", "color": "purple", "description": "工作总结和反思"},
            {"name": "其他", "color": "default", "description": "其他类型任务"}
        ]

        for cat_data in default_categories:
            existing_category = TaskCategory.query.filter_by(
                user_id=user.id,
                name=cat_data["name"]
            ).first()

            if not existing_category:
                category = TaskCategory(
                    user_id=user.id,
                    **cat_data
                )
                db.session.add(category)
                print(f"创建了任务类别: {cat_data['name']}")

        # 创建默认项目
        default_projects = [
            {"name": "时间管理系统", "color": "blue", "description": "个人时间管理系统的开发"},
            {"name": "技能提升", "color": "green", "description": "专业技能学习和提升"},
            {"name": "个人项目", "color": "purple", "description": "个人兴趣项目"}
        ]

        for proj_data in default_projects:
            existing_project = Project.query.filter_by(
                user_id=user.id,
                name=proj_data["name"]
            ).first()

            if not existing_project:
                project = Project(
                    user_id=user.id,
                    **proj_data
                )
                db.session.add(project)
                print(f"创建了项目: {proj_data['name']}")

        db.session.commit()
        print("示例数据初始化完成！")

        # 显示创建的数据
        print("\n=== 创建的数据概览 ===")

        categories = TaskCategory.query.filter_by(user_id=user.id).all()
        print(f"任务类别 ({len(categories)}个):")
        for cat in categories:
            print(f"  - {cat.name} ({cat.color})")

        projects = Project.query.filter_by(user_id=user.id).all()
        print(f"\n项目 ({len(projects)}个):")
        for proj in projects:
            print(f"  - {proj.name} ({proj.color})")

if __name__ == "__main__":
    try:
        init_sample_data()
    except Exception as e:
        print(f"初始化示例数据失败: {e}")
        sys.exit(1)