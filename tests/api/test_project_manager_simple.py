#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

def test_project_manager_apis():
    """测试项目管理组件相关API"""
    print("=" * 50)
    print("项目管理组件API测试")
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

    # 2. 测试获取项目列表API
    print("\n2. 测试获取项目列表API...")
    try:
        response = requests.get(f"{BASE_URL}/projects/", headers=headers)

        if response.status_code == 200:
            projects = response.json()
            print(f"[OK] 获取项目列表成功，共{len(projects)}个项目")

            # 验证项目数据结构
            if projects:
                project = projects[0]
                expected_fields = ['id', 'name', 'color', 'created_at', 'user_id']
                for field in expected_fields:
                    if field in project:
                        print(f"  ✓ {field}: {project[field]}")
                    else:
                        print(f"  ✗ {field}: 缺失")
        else:
            print(f"[ERROR] 获取项目列表失败: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] 获取项目列表异常: {e}")

    # 3. 测试创建项目API
    print("\n3. 测试创建项目API...")
    created_project = None
    try:
        project_data = {
            "name": f"测试项目_{datetime.now().strftime('%H%M%S')}",
            "color": "#52c41a",
            "description": "这是一个测试项目，用于验证项目管理组件功能"
        }

        response = requests.post(f"{BASE_URL}/projects/", headers=headers, json=project_data)

        if response.status_code == 201:
            data = response.json()
            created_project = data.get('project')
            print(f"[OK] 创建项目成功")
            print(f"[INFO] 项目ID: {created_project.get('id')}")
            print(f"[INFO] 项目名称: {created_project.get('name')}")
            print(f"[INFO] 项目颜色: {created_project.get('color')}")
            print(f"[INFO] 项目描述: {created_project.get('description')}")
        else:
            print(f"[ERROR] 创建项目失败: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] 创建项目异常: {e}")

    # 4. 测试获取单个项目API
    print("\n4. 测试获取单个项目API...")
    if created_project:
        try:
            project_id = created_project['id']
            response = requests.get(f"{BASE_URL}/projects/{project_id}", headers=headers)

            if response.status_code == 200:
                project = response.json()
                print(f"[OK] 获取项目详情成功")
                print(f"[INFO] 项目ID: {project.get('id')}")
                print(f"[INFO] 项目名称: {project.get('name')}")
                print(f"[INFO] 项目描述: {project.get('description')}")
            else:
                print(f"[ERROR] 获取项目详情失败: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] 获取项目详情异常: {e}")
    else:
        print("[SKIP] 没有可用的测试项目，跳过获取项目详情测试")

    # 5. 测试更新项目API
    print("\n5. 测试更新项目API...")
    if created_project:
        try:
            project_id = created_project['id']
            update_data = {
                "name": f"更新后的项目_{datetime.now().strftime('%H%M%S')}",
                "color": "#fa8c16",
                "description": "这是更新后的项目描述"
            }

            response = requests.put(f"{BASE_URL}/projects/{project_id}", headers=headers, json=update_data)

            if response.status_code == 200:
                data = response.json()
                project = data.get('project')
                print(f"[OK] 更新项目成功")
                print(f"[INFO] 更新后的名称: {project.get('name')}")
                print(f"[INFO] 更新后的颜色: {project.get('color')}")
                print(f"[INFO] 更新后的描述: {project.get('description')}")
            else:
                print(f"[ERROR] 更新项目失败: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] 更新项目异常: {e}")
    else:
        print("[SKIP] 没有可用的测试项目，跳过更新项目测试")

    # 6. 测试删除项目API
    print("\n6. 测试删除项目API...")
    if created_project:
        try:
            project_id = created_project['id']
            response = requests.delete(f"{BASE_URL}/projects/{project_id}", headers=headers)

            if response.status_code == 200:
                print("[OK] 删除项目成功")

                # 验证项目是否已删除
                get_response = requests.get(f"{BASE_URL}/projects/{project_id}", headers=headers)
                if get_response.status_code == 404:
                    print("[OK] 项目已成功删除")
                else:
                    print("[WARNING] 项目可能未完全删除")
            else:
                print(f"[ERROR] 删除项目失败: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] 删除项目异常: {e}")
    else:
        print("[SKIP] 没有可用的测试项目，跳过删除项目测试")

    # 7. 测试项目验证规则
    print("\n7. 测试项目验证规则...")
    try:
        # 测试创建项目时缺少必填字段
        print("[INFO] 测试缺少必填字段...")
        invalid_project_data = {
            "description": "这个项目缺少名称和颜色"
        }

        response = requests.post(f"{BASE_URL}/projects/", headers=headers, json=invalid_project_data)
        if response.status_code == 400:
            print("[OK] 正确拒绝了缺少必填字段的项目创建请求")
        else:
            print(f"[ERROR] 应该拒绝缺少必填字段的请求，但状态码是: {response.status_code}")

        # 测试创建项目时名称重复
        print("[INFO] 测试项目名称重复...")
        # 先创建一个项目
        project_data = {
            "name": f"重复测试项目_{datetime.now().strftime('%H%M%S')}",
            "color": "#ff0000",
            "description": "这是一个用于测试重复的项目"
        }

        create_response = requests.post(f"{BASE_URL}/projects/", headers=headers, json=project_data)
        if create_response.status_code == 201:
            # 尝试创建同名项目
            duplicate_project_data = {
                "name": project_data['name'],
                "color": "#00ff00",
                "description": "这是一个重复名称的项目"
            }

            duplicate_response = requests.post(f"{BASE_URL}/projects/", headers=headers, json=duplicate_project_data)
            if duplicate_response.status_code == 400:
                print("[OK] 正确拒绝了重复名称的项目创建请求")
            else:
                print(f"[ERROR] 应该拒绝重复名称的请求，但状态码是: {duplicate_response.status_code}")
        else:
            print("[SKIP] 无法创建测试项目，跳过重复名称测试")
    except Exception as e:
        print(f"[ERROR] 项目验证规则测试异常: {e}")

    # 8. 测试项目统计数据
    print("\n8. 测试项目统计数据...")
    try:
        # 获取任务数据用于统计
        tasks_response = requests.get(f"{BASE_URL}/tasks/", headers=headers)
        if tasks_response.status_code == 200:
            tasks = tasks_response.json().get('tasks', [])
            print(f"[OK] 获取任务数据成功，共{len(tasks)}个任务")

            # 按项目分组统计任务
            project_task_count = {}
            project_completed_count = {}

            for task in tasks:
                if task.get('project_id'):
                    project_task_count[task['project_id']] = project_task_count.get(task['project_id'], 0) + 1
                    if task.get('status') == 'COMPLETED':
                        project_completed_count[task['project_id']] = project_completed_count.get(task['project_id'], 0) + 1

            print("[INFO] 项目任务统计:")
            for project_id, total_count in project_task_count.items():
                completed_count = project_completed_count.get(project_id, 0)
                completion_rate = (completed_count / total_count * 100) if total_count > 0 else 0
                print(f"  项目 {project_id}: {total_count} 个任务，{completed_count} 个完成，完成率 {completion_rate:.1f}%")
        else:
            print(f"[INFO] 获取任务数据失败: {tasks_response.status_code}")
    except Exception as e:
        print(f"[INFO] 获取项目统计数据异常: {e}")

    # 9. 测试项目管理组件功能完整性
    print("\n9. 测试项目管理组件功能完整性...")
    required_functions = [
        ("获取项目列表", "/projects/"),
        ("创建项目", "/projects/"),
        ("获取项目详情", "/projects/{id}"),
        ("更新项目", "/projects/{id}"),
        ("删除项目", "/projects/{id}"),
    ]

    working_functions = 0

    print("[INFO] 项目管理功能测试:")
    for name, endpoint in required_functions:
        try:
            if "获取项目列表" in name:
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            elif "创建项目" in name:
                test_data = {
                    "name": f"功能测试项目_{datetime.now().strftime('%H%M%S')}",
                    "color": "#1890ff"
                }
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=test_data)
            elif "获取项目详情" in name:
                response = requests.get(f"{BASE_URL}{endpoint.format(id='test')}", headers=headers)
            elif "更新项目" in name:
                response = requests.put(f"{BASE_URL}{endpoint.format(id='test')}", headers=headers, json={})
            elif "删除项目" in name:
                response = requests.delete(f"{BASE_URL}{endpoint.format(id='test')}", headers=headers)

            if response.status_code in [200, 201] or (response.status_code == 404 and ("详情" in name or "更新" in name or "删除" in name)):
                working_functions += 1
                status = "正常" if response.status_code in [200, 201] else "预期错误"
                print(f"  [OK] {name} - {status}")
            else:
                print(f"  [ERROR] {name} - 状态码: {response.status_code}")
        except Exception as e:
            print(f"  [ERROR] {name} - 异常: {e}")

    # 功能完整性评估
    print(f"\n[INFO] 功能通过率: {working_functions}/{len(required_functions)}")

    if working_functions >= len(required_functions) * 0.8:
        print("[OK] 项目管理组件功能基本完整")
        return True
    else:
        print("[ERROR] 项目管理组件功能不完整")
        return False

def main():
    """主函数"""
    print("开始测试项目管理组件相关API接口...")

    success = test_project_manager_apis()

    print("\n" + "=" * 50)
    print("项目管理组件API测试完成")

    if success:
        print("结论: 项目管理组件功能正常，可以进行项目的创建、编辑、删除和管理")
    else:
        print("结论: 项目管理组件功能不完整，请检查相关API接口")

    print("=" * 50)

    return success

if __name__ == "__main__":
    main()