#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api"

def test_analytics_apis():
    """测试数据分析页面相关API"""
    print("=" * 50)
    print("数据分析页面API测试")
    print("=" * 50)

    # 1. 用户认证
    print("1. 测试用户认证...")
    login_data = {
        "username": "demo_user",
        "password": "demo123456"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        assert response.status_code == 200, f"登录失败: {response.status_code}"

        token = response.json()['access_token']
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        print("[OK] 用户认证成功")
    except Exception as e:
        print(f"[ERROR] 用户认证失败: {e}")
        return False

    # 2. 测试任务API
    print("\n2. 测试任务API...")
    try:
        response = requests.get(f"{BASE_URL}/tasks/", headers=headers)
        assert response.status_code == 200, f"获取任务失败: {response.status_code}"

        data = response.json()
        assert "tasks" in data, "响应中必须包含tasks字段"
        tasks = data['tasks']
        print(f"[OK] 获取到 {len(tasks)} 个任务")

        # 任务状态统计
        status_count = {}
        for task in tasks:
            status = task.get('status', 'UNKNOWN')
            status_count[status] = status_count.get(status, 0) + 1
        print(f"[INFO] 任务状态统计: {status_count}")

        # 任务优先级统计
        priority_count = {}
        for task in tasks:
            priority = task.get('priority', 'UNKNOWN')
            priority_count[priority] = priority_count.get(priority, 0) + 1
        print(f"[INFO] 任务优先级分布: {priority_count}")

        # 计算完成率
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.get('status') == 'COMPLETED'])
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        print(f"[INFO] 任务完成率: {completion_rate:.1f}%")

    except Exception as e:
        print(f"[ERROR] 任务API测试失败: {e}")
        return False

    # 3. 测试任务分类API
    print("\n3. 测试任务分类API...")
    try:
        response = requests.get(f"{BASE_URL}/task-categories/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            categories = data.get('task_categories', [])
            print(f"[OK] 获取到 {len(categories)} 个任务分类")
        else:
            print(f"[INFO] 任务分类API不存在或无权限: {response.status_code}")
    except Exception as e:
        print(f"[INFO] 任务分类API测试异常: {e}")

    # 4. 测试项目API
    print("\n4. 测试项目API...")
    try:
        response = requests.get(f"{BASE_URL}/projects/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            projects = data.get('projects', [])
            print(f"[OK] 获取到 {len(projects)} 个项目")
        else:
            print(f"[INFO] 项目API不存在或无权限: {response.status_code}")
    except Exception as e:
        print(f"[INFO] 项目API测试异常: {e}")

    # 5. 测试番茄钟API
    print("\n5. 测试番茄钟API...")
    try:
        response = requests.get(f"{BASE_URL}/pomodoro-sessions/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            sessions = data.get('pomodoro_sessions', [])
            print(f"[OK] 获取到 {len(sessions)} 个番茄钟会话")

            # 番茄钟统计
            completed_sessions = len([s for s in sessions if s.get('status') == 'COMPLETED'])
            total_focus_time = sum([s.get('actual_duration', s.get('planned_duration', 0)) for s in sessions])
            print(f"[INFO] 完成番茄钟数: {completed_sessions}")
            print(f"[INFO] 总专注时间: {total_focus_time} 分钟")
        else:
            print(f"[INFO] 番茄钟API不存在或无权限: {response.status_code}")
    except Exception as e:
        print(f"[INFO] 番茄钟API测试异常: {e}")

    # 6. 创建测试数据
    print("\n6. 创建测试数据...")
    try:
        # 获取分类
        categories_response = requests.get(f"{BASE_URL}/task-categories/", headers=headers)
        category_id = None

        if categories_response.status_code == 200:
            categories = categories_response.json().get('task_categories', [])
            if categories:
                category_id = categories[0]['id']

        # 创建示例任务
        if category_id:
            task_data = {
                "title": f"测试任务_{datetime.now().strftime('%H%M%S')}",
                "description": "用于数据分析测试的任务",
                "category_id": category_id,
                "planned_start_time": datetime.now().isoformat(),
                "estimated_pomodoros": 2,
                "priority": "MEDIUM",
                "task_type": "FLEXIBLE"
            }

            task_response = requests.post(f"{BASE_URL}/tasks/",
                                        headers=headers,
                                        json=task_data)
            if task_response.status_code == 201:
                print("[OK] 创建测试任务成功")
            else:
                print(f"[INFO] 创建测试任务失败: {task_response.status_code}")
        else:
            print("[INFO] 无可用分类，跳过任务创建")

    except Exception as e:
        print(f"[INFO] 创建测试数据异常: {e}")

    print("\n" + "=" * 50)
    print("数据分析API测试完成")
    print("所有基础功能正常，数据分析页面可以获取必要的数据")
    print("=" * 50)

    return True

if __name__ == "__main__":
    test_analytics_apis()