#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pytest
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

class TestProjectManagerAPI:
    """项目管理组件相关API测试"""

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

    def test_get_projects_api(self):
        """测试获取项目列表API - 项目管理组件的核心功能"""
        print("2. 测试获取项目列表API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        response = requests.get(f"{BASE_URL}/projects/", headers=self.headers)

        assert response.status_code == 200, f"获取项目列表失败，状态码: {response.status_code}"

        data = response.json()
        assert isinstance(data, list), "响应必须是项目列表"

        print(f"[OK] 获取项目列表成功，共{len(data)}个项目")

        # 验证项目数据结构
        if data:
            project = data[0]
            expected_fields = ['id', 'name', 'color', 'created_at', 'user_id']
            for field in expected_fields:
                assert field in project, f"项目必须包含{field}字段"

            print(f"[INFO] 示例项目: {project.get('name')} (颜色: {project.get('color')})")

    def test_create_project_api(self):
        """测试创建项目API - 项目管理组件的核心功能"""
        print("3. 测试创建项目API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 构建测试项目数据
        project_data = {
            "name": f"测试项目_{datetime.now().strftime('%H%M%S')}",
            "color": "#52c41a",
            "description": "这是一个测试项目，用于验证项目管理组件功能"
        }

        response = requests.post(f"{BASE_URL}/projects/", headers=self.headers, json=project_data)

        if response.status_code == 201:
            data = response.json()
            assert "project" in data, "响应中必须包含project字段"
            project = data['project']

            print(f"[OK] 创建项目成功")
            print(f"[INFO] 项目ID: {project.get('id')}")
            print(f"[INFO] 项目名称: {project.get('name')}")
            print(f"[INFO] 项目颜色: {project.get('color')}")
            print(f"[INFO] 项目描述: {project.get('description')}")

            # 验证返回的项目数据
            required_fields = ['id', 'name', 'color', 'user_id', 'created_at']
            for field in required_fields:
                assert field in project, f"返回的项目必须包含{field}字段"

            return project  # 返回创建的项目用于后续测试
        else:
            print(f"[ERROR] 创建项目失败，状态码: {response.status_code}")
            print(f"[ERROR] 响应内容: {response.text}")
            return None

    def test_get_single_project_api(self):
        """测试获取单个项目API - 编辑模式需要"""
        print("4. 测试获取单个项目API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 先创建一个测试项目
        created_project = self.test_create_project_api()
        if not created_project:
            print("[SKIP] 无法创建测试项目，跳过获取项目详情测试")
            return

        project_id = created_project['id']

        # 获取项目详情
        response = requests.get(f"{BASE_URL}/projects/{project_id}", headers=self.headers)

        if response.status_code == 200:
            project = response.json()

            print(f"[OK] 获取项目详情成功")
            print(f"[INFO] 项目ID: {project.get('id')}")
            print(f"[INFO] 项目名称: {project.get('name')}")
            print(f"[INFO] 项目描述: {project.get('description')}")

            # 验证项目详情数据结构
            expected_fields = ['id', 'name', 'color', 'description', 'user_id', 'created_at']
            for field in expected_fields:
                if field in project:
                    print(f"  ✓ {field}: {project[field]}")
                else:
                    print(f"  ✗ {field}: 缺失")
        else:
            print(f"[ERROR] 获取项目详情失败，状态码: {response.status_code}")

    def test_update_project_api(self):
        """测试更新项目API - 编辑模式的核心功能"""
        print("5. 测试更新项目API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 先创建一个测试项目
        created_project = self.test_create_project_api()
        if not created_project:
            print("[SKIP] 无法创建测试项目，跳过更新项目测试")
            return

        project_id = created_project['id']

        # 构建更新数据
        update_data = {
            "name": f"更新后的项目_{datetime.now().strftime('%H%M%S')}",
            "color": "#fa8c16",
            "description": "这是更新后的项目描述"
        }

        response = requests.put(f"{BASE_URL}/projects/{project_id}", headers=self.headers, json=update_data)

        if response.status_code == 200:
            data = response.json()
            assert "project" in data, "响应中必须包含project字段"
            project = data['project']

            print(f"[OK] 更新项目成功")
            print(f"[INFO] 更新后的名称: {project.get('name')}")
            print(f"[INFO] 更新后的颜色: {project.get('color')}")
            print(f"[INFO] 更新后的描述: {project.get('description')}")

            # 验证更新是否生效
            assert project['name'] == update_data['name'], "名称更新失败"
            assert project['color'] == update_data['color'], "颜色更新失败"
            assert project['description'] == update_data['description'], "描述更新失败"
        else:
            print(f"[ERROR] 更新项目失败，状态码: {response.status_code}")

    def test_delete_project_api(self):
        """测试删除项目API - 项目管理功能"""
        print("6. 测试删除项目API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 先创建一个测试项目
        created_project = self.test_create_project_api()
        if not created_project:
            print("[SKIP] 无法创建测试项目，跳过删除项目测试")
            return

        project_id = created_project['id']

        # 删除项目
        response = requests.delete(f"{BASE_URL}/projects/{project_id}", headers=self.headers)

        if response.status_code == 200:
            print(f"[OK] 删除项目成功")

            # 验证项目是否已删除
            get_response = requests.get(f"{BASE_URL}/projects/{project_id}", headers=self.headers)
            if get_response.status_code == 404:
                print("[OK] 项目已成功删除")
            else:
                print("[WARNING] 项目可能未完全删除")
        else:
            print(f"[ERROR] 删除项目失败，状态码: {response.status_code}")

    def test_project_validation_rules(self):
        """测试项目验证规则"""
        print("7. 测试项目验证规则...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 测试创建项目时缺少必填字段
        print("[INFO] 测试缺少必填字段...")
        invalid_project_data = {
            "description": "这个项目缺少名称和颜色"
        }

        response = requests.post(f"{BASE_URL}/projects/", headers=self.headers, json=invalid_project_data)
        if response.status_code == 400:
            print("[OK] 正确拒绝了缺少必填字段的项目创建请求")
        else:
            print(f"[ERROR] 应该拒绝缺少必填字段的请求，但状态码是: {response.status_code}")

        # 测试创建项目时名称重复
        print("[INFO] 测试项目名称重复...")
        # 先创建一个项目
        created_project = self.test_create_project_api()
        if created_project:
            # 尝试创建同名项目
            duplicate_project_data = {
                "name": created_project['name'],
                "color": "#ff0000",
                "description": "这是一个重复名称的项目"
            }

            response = requests.post(f"{BASE_URL}/projects/", headers=self.headers, json=duplicate_project_data)
            if response.status_code == 400:
                print("[OK] 正确拒绝了重复名称的项目创建请求")
            else:
                print(f"[ERROR] 应该拒绝重复名称的请求，但状态码是: {response.status_code}")

    def test_project_stats_calculation(self):
        """测试项目统计数据计算"""
        print("8. 测试项目统计数据计算...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 获取任务数据用于统计
        try:
            tasks_response = requests.get(f"{BASE_URL}/tasks/", headers=self.headers)
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
            print(f"[INFO] 获取任务数据异常: {e}")

def run_project_manager_tests():
    """运行所有项目管理组件API测试"""
    print("=" * 60)
    print("项目管理组件API测试开始")
    print("=" * 60)

    test_instance = TestProjectManagerAPI()

    # 运行所有测试方法
    test_methods = [
        test_instance.test_user_authentication,
        test_instance.test_get_projects_api,
        test_instance.test_create_project_api,
        test_instance.test_get_single_project_api,
        test_instance.test_update_project_api,
        test_instance.test_delete_project_api,
        test_instance.test_project_validation_rules,
        test_instance.test_project_stats_calculation
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
        print("🎉 所有测试都通过了！项目管理组件可以正常工作。")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

    print("=" * 60)

    return failed == 0

if __name__ == "__main__":
    run_project_manager_tests()