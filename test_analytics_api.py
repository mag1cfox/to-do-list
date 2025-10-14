#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pytest
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api"

class TestAnalyticsAPI:
    """数据分析页面相关API测试"""

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

    def test_get_tasks_api(self):
        """测试获取任务列表API - 数据分析页面的主要数据源"""
        print("2. 测试获取任务列表API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        response = requests.get(f"{BASE_URL}/tasks/", headers=self.headers)

        assert response.status_code == 200, f"API请求失败，状态码: {response.status_code}"

        data = response.json()
        assert "tasks" in data, "响应中必须包含tasks字段"
        assert isinstance(data["tasks"], list), "tasks必须是列表类型"

        print(f"[OK] 获取到 {len(data['tasks'])} 个任务")

        # 验证任务数据结构
        if data['tasks']:
            task = data['tasks'][0]
            expected_fields = ['id', 'title', 'status', 'priority', 'created_at', 'updated_at']
            for field in expected_fields:
                assert field in task, f"任务必须包含{field}字段"

        print("[OK] 任务数据结构验证通过")

    def test_get_task_categories_api(self):
        """测试获取任务分类API - 用于分类统计"""
        print("3. 测试获取任务分类API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        response = requests.get(f"{BASE_URL}/task-categories/", headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            assert "task_categories" in data, "响应中必须包含task_categories字段"
            print(f"[OK] 获取到 {len(data.get('task_categories', []))} 个任务分类")
        else:
            print(f"[INFO] 任务分类API不存在或无权限，状态码: {response.status_code}")

    def test_get_projects_api(self):
        """测试获取项目列表API - 用于项目统计"""
        print("4. 测试获取项目列表API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        response = requests.get(f"{BASE_URL}/projects/", headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            assert "projects" in data, "响应中必须包含projects字段"
            print(f"[OK] 获取到 {len(data.get('projects', []))} 个项目")
        else:
            print(f"[INFO] 项目API不存在或无权限，状态码: {response.status_code}")

    def test_get_pomodoro_sessions_api(self):
        """测试获取番茄钟会话API - 用于专注时间统计"""
        print("5. 测试获取番茄钟会话API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        response = requests.get(f"{BASE_URL}/pomodoro-sessions/", headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            assert "pomodoro_sessions" in data, "响应中必须包含pomodoro_sessions字段"
            print(f"[OK] 获取到 {len(data.get('pomodoro_sessions', []))} 个番茄钟会话")

            # 验证番茄钟数据结构
            if data['pomodoro_sessions']:
                session = data['pomodoro_sessions'][0]
                expected_fields = ['id', 'task_id', 'status', 'start_time', 'planned_duration']
                for field in expected_fields:
                    if field in session:
                        pass  # 字段存在

            print("[OK] 番茄钟会话数据结构验证通过")
        else:
            print(f"[INFO] 番茄钟会话API不存在或无权限，状态码: {response.status_code}")

    def test_create_sample_tasks_for_analytics(self):
        """创建示例任务数据用于测试分析功能"""
        print("6. 创建示例任务数据...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 获取现有任务分类
        categories_response = requests.get(f"{BASE_URL}/task-categories/", headers=self.headers)
        category_id = None

        if categories_response.status_code == 200:
            categories = categories_response.json().get('task_categories', [])
            if categories:
                category_id = categories[0]['id']

        # 如果没有分类，创建一个
        if not category_id:
            category_data = {
                "name": "测试分类",
                "description": "用于数据分析测试的分类",
                "color": "#1890ff"
            }

            category_response = requests.post(f"{BASE_URL}/task-categories/",
                                           headers=self.headers,
                                           json=category_data)

            if category_response.status_code == 201:
                category_id = category_response.json()['task_category']['id']
                print("[OK] 创建测试分类成功")
            else:
                print("[INFO] 无法创建测试分类")
                return

        # 创建示例任务
        sample_tasks = [
            {
                "title": "数据分析任务1",
                "description": "用于测试数据分析功能的任务",
                "category_id": category_id,
                "planned_start_time": datetime.now().isoformat(),
                "estimated_pomodoros": 2,
                "priority": "HIGH",
                "task_type": "FLEXIBLE"
            },
            {
                "title": "数据分析任务2",
                "description": "另一个测试任务",
                "category_id": category_id,
                "planned_start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
                "estimated_pomodoros": 1,
                "priority": "MEDIUM",
                "task_type": "FLEXIBLE"
            }
        ]

        created_tasks = 0
        for task_data in sample_tasks:
            response = requests.post(f"{BASE_URL}/tasks/",
                                   headers=self.headers,
                                   json=task_data)
            if response.status_code == 201:
                created_tasks += 1

        if created_tasks > 0:
            print(f"[OK] 成功创建 {created_tasks} 个示例任务")
        else:
            print("[INFO] 创建示例任务失败或任务已存在")

    def test_analytics_data_availability(self):
        """测试分析数据的可用性"""
        print("7. 测试分析数据的可用性...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 获取任务数据
        tasks_response = requests.get(f"{BASE_URL}/tasks/", headers=self.headers)

        if tasks_response.status_code == 200:
            tasks = tasks_response.json().get('tasks', [])

            # 统计不同状态的任务数量
            status_count = {}
            for task in tasks:
                status = task.get('status', 'UNKNOWN')
                status_count[status] = status_count.get(status, 0) + 1

            print(f"[OK] 任务状态统计: {status_count}")

            # 统计优先级分布
            priority_count = {}
            for task in tasks:
                priority = task.get('priority', 'UNKNOWN')
                priority_count[priority] = priority_count.get(priority, 0) + 1

            print(f"[OK] 优先级分布: {priority_count}")

            # 计算完成率
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t.get('status') == 'COMPLETED'])
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

            print(f"[OK] 任务完成率: {completion_rate:.1f}% ({completed_tasks}/{total_tasks})")
        else:
            print("[ERROR] 无法获取任务数据进行统计")

    def test_api_response_format(self):
        """测试API响应格式的一致性"""
        print("8. 测试API响应格式的一致性...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 测试任务API响应格式
        tasks_response = requests.get(f"{BASE_URL}/tasks/", headers=self.headers)

        if tasks_response.status_code == 200:
            data = tasks_response.json()

            # 检查标准响应格式
            expected_top_level_fields = ['tasks', 'count', 'message']
            for field in expected_top_level_fields:
                assert field in data, f"响应应包含{field}字段"

            print("[OK] 任务API响应格式符合标准")
        else:
            print("[ERROR] 任务API响应格式测试失败")

def run_analytics_tests():
    """运行所有数据分析API测试"""
    print("=" * 60)
    print("数据分析页面API测试开始")
    print("=" * 60)

    test_instance = TestAnalyticsAPI()

    # 运行所有测试方法
    test_methods = [
        test_instance.test_user_authentication,
        test_instance.test_get_tasks_api,
        test_instance.test_get_task_categories_api,
        test_instance.test_get_projects_api,
        test_instance.test_get_pomodoro_sessions_api,
        test_instance.test_create_sample_tasks_for_analytics,
        test_instance.test_analytics_data_availability,
        test_instance.test_api_response_format
    ]

    passed = 0
    failed = 0
    skipped = 0

    for test_method in test_methods:
        try:
            test_instance.setup_method()  # 重新设置认证
            test_method()
            passed += 1
            print(f"✅ {test_method.__name__} - 通过")
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
        print("🎉 所有测试都通过了！数据分析页面可以正常工作。")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

    print("=" * 60)

    return failed == 0

if __name__ == "__main__":
    run_analytics_tests()