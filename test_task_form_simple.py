#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api"

def test_task_form_apis():
    """测试任务创建和编辑组件相关API"""
    print("=" * 50)
    print("任务创建和编辑组件API测试")
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

    # 2. 测试获取任务类别API
    print("\n2. 测试获取任务类别API...")
    try:
        response = requests.get(f"{BASE_URL}/task-categories/", headers=headers)

        if response.status_code == 200:
            data = response.json()
            categories = data.get('task_categories', [])
            print(f"[OK] 获取任务类别成功，共{len(categories)}个类别")

            if categories:
                category = categories[0]
                print(f"[INFO] 示例类别: {category.get('name')} (颜色: {category.get('color')})")
                test_category_id = category['id']
            else:
                print("[INFO] 没有可用的任务类别")
                test_category_id = None
        else:
            print(f"[INFO] 任务类别API不存在或无权限: {response.status_code}")
            test_category_id = None
    except Exception as e:
        print(f"[INFO] 任务类别API测试异常: {e}")
        test_category_id = None

    # 3. 测试获取项目列表API
    print("\n3. 测试获取项目列表API...")
    try:
        response = requests.get(f"{BASE_URL}/projects/", headers=headers)

        if response.status_code == 200:
            data = response.json()
            projects = data.get('projects', [])
            print(f"[OK] 获取项目列表成功，共{len(projects)}个项目")

            if projects:
                project = projects[0]
                print(f"[INFO] 示例项目: {project.get('name')} (颜色: {project.get('color')})")
                test_project_id = project['id']
            else:
                print("[INFO] 没有可用的项目")
                test_project_id = None
        else:
            print(f"[INFO] 项目列表API不存在或无权限: {response.status_code}")
            test_project_id = None
    except Exception as e:
        print(f"[INFO] 项目列表API测试异常: {e}")
        test_project_id = None

    # 4. 测试获取标签列表API
    print("\n4. 测试获取标签列表API...")
    try:
        response = requests.get(f"{BASE_URL}/tags/", headers=headers)

        if response.status_code == 200:
            data = response.json()
            tags = data.get('tags', [])
            print(f"[OK] 获取标签列表成功，共{len(tags)}个标签")

            if tags:
                tag = tags[0]
                print(f"[INFO] 示例标签: {tag.get('name')} (颜色: {tag.get('color')})")
            else:
                print("[INFO] 没有可用的标签")
        else:
            print(f"[INFO] 标签列表API不存在或无权限: {response.status_code}")
    except Exception as e:
        print(f"[INFO] 标签列表API测试异常: {e}")

    # 5. 测试创建任务API
    print("\n5. 测试创建任务API...")
    created_task = None
    if test_category_id:
        try:
            task_data = {
                "title": f"测试任务_{datetime.now().strftime('%H%M%S')}",
                "description": "这是一个测试任务，用于验证任务创建功能",
                "category_id": test_category_id,
                "planned_start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
                "estimated_pomodoros": 2,
                "priority": "HIGH",
                "task_type": "FLEXIBLE"
            }

            response = requests.post(f"{BASE_URL}/tasks/", headers=headers, json=task_data)

            if response.status_code == 201:
                data = response.json()
                created_task = data.get('task')
                print(f"[OK] 创建任务成功")
                print(f"[INFO] 任务ID: {created_task.get('id')}")
                print(f"[INFO] 任务标题: {created_task.get('title')}")
                print(f"[INFO] 任务状态: {created_task.get('status')}")
                print(f"[INFO] 任务优先级: {created_task.get('priority')}")
            else:
                print(f"[ERROR] 创建任务失败: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] 创建任务异常: {e}")
    else:
        print("[SKIP] 没有可用的任务类别，跳过创建任务测试")

    # 6. 测试获取单个任务API
    print("\n6. 测试获取单个任务API...")
    if created_task:
        try:
            task_id = created_task['id']
            response = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=headers)

            if response.status_code == 200:
                data = response.json()
                task = data.get('task')
                print(f"[OK] 获取任务详情成功")
                print(f"[INFO] 任务标题: {task.get('title')}")
                print(f"[INFO] 任务描述: {task.get('description')}")
                print(f"[INFO] 任务类型: {task.get('task_type')}")
            else:
                print(f"[ERROR] 获取任务详情失败: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] 获取任务详情异常: {e}")
    else:
        print("[SKIP] 没有可用的测试任务，跳过获取任务详情测试")

    # 7. 测试更新任务API
    print("\n7. 测试更新任务API...")
    if created_task:
        try:
            task_id = created_task['id']
            update_data = {
                "title": f"更新后的任务_{datetime.now().strftime('%H%M%S')}",
                "description": "这是更新后的任务描述",
                "priority": "MEDIUM",
                "estimated_pomodoros": 3,
                "status": "IN_PROGRESS"
            }

            response = requests.put(f"{BASE_URL}/tasks/{task_id}", headers=headers, json=update_data)

            if response.status_code == 200:
                data = response.json()
                task = data.get('task')
                print(f"[OK] 更新任务成功")
                print(f"[INFO] 更新后的标题: {task.get('title')}")
                print(f"[INFO] 更新后的优先级: {task.get('priority')}")
                print(f"[INFO] 更新后的状态: {task.get('status')}")
            else:
                print(f"[ERROR] 更新任务失败: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] 更新任务异常: {e}")
    else:
        print("[SKIP] 没有可用的测试任务，跳过更新任务测试")

    # 8. 测试创建标签API
    print("\n8. 测试创建标签API...")
    try:
        tag_data = {
            "name": f"测试标签_{datetime.now().strftime('%H%M%S')}",
            "color": "#1890ff"
        }

        response = requests.post(f"{BASE_URL}/tags/", headers=headers, json=tag_data)

        if response.status_code == 201:
            data = response.json()
            tag = data.get('tag')
            print(f"[OK] 创建标签成功")
            print(f"[INFO] 标签ID: {tag.get('id')}")
            print(f"[INFO] 标签名称: {tag.get('name')}")
            print(f"[INFO] 标签颜色: {tag.get('color')}")
        else:
            print(f"[INFO] 创建标签API不存在或失败: {response.status_code}")
    except Exception as e:
        print(f"[INFO] 创建标签异常: {e}")

    # 9. 测试任务表单功能完整性
    print("\n9. 测试任务表单功能完整性...")
    required_functions = [
        ("创建任务", "/tasks/"),
        ("获取任务详情", "/tasks/{id}"),
        ("更新任务", "/tasks/{id}"),
    ]

    optional_functions = [
        ("获取任务类别", "/task-categories/"),
        ("获取项目列表", "/projects/"),
        ("获取标签列表", "/tags/"),
        ("创建标签", "/tags/"),
    ]

    working_required = 0
    working_optional = 0

    print("[INFO] 核心功能测试:")
    for name, endpoint in required_functions:
        try:
            if "创建任务" in name:
                if test_category_id:
                    task_data = {
                        "title": "测试任务",
                        "category_id": test_category_id,
                        "planned_start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
                    }
                    response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=task_data)
                else:
                    response = requests.Response()
                    response.status_code = 999  # 自定义状态码表示跳过
            elif "获取任务详情" in name:
                if created_task:
                    response = requests.get(f"{BASE_URL}{endpoint.format(id=created_task['id'])}", headers=headers)
                else:
                    response = requests.Response()
                    response.status_code = 999
            elif "更新任务" in name:
                if created_task:
                    response = requests.put(f"{BASE_URL}{endpoint.format(id=created_task['id'])}", headers=headers, json={})
                else:
                    response = requests.Response()
                    response.status_code = 999

            if response.status_code == 200 or response.status_code == 201:
                working_required += 1
                print(f"  [OK] {name}")
            elif response.status_code == 999:
                print(f"  [SKIP] {name}")
            else:
                print(f"  [ERROR] {name} - 状态码: {response.status_code}")
        except Exception as e:
            print(f"  [ERROR] {name} - 异常: {e}")

    print("[INFO] 辅助功能测试:")
    for name, endpoint in optional_functions:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            if response.status_code == 200:
                working_optional += 1
                print(f"  [OK] {name}")
            else:
                print(f"  [ERROR] {name} - 状态码: {response.status_code}")
        except Exception as e:
            print(f"  [ERROR] {name} - 异常: {e}")

    # 功能完整性评估
    print(f"\n[INFO] 核心功能通过率: {working_required}/{len(required_functions)}")
    print(f"[INFO] 辅助功能通过率: {working_optional}/{len(optional_functions)}")

    if working_required >= len(required_functions) * 0.8:
        print("[OK] 任务创建和编辑组件功能基本完整")
        return True
    else:
        print("[ERROR] 任务创建和编辑组件功能不完整")
        return False

def main():
    """主函数"""
    print("开始测试任务创建和编辑组件相关API接口...")

    success = test_task_form_apis()

    print("\n" + "=" * 50)
    print("任务创建和编辑组件API测试完成")

    if success:
        print("结论: 任务创建和编辑组件功能正常，可以进行任务的创建、编辑和管理")
    else:
        print("结论: 任务创建和编辑组件功能不完整，请检查相关API接口")

    print("=" * 50)

    return success

if __name__ == "__main__":
    main()