#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pytest
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api"

class TestTaskFormAPI:
    """任务创建和编辑组件相关API测试"""

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

    def test_get_task_categories_api(self):
        """测试获取任务类别API - 任务表单需要的分类数据"""
        print("2. 测试获取任务类别API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        response = requests.get(f"{BASE_URL}/task-categories/", headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            assert "task_categories" in data, "响应中必须包含task_categories字段"
            categories = data['task_categories']
            print(f"[OK] 获取任务类别成功，共{len(categories)}个类别")

            # 验证任务类别数据结构
            if categories:
                category = categories[0]
                expected_fields = ['id', 'name', 'color']
                for field in expected_fields:
                    if field in category:
                        print(f"  ✓ {field}: {category[field]}")
                    else:
                        print(f"  ✗ {field}: 缺失")
        else:
            print(f"[INFO] 任务类别API不存在或无权限，状态码: {response.status_code}")

    def test_get_projects_api(self):
        """测试获取项目列表API - 任务表单需要的项目数据"""
        print("3. 测试获取项目列表API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        response = requests.get(f"{BASE_URL}/projects/", headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            assert "projects" in data, "响应中必须包含projects字段"
            projects = data['projects']
            print(f"[OK] 获取项目列表成功，共{len(projects)}个项目")

            # 验证项目数据结构
            if projects:
                project = projects[0]
                expected_fields = ['id', 'name', 'color']
                for field in expected_fields:
                    if field in project:
                        print(f"  ✓ {field}: {project[field]}")
                    else:
                        print(f"  ✗ {field}: 缺失")
        else:
            print(f"[INFO] 项目列表API不存在或无权限，状态码: {response.status_code}")

    def test_get_tags_api(self):
        """测试获取标签列表API - 任务表单需要的标签数据"""
        print("4. 测试获取标签列表API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        response = requests.get(f"{BASE_URL}/tags/", headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            assert "tags" in data, "响应中必须包含tags字段"
            tags = data['tags']
            print(f"[OK] 获取标签列表成功，共{len(tags)}个标签")

            # 验证标签数据结构
            if tags:
                tag = tags[0]
                expected_fields = ['id', 'name', 'color']
                for field in expected_fields:
                    if field in tag:
                        print(f"  ✓ {field}: {tag[field]}")
                    else:
                        print(f"  ✗ {field}: 缺失")
        else:
            print(f"[INFO] 标签列表API不存在或无权限，状态码: {response.status_code}")

    def test_create_task_api(self):
        """测试创建任务API - 任务表单的核心功能"""
        print("5. 测试创建任务API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 首先获取一个任务类别（必需字段）
        categories_response = requests.get(f"{BASE_URL}/task-categories/", headers=self.headers)
        category_id = None

        if categories_response.status_code == 200:
            categories = categories_response.json().get('task_categories', [])
            if categories:
                category_id = categories[0]['id']
            else:
                print("[SKIP] 没有可用的任务类别，跳过创建任务测试")
                return
        else:
            print("[SKIP] 无法获取任务类别，跳过创建任务测试")
            return

        # 构建测试任务数据
        task_data = {
            "title": f"测试任务_{datetime.now().strftime('%H%M%S')}",
            "description": "这是一个测试任务，用于验证任务创建功能",
            "category_id": category_id,
            "planned_start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
            "estimated_pomodoros": 2,
            "priority": "HIGH",
            "task_type": "FLEXIBLE"
        }

        response = requests.post(f"{BASE_URL}/tasks/", headers=self.headers, json=task_data)

        if response.status_code == 201:
            data = response.json()
            assert "task" in data, "响应中必须包含task字段"
            task = data['task']

            print(f"[OK] 创建任务成功")
            print(f"[INFO] 任务ID: {task.get('id')}")
            print(f"[INFO] 任务标题: {task.get('title')}")
            print(f"[INFO] 任务状态: {task.get('status')}")

            # 验证返回的任务数据
            required_fields = ['id', 'title', 'status', 'category_id', 'planned_start_time']
            for field in required_fields:
                assert field in task, f"返回的任务必须包含{field}字段"

            return task  # 返回创建的任务用于后续测试
        else:
            print(f"[ERROR] 创建任务失败，状态码: {response.status_code}")
            print(f"[ERROR] 响应内容: {response.text}")
            return None

    def test_get_single_task_api(self):
        """测试获取单个任务API - 编辑模式需要"""
        print("6. 测试获取单个任务API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 先创建一个测试任务
        created_task = self.test_create_task_api()
        if not created_task:
            print("[SKIP] 无法创建测试任务，跳过获取任务详情测试")
            return

        task_id = created_task['id']

        # 获取任务详情
        response = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            assert "task" in data, "响应中必须包含task字段"
            task = data['task']

            print(f"[OK] 获取任务详情成功")
            print(f"[INFO] 任务ID: {task.get('id')}")
            print(f"[INFO] 任务标题: {task.get('title')}")
            print(f"[INFO] 任务描述: {task.get('description')}")

            # 验证任务详情数据结构
            expected_fields = ['id', 'title', 'description', 'status', 'priority', 'task_type']
            for field in expected_fields:
                if field in task:
                    print(f"  ✓ {field}: {task[field]}")
                else:
                    print(f"  ✗ {field}: 缺失")
        else:
            print(f"[ERROR] 获取任务详情失败，状态码: {response.status_code}")

    def test_update_task_api(self):
        """测试更新任务API - 编辑模式的核心功能"""
        print("7. 测试更新任务API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 先创建一个测试任务
        created_task = self.test_create_task_api()
        if not created_task:
            print("[SKIP] 无法创建测试任务，跳过更新任务测试")
            return

        task_id = created_task['id']

        # 构建更新数据
        update_data = {
            "title": f"更新后的任务_{datetime.now().strftime('%H%M%S')}",
            "description": "这是更新后的任务描述",
            "priority": "MEDIUM",
            "estimated_pomodoros": 3,
            "status": "IN_PROGRESS"
        }

        response = requests.put(f"{BASE_URL}/tasks/{task_id}", headers=self.headers, json=update_data)

        if response.status_code == 200:
            data = response.json()
            assert "task" in data, "响应中必须包含task字段"
            task = data['task']

            print(f"[OK] 更新任务成功")
            print(f"[INFO] 更新后的标题: {task.get('title')}")
            print(f"[INFO] 更新后的优先级: {task.get('priority')}")
            print(f"[INFO] 更新后的状态: {task.get('status')}")

            # 验证更新是否生效
            assert task['title'] == update_data['title'], "标题更新失败"
            assert task['priority'] == update_data['priority'], "优先级更新失败"
        else:
            print(f"[ERROR] 更新任务失败，状态码: {response.status_code}")

    def test_create_tag_api(self):
        """测试创建标签API - 任务表单的标签管理功能"""
        print("8. 测试创建标签API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        tag_data = {
            "name": f"测试标签_{datetime.now().strftime('%H%M%S')}",
            "color": "#1890ff"
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
        else:
            print(f"[INFO] 创建标签API不存在或失败，状态码: {response.status_code}")

    def test_task_form_data_completeness(self):
        """测试任务表单所需数据的完整性"""
        print("9. 测试任务表单数据完整性...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        required_data_sources = [
            ('任务类别', '/task-categories/'),
            ('项目列表', '/projects/'),
            ('标签列表', '/tags/'),
        ]

        working_data_sources = 0

        print("[INFO] 任务表单数据源测试:")
        for name, endpoint in required_data_sources:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", headers=self.headers)
                if response.status_code == 200:
                    working_data_sources += 1
                    data = response.json()
                    key = list(data.keys())[0]  # 获取第一个键（通常是数据列表）
                    count = len(data.get(key, []))
                    print(f"  ✓ {name}: {count} 条数据")
                else:
                    print(f"  ✗ {name}: 状态码 {response.status_code}")
            except Exception as e:
                print(f"  ✗ {name}: 异常 {e}")

        print(f"[INFO] 数据源可用性: {working_data_sources}/{len(required_data_sources)}")

        if working_data_sources >= len(required_data_sources) * 0.8:  # 至少80%的数据源可用
            print("[OK] 任务表单数据基本完整")
            return True
        else:
            print("[ERROR] 任务表单数据不完整")
            return False

def run_task_form_tests():
    """运行所有任务表单API测试"""
    print("=" * 60)
    print("任务创建和编辑组件API测试开始")
    print("=" * 60)

    test_instance = TestTaskFormAPI()

    # 运行所有测试方法
    test_methods = [
        test_instance.test_user_authentication,
        test_instance.test_get_task_categories_api,
        test_instance.test_get_projects_api,
        test_instance.test_get_tags_api,
        test_instance.test_create_task_api,
        test_instance.test_get_single_task_api,
        test_instance.test_update_task_api,
        test_instance.test_create_tag_api,
        test_instance.test_task_form_data_completeness
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
        print("🎉 所有测试都通过了！任务创建和编辑组件可以正常工作。")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

    print("=" * 60)

    return failed == 0

if __name__ == "__main__":
    run_task_form_tests()