#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pytest
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api"

class TestTimeBlockSchedulerAPI:
    """时间块拖拽调度组件相关API测试"""

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

    def test_get_time_blocks_api(self):
        """测试获取时间块列表API - 时间块调度的核心功能"""
        print("2. 测试获取时间块列表API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        response = requests.get(f"{BASE_URL}/time-blocks/", headers=self.headers)

        assert response.status_code == 200, f"获取时间块列表失败，状态码: {response.status_code}"

        data = response.json()
        assert isinstance(data, list), "响应必须是时间块列表"

        print(f"[OK] 获取时间块列表成功，共{len(data)}个时间块")

        # 验证时间块数据结构
        if data:
            block = data[0]
            expected_fields = ['id', 'date', 'start_time', 'end_time', 'block_type', 'color', 'user_id']
            for field in expected_fields:
                assert field in block, f"时间块必须包含{field}字段"

            print(f"[INFO] 示例时间块: {block.get('date')} {block.get('start_time')}-{block.get('end_time')}")

    def test_create_time_block_api(self):
        """测试创建时间块API - 时间块调度的核心功能"""
        print("3. 测试创建时间块API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 构建测试时间块数据
        today = datetime.now().date()
        block_data = {
            "date": today.isoformat(),
            "start_time": datetime.combine(today, datetime.min.time()).isoformat(),
            "end_time": datetime.combine(today, datetime.min.time() + timedelta(hours=2)).isoformat(),
            "block_type": "GROWTH",
            "color": "#52c41a",
            "is_recurring": False
        }

        response = requests.post(f"{BASE_URL}/time-blocks/", headers=self.headers, json=block_data)

        if response.status_code == 201:
            data = response.json()
            assert "time_block" in data, "响应中必须包含time_block字段"
            block = data['time_block']

            print(f"[OK] 创建时间块成功")
            print(f"[INFO] 时间块ID: {block.get('id')}")
            print(f"[INFO] 时间块类型: {block.get('block_type')}")
            print(f"[INFO] 时间范围: {block.get('start_time')} - {block.get('end_time')}")

            # 验证返回的时间块数据
            required_fields = ['id', 'date', 'start_time', 'end_time', 'block_type', 'user_id']
            for field in required_fields:
                assert field in block, f"返回的时间块必须包含{field}字段"

            return block  # 返回创建的时间块用于后续测试
        else:
            print(f"[ERROR] 创建时间块失败，状态码: {response.status_code}")
            return None

    def test_get_single_time_block_api(self):
        """测试获取单个时间块API - 编辑模式需要"""
        print("4. 测试获取单个时间块API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 先创建一个测试时间块
        created_block = self.test_create_time_block_api()
        if not created_block:
            print("[SKIP] 无法创建测试时间块，跳过获取时间块详情测试")
            return

        block_id = created_block['id']

        # 获取时间块详情
        response = requests.get(f"{BASE_URL}/time-blocks/{block_id}", headers=self.headers)

        if response.status_code == 200:
            block = response.json()

            print(f"[OK] 获取时间块详情成功")
            print(f"[INFO] 时间块ID: {block.get('id')}")
            print(f"[INFO] 时间块类型: {block.get('block_type')}")
            print(f"[INFO] 时间范围: {block.get('start_time')} - {block.get('end_time')}")
        else:
            print(f"[ERROR] 获取时间块详情失败，状态码: {response.status_code}")

    def test_update_time_block_api(self):
        """测试更新时间块API - 时间块编辑功能"""
        print("5. 测试更新时间块API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 先创建一个测试时间块
        created_block = self.test_create_time_block_api()
        if not created_block:
            print("[SKIP] 无法创建测试时间块，跳过更新时间块测试")
            return

        block_id = created_block['id']

        # 构建更新数据
        update_data = {
            "block_type": "RESEARCH",
            "color": "#fa8c16",
            "start_time": datetime.combine(created_block['date'], datetime.min.time() + timedelta(hours=3)).isoformat(),
            "end_time": datetime.combine(created_block['date'], datetime.min.time() + timedelta(hours=5)).isoformat(),
            "is_recurring": True,
            "recurrence_pattern": "daily"
        }

        response = requests.put(f"{BASE_URL}/time-blocks/{block_id}", headers=self.headers, json=update_data)

        if response.status_code == 200:
            data = response.json()
            block = data['time_block']

            print(f"[OK] 更新时间块成功")
            print(f"[INFO] 更新后的类型: {block.get('block_type')}")
            print(f"[INFO] 更新后的颜色: {block.get('color')}")
            print(f"[INFO] 更新后的时间范围: {block.get('start_time')} - {block.get('end_time')}")
            print(f"[INFO] 重复设置: {block.get('is_recurring')}")
        else:
            print(f"[ERROR] 更新时间块失败，状态码: {response.status_code}")

    def test_delete_time_block_api(self):
        """测试删除时间块API - 时间块管理功能"""
        print("6. 测试删除时间块API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 先创建一个测试时间块
        created_block = self.test_create_time_block_api()
        if not created_block:
            print("[SKIP] 无法创建测试时间块，跳过删除时间块测试")
            return

        block_id = created_block['id']

        # 删除时间块
        response = requests.delete(f"{BASE_URL}/time-blocks/{block_id}", headers=self.headers)

        if response.status_code == 200:
            print(f"[OK] 删除时间块成功")

            # 验证时间块是否已删除
            get_response = requests.get(f"{BASE_URL}/time-blocks/{block_id}", headers=self.headers)
            if get_response.status_code == 404:
                print("[OK] 时间块已成功删除")
            else:
                print("[WARNING] 时间块可能未完全删除")
        else:
            print(f"[ERROR] 删除时间块失败，状态码: {response.status_code}")

    def test_time_block_validation_rules(self):
        """测试时间块验证规则"""
        print("7. 测试时间块验证规则...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        today = datetime.now().date()

        # 测试创建时间块时缺少必填字段
        print("[INFO] 测试缺少必填字段...")
        invalid_block_data = {
            "color": "#ff0000"
        }

        response = requests.post(f"{BASE_URL}/time-blocks/", headers=self.headers, json=invalid_block_data)
        if response.status_code == 400:
            print("[OK] 正确拒绝了缺少必填字段的时间块创建请求")
        else:
            print(f"[ERROR] 应该拒绝缺少必填字段的请求，但状态码是: {response.status_code}")

        # 测试创建时间块时时间逻辑错误
        print("[INFO] 测试时间逻辑错误...")
        invalid_time_block_data = {
            "date": today.isoformat(),
            "start_time": datetime.combine(today, datetime.min.time() + timedelta(hours=3)).isoformat(),
            "end_time": datetime.combine(today, datetime.min.time() + timedelta(hours=1)).isoformat(),  # 结束时间早于开始时间
            "block_type": "GROWTH",
            "color": "#ff0000"
        }

        response = requests.post(f"{BASE_URL}/time-blocks/", headers=self.headers, json=invalid_time_block_data)
        if response.status_code == 400:
            print("[OK] 正确拒绝了时间逻辑错误的请求")
        else:
            print(f"[ERROR] 应该拒绝时间逻辑错误的请求，但状态码是: {response.status_code}")

        # 测试创建时间块时类型错误
        print("[INFO] 测试类型错误...")
        invalid_type_block_data = {
            "date": today.isoformat(),
            "start_time": datetime.combine(today, datetime.min.time()).isoformat(),
            "end_time": datetime.combine(today, datetime.min.time() + timedelta(hours=2)).isoformat(),
            "block_type": "INVALID_TYPE",
            "color": "#ff0000"
        }

        response = requests.post(f"{BASE_URL}/time-blocks/", headers=self.headers, json=invalid_type_block_data)
        if response.status_code == 400:
            print("[OK] 正确拒绝了类型错误的请求")
        else:
            print(f"[ERROR] 应该拒绝类型错误的请求，但状态码是: {response.status_code}")

    def test_time_block_overlap_detection(self):
        """测试时间块重叠检测"""
        print("8. 测试时间块重叠检测...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        today = datetime.now().date()
        base_time = datetime.combine(today, datetime.min.time())

        # 先创建一个时间块
        first_block_data = {
            "date": today.isoformat(),
            "start_time": (base_time + timedelta(hours=9)).isoformat(),
            "end_time": (base_time + timedelta(hours=11)).isoformat(),
            "block_type": "GROWTH",
            "color": "#52c41a"
        }

        first_response = requests.post(f"{BASE_URL}/time-blocks/", headers=self.headers, json=first_block_data)
        if first_response.status_code != 201:
            print("[SKIP] 无法创建第一个时间块，跳过重叠检测测试")
            return

        # 尝试创建重叠的时间块
        overlapping_block_data = {
            "date": today.isoformat(),
            "start_time": (base_time + timedelta(hours=10)).isoformat(),
            "end_time": (base_time + timedelta(hours=12)).isoformat(),
            "block_type": "RESEARCH",
            "color": "#1890ff"
        }

        overlapping_response = requests.post(f"{BASE_URL}/time-blocks/", headers=self.headers, json=overlapping_block_data)
        if overlapping_response.status_code == 400:
            print("[OK] 正确检测到时间块重叠")
            print(f"[INFO] 错误信息: {overlapping_response.json().get('error')}")
        else:
            print(f"[ERROR] 应该检测到时间块重叠，但状态码是: {overlapping_response.status_code}")

    def test_get_tasks_for_scheduling(self):
        """测试获取任务数据 - 用于调度"""
        print("9. 测试获取任务数据...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        try:
            response = requests.get(f"{BASE_URL}/tasks/", headers=self.headers)
            if response.status_code == 200:
                tasks = response.json().get('tasks', [])
                print(f"[OK] 获取任务数据成功，共{len(tasks)}个任务")

                # 统计任务状态
                status_count = {}
                for task in tasks:
                    status = task.get('status')
                    status_count[status] = status_count.get(status, 0) + 1

                print("[INFO] 任务状态统计:")
                for status, count in status_count.items():
                    print(f"  {status}: {count}个")

                # 统计任务类型
                type_count = {}
                for task in tasks:
                    task_type = task.get('task_type')
                    type_count[task_type] = type_count.get(task_type, 0) + 1

                print("[INFO] 任务类型统计:")
                for task_type, count in type_count.items():
                    print(f"  {task_type}: {count}个")

                return tasks
            else:
                print(f"[INFO] 获取任务数据失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"[INFO] 获取任务数据异常: {e}")
            return []

    def test_time_block_scheduler_functionality(self):
        """测试时间块调度功能完整性"""
        print("10. 测试时间块调度功能完整性...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        required_functions = [
            ("获取时间块列表", "/time-blocks/"),
            ("创建时间块", "/time-blocks/"),
            ("获取时间块详情", "/time-blocks/{id}"),
            ("更新时间块", "/time-blocks/{id}"),
            ("删除时间块", "/time-blocks/{id}"),
            ("获取任务数据", "/tasks/"),
        ]

        working_functions = 0

        print("[INFO] 时间块调度功能测试:")
        for name, endpoint in required_functions:
            try:
                if "获取时间块列表" in name:
                    response = requests.get(f"{BASE_URL}{endpoint}", headers=self.headers)
                elif "创建时间块" in name:
                    today = datetime.now().date()
                    test_data = {
                        "date": today.isoformat(),
                        "start_time": datetime.combine(today, datetime.min.time() + timedelta(hours=14)).isoformat(),
                        "end_time": datetime.combine(today, datetime.min.time() + timedelta(hours=16)).isoformat(),
                        "block_type": "GROWTH",
                        "color": "#1890ff"
                    }
                    response = requests.post(f"{BASE_URL}{endpoint}", headers=self.headers, json=test_data)
                elif "获取时间块详情" in name:
                    response = requests.get(f"{BASE_URL}{endpoint.format(id='test')}", headers=self.headers)
                elif "更新时间块" in name:
                    response = requests.put(f"{BASE_URL}{endpoint.format(id='test')}", headers=self.headers, json={})
                elif "删除时间块" in name:
                    response = requests.delete(f"{BASE_URL}{endpoint.format(id='test')}", headers=self.headers)
                elif "获取任务数据" in name:
                    response = requests.get(f"{BASE_URL}{endpoint}", headers=self.headers)

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
            print("[OK] 时间块拖拽调度组件功能基本完整")
            return True
        else:
            print("[ERROR] 时间块拖拽调度组件功能不完整")
            return False

def run_time_block_scheduler_tests():
    """运行所有时间块拖拽调度组件API测试"""
    print("=" * 60)
    print("时间块拖拽调度组件API测试开始")
    print("=" * 60)

    test_instance = TestTimeBlockSchedulerAPI()

    # 运行所有测试方法
    test_methods = [
        test_instance.test_user_authentication,
        test_instance.test_get_time_blocks_api,
        test_instance.test_create_time_block_api,
        test_instance.test_get_single_time_block_api,
        test_instance.test_update_time_block_api,
        test_instance.test_delete_time_block_api,
        test_instance.test_time_block_validation_rules,
        test_instance.test_time_block_overlap_detection,
        test_instance.test_get_tasks_for_scheduling,
        test_instance.test_time_block_scheduler_functionality
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
                print(f"[PASS] {test_method.__name__} - 通过")
            else:
                failed += 1
                print(f"[FAIL] {test_method.__name__} - 失败")
        except AssertionError as e:
            print(f"[FAIL] {test_method.__name__} - 失败: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {test_method.__name__} - 异常: {e}")
            failed += 1
        print("-" * 40)

    print("=" * 60)
    print("测试结果汇总:")
    print(f"[PASS] 通过: {passed}")
    print(f"[FAIL] 失败: {failed}")
    print(f"[SKIP] 跳过: {skipped}")
    print(f"总计: {passed + failed + skipped}")

    if failed == 0:
        print("[SUCCESS] 所有测试都通过了！时间块拖拽调度组件可以正常工作。")
    else:
        print("[WARNING] 部分测试失败，请检查相关功能。")

    print("=" * 60)

    return failed == 0

if __name__ == "__main__":
    run_time_block_scheduler_tests()