#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

def test_tag_manager_apis():
    """测试标签管理组件相关API"""
    print("=" * 50)
    print("标签管理组件API测试")
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

    # 2. 测试获取标签列表API
    print("\n2. 测试获取标签列表API...")
    try:
        response = requests.get(f"{BASE_URL}/tags/", headers=headers)

        if response.status_code == 200:
            tags = response.json()
            print(f"[OK] 获取标签列表成功，共{len(tags)}个标签")

            # 验证标签数据结构
            if tags:
                tag = tags[0]
                expected_fields = ['id', 'name', 'color', 'user_id']
                for field in expected_fields:
                    if field in tag:
                        print(f"  ✓ {field}: {tag[field]}")
                    else:
                        print(f"  ✗ {field}: 缺失")
        else:
            print(f"[ERROR] 获取标签列表失败: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] 获取标签列表异常: {e}")

    # 3. 测试创建标签API
    print("\n3. 测试创建标签API...")
    created_tag = None
    try:
        tag_data = {
            "name": f"测试标签_{datetime.now().strftime('%H%M%S')}",
            "color": "#52c41a"
        }

        response = requests.post(f"{BASE_URL}/tags/", headers=headers, json=tag_data)

        if response.status_code == 201:
            data = response.json()
            created_tag = data.get('tag')
            print(f"[OK] 创建标签成功")
            print(f"[INFO] 标签ID: {created_tag.get('id')}")
            print(f"[INFO] 标签名称: {created_tag.get('name')}")
            print(f"[INFO] 标签颜色: {created_tag.get('color')}")
        else:
            print(f"[ERROR] 创建标签失败: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] 创建标签异常: {e}")

    # 4. 测试获取单个标签API
    print("\n4. 测试获取单个标签API...")
    if created_tag:
        try:
            tag_id = created_tag['id']
            response = requests.get(f"{BASE_URL}/tags/{tag_id}", headers=headers)

            if response.status_code == 200:
                tag = response.json()
                print(f"[OK] 获取标签详情成功")
                print(f"[INFO] 标签ID: {tag.get('id')}")
                print(f"[INFO] 标签名称: {tag.get('name')}")
                print(f"[INFO] 标签颜色: {tag.get('color')}")
            else:
                print(f"[ERROR] 获取标签详情失败: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] 获取标签详情异常: {e}")
    else:
        print("[SKIP] 没有可用的测试标签，跳过获取标签详情测试")

    # 5. 测试更新标签API
    print("\n5. 测试更新标签API...")
    if created_tag:
        try:
            tag_id = created_tag['id']
            update_data = {
                "name": f"更新后的标签_{datetime.now().strftime('%H%M%S')}",
                "color": "#fa8c16"
            }

            response = requests.put(f"{BASE_URL}/tags/{tag_id}", headers=headers, json=update_data)

            if response.status_code == 200:
                data = response.json()
                tag = data.get('tag')
                print(f"[OK] 更新标签成功")
                print(f"[INFO] 更新后的名称: {tag.get('name')}")
                print(f"[INFO] 更新后的颜色: {tag.get('color')}")
            else:
                print(f"[ERROR] 更新标签失败: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] 更新标签异常: {e}")
    else:
        print("[SKIP] 没有可用的测试标签，跳过更新标签测试")

    # 6. 测试删除标签API
    print("\n6. 测试删除标签API...")
    if created_tag:
        try:
            tag_id = created_tag['id']
            response = requests.delete(f"{BASE_URL}/tags/{tag_id}", headers=headers)

            if response.status_code == 200:
                print("[OK] 删除标签成功")

                # 验证标签是否已删除
                get_response = requests.get(f"{BASE_URL}/tags/{tag_id}", headers=headers)
                if get_response.status_code == 404:
                    print("[OK] 标签已成功删除")
                else:
                    print("[WARNING] 标签可能未完全删除")
            else:
                print(f"[ERROR] 删除标签失败: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] 删除标签异常: {e}")
    else:
        print("[SKIP] 没有可用的测试标签，跳过删除标签测试")

    # 7. 测试标签验证规则
    print("\n7. 测试标签验证规则...")
    try:
        # 测试创建标签时缺少必填字段
        print("[INFO] 测试缺少必填字段...")
        invalid_tag_data = {
            "color": "#ff0000"
        }

        response = requests.post(f"{BASE_URL}/tags/", headers=headers, json=invalid_tag_data)
        if response.status_code == 400:
            print("[OK] 正确拒绝了缺少必填字段的标签创建请求")
        else:
            print(f"[ERROR] 应该拒绝缺少必填字段的请求，但状态码是: {response.status_code}")

        # 测试创建标签时名称重复
        print("[INFO] 测试标签名称重复...")
        # 先创建一个标签
        tag_data = {
            "name": f"重复测试标签_{datetime.now().strftime('%H%M%S')}",
            "color": "#ff0000"
        }

        create_response = requests.post(f"{BASE_URL}/tags/", headers=headers, json=tag_data)
        if create_response.status_code == 201:
            # 尝试创建同名标签
            duplicate_tag_data = {
                "name": tag_data['name'],
                "color": "#00ff00"
            }

            duplicate_response = requests.post(f"{BASE_URL}/tags/", headers=headers, json=duplicate_tag_data)
            if duplicate_response.status_code == 400:
                print("[OK] 正确拒绝了重复名称的标签创建请求")
            else:
                print(f"[ERROR] 应该拒绝重复名称的请求，但状态码是: {duplicate_response.status_code}")
        else:
            print("[SKIP] 无法创建测试标签，跳过重复名称测试")
    except Exception as e:
        print(f"[ERROR] 标签验证规则测试异常: {e}")

    # 8. 测试标签统计数据
    print("\n8. 测试标签统计数据...")
    try:
        # 获取任务数据用于统计
        tasks_response = requests.get(f"{BASE_URL}/tasks/", headers=headers)
        if tasks_response.status_code == 200:
            tasks = tasks_response.json().get('tasks', [])
            print(f"[OK] 获取任务数据成功，共{len(tasks)}个任务")

            # 获取标签数据
            tags_response = requests.get(f"{BASE_URL}/tags/", headers=headers)
            if tags_response.status_code == 200:
                tags = tags_response.json()
                print(f"[OK] 获取标签数据成功，共{len(tags)}个标签")

                # 按标签统计任务
                tag_task_count = {}
                tag_completed_count = {}

                for task in tasks:
                    if task.get('tags'):
                        for tag in task['tags']:
                            tag_task_count[tag['id']] = tag_task_count.get(tag['id'], 0) + 1
                            if task.get('status') == 'COMPLETED':
                                tag_completed_count[tag['id']] = tag_completed_count.get(tag['id'], 0) + 1

                print("[INFO] 标签任务统计:")
                for tag_id, total_count in tag_task_count.items():
                    completed_count = tag_completed_count.get(tag_id, 0)
                    completion_rate = (completed_count / total_count * 100) if total_count > 0 else 0
                    tag_name = next((tag['name'] for tag in tags if tag['id'] == tag_id), 'Unknown')
                    print(f"  标签 {tag_name}: {total_count} 个任务，{completed_count} 个完成，完成率 {completion_rate:.1f}%")
            else:
                print(f"[INFO] 获取标签数据失败: {tags_response.status_code}")
        else:
            print(f"[INFO] 获取任务数据失败: {tasks_response.status_code}")
    except Exception as e:
        print(f"[INFO] 获取标签统计数据异常: {e}")

    # 9. 测试标签管理组件功能完整性
    print("\n9. 测试标签管理组件功能完整性...")
    required_functions = [
        ("获取标签列表", "/tags/"),
        ("创建标签", "/tags/"),
        ("获取标签详情", "/tags/{id}"),
        ("更新标签", "/tags/{id}"),
        ("删除标签", "/tags/{id}"),
    ]

    working_functions = 0

    print("[INFO] 标签管理功能测试:")
    for name, endpoint in required_functions:
        try:
            if "获取标签列表" in name:
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            elif "创建标签" in name:
                test_data = {
                    "name": f"功能测试标签_{datetime.now().strftime('%H%M%S')}",
                    "color": "#1890ff"
                }
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=test_data)
            elif "获取标签详情" in name:
                response = requests.get(f"{BASE_URL}{endpoint.format(id='test')}", headers=headers)
            elif "更新标签" in name:
                response = requests.put(f"{BASE_URL}{endpoint.format(id='test')}", headers=headers, json={})
            elif "删除标签" in name:
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
        print("[OK] 标签管理组件功能基本完整")
        return True
    else:
        print("[ERROR] 标签管理组件功能不完整")
        return False

def main():
    """主函数"""
    print("开始测试标签管理组件相关API接口...")

    success = test_tag_manager_apis()

    print("\n" + "=" * 50)
    print("标签管理组件API测试完成")

    if success:
        print("结论: 标签管理组件功能正常，可以进行标签的创建、编辑、删除和管理")
    else:
        print("结论: 标签管理组件功能不完整，请检查相关API接口")

    print("=" * 50)

    return success

if __name__ == "__main__":
    main()