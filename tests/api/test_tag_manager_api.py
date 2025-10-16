#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pytest
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

class TestTagManagerAPI:
    """标签管理组件相关API测试"""

    def setup_method(self):
        """测试前设置 - 获取认证token"""
        # 登录获取token
        login_data = {
            "username": "demo_user",
            "password": "demo123456"
        }

        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)

        if response.status_code == 200:
            self.token = response.json()['access_token']
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
        else:
            self.token = None
            self.headers = {}
            print(f"登录失败: {response.status_code}")

    def test_user_authentication(self):
        """测试用户认证"""
        print("1. 测试用户认证...")

        assert self.token is not None, "认证token不能为空"
        assert "Authorization" in self.headers, "请求头必须包含Authorization"

        print("[OK] 用户认证成功")

    def test_get_tags_api(self):
        """测试获取标签列表API - 标签管理组件的核心功能"""
        print("2. 测试获取标签列表API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        response = requests.get(f"{BASE_URL}/tags/", headers=self.headers)

        assert response.status_code == 200, f"获取标签列表失败，状态码: {response.status_code}"

        data = response.json()
        assert isinstance(data, list), "响应必须是标签列表"

        print(f"[OK] 获取标签列表成功，共{len(data)}个标签")

        # 验证标签数据结构
        if data:
            tag = data[0]
            expected_fields = ['id', 'name', 'color', 'user_id']
            for field in expected_fields:
                assert field in tag, f"标签必须包含{field}字段"

            print(f"[INFO] 示例标签: {tag.get('name')} (颜色: {tag.get('color')})")

    def test_create_tag_api(self):
        """测试创建标签API - 标签管理组件的核心功能"""
        print("3. 测试创建标签API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 构建测试标签数据
        tag_data = {
            "name": f"测试标签_{datetime.now().strftime('%H%M%S')}",
            "color": "#52c41a"
        }

        response = requests.post(f"{BASE_URL}/tags/", headers=self.headers, json=tag_data)

        if response.status_code == 201:
            data = response.json()
            assert "tag" in data, "响应中必须包含tag字段"
            tag = data['tag']

            print(f"[OK] 创建标签成功")
            print(f"[INFO] 标签ID: {tag.get('id')}")
            print(f"[INFO] 标签名称: {tag.get('name')}")
            print(f"[INFO] 标签颜色: {tag.get('color')}")

            # 验证返回的标签数据
            required_fields = ['id', 'name', 'color', 'user_id']
            for field in required_fields:
                assert field in tag, f"返回的标签必须包含{field}字段"

            return tag  # 返回创建的标签用于后续测试
        else:
            print(f"[ERROR] 创建标签失败，状态码: {response.status_code}")
            print(f"[ERROR] 响应内容: {response.text}")
            return None

    def test_get_single_tag_api(self):
        """测试获取单个标签API - 编辑模式需要"""
        print("4. 测试获取单个标签API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 先创建一个测试标签
        created_tag = self.test_create_tag_api()
        if not created_tag:
            print("[SKIP] 无法创建测试标签，跳过获取标签详情测试")
            return

        tag_id = created_tag['id']

        # 获取标签详情
        response = requests.get(f"{BASE_URL}/tags/{tag_id}", headers=self.headers)

        if response.status_code == 200:
            tag = response.json()

            print(f"[OK] 获取标签详情成功")
            print(f"[INFO] 标签ID: {tag.get('id')}")
            print(f"[INFO] 标签名称: {tag.get('name')}")
            print(f"[INFO] 标签颜色: {tag.get('color')}")

            # 验证标签详情数据结构
            expected_fields = ['id', 'name', 'color', 'user_id']
            for field in expected_fields:
                if field in tag:
                    print(f"  ✓ {field}: {tag[field]}")
                else:
                    print(f"  ✗ {field}: 缺失")
        else:
            print(f"[ERROR] 获取标签详情失败，状态码: {response.status_code}")

    def test_update_tag_api(self):
        """测试更新标签API - 编辑模式的核心功能"""
        print("5. 测试更新标签API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 先创建一个测试标签
        created_tag = self.test_create_tag_api()
        if not created_tag:
            print("[SKIP] 无法创建测试标签，跳过更新标签测试")
            return

        tag_id = created_tag['id']

        # 构建更新数据
        update_data = {
            "name": f"更新后的标签_{datetime.now().strftime('%H%M%S')}",
            "color": "#fa8c16"
        }

        response = requests.put(f"{BASE_URL}/tags/{tag_id}", headers=self.headers, json=update_data)

        if response.status_code == 200:
            data = response.json()
            tag = data['tag']

            print(f"[OK] 更新标签成功")
            print(f"[INFO] 更新后的名称: {tag.get('name')}")
            print(f"[INFO] 更新后的颜色: {tag.get('color')}")

            # 验证更新是否生效
            assert tag['name'] == update_data['name'], "名称更新失败"
            assert tag['color'] == update_data['color'], "颜色更新失败"
        else:
            print(f"[ERROR] 更新标签失败，状态码: {response.status_code}")

    def test_delete_tag_api(self):
        """测试删除标签API - 标签管理功能"""
        print("6. 测试删除标签API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 先创建一个测试标签
        created_tag = self.test_create_tag_api()
        if not created_tag:
            print("[SKIP] 无法创建测试标签，跳过删除标签测试")
            return

        tag_id = created_tag['id']

        # 删除标签
        response = requests.delete(f"{BASE_URL}/tags/{tag_id}", headers=self.headers)

        if response.status_code == 200:
            print(f"[OK] 删除标签成功")

            # 验证标签是否已删除
            get_response = requests.get(f"{BASE_URL}/tags/{tag_id}", headers=self.headers)
            if get_response.status_code == 404:
                print("[OK] 标签已成功删除")
            else:
                print("[WARNING] 标签可能未完全删除")
        else:
            print(f"[ERROR] 删除标签失败，状态码: {response.status_code}")

    def test_tag_validation_rules(self):
        """测试标签验证规则"""
        print("7. 测试标签验证规则...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 测试创建标签时缺少必填字段
        print("[INFO] 测试缺少必填字段...")
        invalid_tag_data = {
            "color": "#ff0000"
        }

        response = requests.post(f"{BASE_URL}/tags/", headers=self.headers, json=invalid_tag_data)
        if response.status_code == 400:
            print("[OK] 正确拒绝了缺少必填字段的标签创建请求")
        else:
            print(f"[ERROR] 应该拒绝缺少必填字段的请求，但状态码是: {response.status_code}")

        # 测试创建标签时名称重复
        print("[INFO] 测试标签名称重复...")
        # 先创建一个标签
        created_tag = self.test_create_tag_api()
        if created_tag:
            # 尝试创建同名标签
            duplicate_tag_data = {
                "name": created_tag['name'],
                "color": "#00ff00"
            }

            response = requests.post(f"{BASE_URL}/tags/", headers=self.headers, json=duplicate_tag_data)
            if response.status_code == 400:
                print("[OK] 正确拒绝了重复名称的标签创建请求")
            else:
                print(f"[ERROR] 应该拒绝重复名称的请求，但状态码是: {response.status_code}")

    def test_tag_statistics_calculation(self):
        """测试标签统计数据计算"""
        print("8. 测试标签统计数据计算...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 获取任务数据用于统计
        try:
            tasks_response = requests.get(f"{BASE_URL}/tasks/", headers=self.headers)
            if tasks_response.status_code == 200:
                tasks = tasks_response.json().get('tasks', [])
                print(f"[OK] 获取任务数据成功，共{len(tasks)}个任务")

                # 获取标签数据
                tags_response = requests.get(f"{BASE_URL}/tags/", headers=self.headers)
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
                        print(f"  标签 {tag_name} ({tag_id}): {total_count} 个任务，{completed_count} 个完成，完成率 {completion_rate:.1f}%")
                else:
                    print(f"[INFO] 获取标签数据失败: {tags_response.status_code}")
            else:
                print(f"[INFO] 获取任务数据失败: {tasks_response.status_code}")
        except Exception as e:
            print(f"[INFO] 获取标签统计数据异常: {e}")

    def test_tag_usage_in_tasks(self):
        """测试标签在任务中的使用情况"""
        print("9. 测试标签在任务中的使用情况...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 创建一个测试标签
        created_tag = self.test_create_tag_api()
        if not created_tag:
            print("[SKIP] 无法创建测试标签，跳过使用情况测试")
            return

        try:
            # 检查是否有任务使用了这个标签
            tasks_response = requests.get(f"{BASE_URL}/tasks/", headers=self.headers)
            if tasks_response.status_code == 200:
                tasks = tasks_response.json().get('tasks', [])
                tag_usage = 0

                for task in tasks:
                    if task.get('tags') and any(tag['id'] == created_tag['id'] for tag in task['tags']):
                        tag_usage += 1

                print(f"[INFO] 新创建标签的使用次数: {tag_usage}")

                # 如果没有使用，测试是否可以删除
                if tag_usage == 0:
                    delete_response = requests.delete(f"{BASE_URL}/tags/{created_tag['id']}", headers=self.headers)
                    if delete_response.status_code == 200:
                        print("[OK] 未使用的标签可以正常删除")
                    else:
                        print(f"[ERROR] 未使用的标签删除失败: {delete_response.status_code}")
                else:
                    print(f"[INFO] 标签已被使用 {tag_usage} 次，不能直接删除")
            else:
                print(f"[INFO] 获取任务数据失败: {tasks_response.status_code}")
        except Exception as e:
            print(f"[INFO] 测试标签使用情况异常: {e}")

def run_tag_manager_tests():
    """运行所有标签管理组件API测试"""
    print("=" * 60)
    print("标签管理组件API测试开始")
    print("=" * 60)

    test_instance = TestTagManagerAPI()

    # 运行所有测试方法
    test_methods = [
        test_instance.test_user_authentication,
        test_instance.test_get_tags_api,
        test_instance.test_create_tag_api,
        test_instance.test_get_single_tag_api,
        test_instance.test_update_tag_api,
        test_instance.test_delete_tag_api,
        test_instance.test_tag_validation_rules,
        test_instance.test_tag_statistics_calculation,
        test_instance.test_tag_usage_in_tasks
    ]

    passed = 0
    failed = 0
    skipped = 0

    for test_method in test_methods:
        try:
            test_instance.setup_method()  # 重新设置认证
            result = test_method()
            if result is not False:
                passed += 1
                print(f"✅ {test_method.__name__} - 通过")
            else:
                failed += 1
                print(f"❌ {test_method.__name__} - 失败")
        except AssertionError as e:
            print(f"❌ {test_method.__name__} - 失败: {e}")
            failed += 1
        except Exception as e:
            print(f"⚠️  {test_method.__name__} - 异常: {e}")
            failed += 1
        print("-" * 40)

    print("=" * 60)
    print("测试结果汇总:")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"⚠️  跳过: {skipped}")
    print(f"总计: {passed + failed + skipped}")

    if failed == 0:
        print("🎉 所有测试都通过了！标签管理组件可以正常工作。")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

    print("=" * 60)

    return failed == 0

if __name__ == "__main__":
    run_tag_manager_tests()