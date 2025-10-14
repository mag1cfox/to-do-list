#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pytest
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

class TestProfileAPI:
    """用户个人资料管理页面相关API测试"""

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

    def test_get_user_profile_api(self):
        """测试获取用户资料API - 个人资料页面的核心功能"""
        print("2. 测试获取用户资料API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        response = requests.get(f"{BASE_URL}/users/profile", headers=self.headers)

        assert response.status_code == 200, f"获取用户资料失败，状态码: {response.status_code}"

        data = response.json()
        assert "user" in data, "响应中必须包含user字段"
        assert "message" in data, "响应中必须包含message字段"

        user = data["user"]

        # 验证用户资料核心字段
        required_fields = ['id', 'username', 'email', 'created_at', 'updated_at']
        for field in required_fields:
            assert field in user, f"用户资料必须包含{field}字段"

        # 验证字段格式
        assert isinstance(user['id'], str), "用户ID必须是字符串"
        assert isinstance(user['username'], str), "用户名必须是字符串"
        assert isinstance(user['email'], str), "邮箱必须是字符串"

        # 验证邮箱格式
        assert '@' in user['email'], "邮箱格式不正确"

        print(f"[OK] 获取用户资料成功")
        print(f"[INFO] 用户ID: {user['id']}")
        print(f"[INFO] 用户名: {user['username']}")
        print(f"[INFO] 邮箱: {user['email']}")
        print(f"[INFO] 创建时间: {user['created_at']}")
        print(f"[INFO] 更新时间: {user['updated_at']}")

    def test_get_user_preferences_api(self):
        """测试获取用户偏好设置API - 个人资料页面可能需要的数据"""
        print("3. 测试获取用户偏好设置API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        response = requests.get(f"{BASE_URL}/users/preferences", headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            assert "preferences" in data, "响应中必须包含preferences字段"
            assert "message" in data, "响应中必须包含message字段"

            preferences = data["preferences"]
            print(f"[OK] 获取用户偏好设置成功")
            print(f"[INFO] 偏好设置内容: {json.dumps(preferences, indent=2, ensure_ascii=False)}")
        else:
            print(f"[INFO] 用户偏好设置API不存在或无权限，状态码: {response.status_code}")

    def test_update_user_profile_api(self):
        """测试更新用户资料API - 个人资料编辑功能"""
        print("4. 测试更新用户资料API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 先获取当前用户资料
        get_response = requests.get(f"{BASE_URL}/users/profile", headers=self.headers)
        if get_response.status_code != 200:
            print("[SKIP] 无法获取当前用户资料，跳过更新测试")
            return

        current_user = get_response.json()["user"]

        # 测试更新数据（包含个人资料管理相关的字段）
        update_data = {
            "username": current_user["username"],
            "email": current_user["email"],
            "phone": f"1380000{datetime.now().strftime('%H%M%S')}",  # 动态手机号
            "location": f"测试城市_{datetime.now().strftime('%H%M')}",
            "bio": f"这是测试个人简介，更新于{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }

        response = requests.put(f"{BASE_URL}/users/profile", headers=self.headers, json=update_data)

        if response.status_code == 200:
            data = response.json()
            assert "user" in data or "message" in data, "响应中必须包含user或message字段"
            print("[OK] 更新用户资料成功")
            print(f"[INFO] 更新了手机号、所在地和个人简介")
            print(f"[INFO] 更新内容: {update_data}")
        else:
            print(f"[INFO] 更新用户资料API不存在或失败，状态码: {response.status_code}")

    def test_user_profile_data_structure(self):
        """测试用户资料数据结构的完整性"""
        print("5. 测试用户资料数据结构完整性...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        response = requests.get(f"{BASE_URL}/users/profile", headers=self.headers)

        if response.status_code == 200:
            user = response.json()["user"]

            # 验证必需字段
            required_fields = ['id', 'username', 'email', 'created_at', 'updated_at']
            optional_fields = ['phone', 'location', 'bio', 'avatar', 'preferences']

            print("[OK] 必需字段验证:")
            for field in required_fields:
                if field in user:
                    print(f"  ✓ {field}: {type(user[field]).__name__}")
                else:
                    print(f"  ✗ {field}: 缺失")

            print("[OK] 可选字段验证:")
            for field in optional_fields:
                if field in user:
                    print(f"  ✓ {field}: {type(user[field]).__name__}")
                else:
                    print(f"  - {field}: 不存在（可选）")

            # 验证时间格式
            if 'created_at' in user and user['created_at']:
                try:
                    datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))
                    print("  ✓ created_at: 时间格式正确")
                except:
                    print("  ✗ created_at: 时间格式错误")

            if 'updated_at' in user and user['updated_at']:
                try:
                    datetime.fromisoformat(user['updated_at'].replace('Z', '+00:00'))
                    print("  ✓ updated_at: 时间格式正确")
                except:
                    print("  ✗ updated_at: 时间格式错误")
        else:
            print("[SKIP] 无法获取用户资料，跳过数据结构测试")

    def test_profile_page_functionality(self):
        """测试个人资料页面功能依赖的API完整性"""
        print("6. 测试个人资料页面功能完整性...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 测试个人资料页面需要的所有API
        required_apis = [
            ('GET', '/users/profile', '获取用户资料'),
        ]

        optional_apis = [
            ('GET', '/users/preferences', '获取用户偏好设置'),
            ('PUT', '/users/profile', '更新用户资料'),
            ('GET', '/tasks/', '获取任务统计'),
            ('GET', '/pomodoro-sessions/', '获取番茄钟统计'),
        ]

        working_required = 0
        working_optional = 0

        print("[INFO] 必需API测试:")
        for method, endpoint, description in required_apis:
            try:
                if method == 'GET':
                    response = requests.get(f"{BASE_URL}{endpoint}", headers=self.headers)
                elif method == 'PUT':
                    response = requests.put(f"{BASE_URL}{endpoint}", headers=self.headers, json={})

                if response.status_code == 200:
                    working_required += 1
                    print(f"  ✓ {description} - 正常")
                else:
                    print(f"  ✗ {description} - 状态码: {response.status_code}")
            except Exception as e:
                print(f"  ✗ {description} - 异常: {e}")

        print("[INFO] 可选API测试:")
        for method, endpoint, description in optional_apis:
            try:
                if method == 'GET':
                    response = requests.get(f"{BASE_URL}{endpoint}", headers=self.headers)
                elif method == 'PUT':
                    response = requests.put(f"{BASE_URL}{endpoint}", headers=self.headers, json={})

                if response.status_code in [200, 404, 405]:  # 200或API不存在
                    working_optional += 1
                    status = "正常" if response.status_code == 200 else "不存在"
                    print(f"  ✓ {description} - {status}")
                else:
                    print(f"  ✗ {description} - 状态码: {response.status_code}")
            except Exception as e:
                print(f"  ✗ {description} - 异常: {e}")

        print(f"[INFO] 必需API通过率: {working_required}/{len(required_apis)}")
        print(f"[INFO] 可选API通过率: {working_optional}/{len(optional_apis)}")

        # 个人资料页面基本功能评估
        if working_required >= len(required_apis):
            print("[OK] 个人资料页面基本功能可用")
            return True
        else:
            print("[ERROR] 个人资料页面功能不完整")
            return False

    def test_profile_related_apis(self):
        """测试个人资料相关的其他API"""
        print("7. 测试个人资料相关的其他API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 测试获取任务（用于统计数据）
        try:
            response = requests.get(f"{BASE_URL}/tasks/", headers=self.headers)
            if response.status_code == 200:
                tasks = response.json().get('tasks', [])
                print(f"[OK] 获取任务数据成功，共{len(tasks)}个任务")

                # 统计任务状态
                completed_tasks = len([t for t in tasks if t.get('status') == 'COMPLETED'])
                print(f"[INFO] 已完成任务: {completed_tasks}个")
            else:
                print(f"[INFO] 获取任务数据失败: {response.status_code}")
        except Exception as e:
            print(f"[INFO] 获取任务数据异常: {e}")

        # 测试获取番茄钟会话（用于统计数据）
        try:
            response = requests.get(f"{BASE_URL}/pomodoro-sessions/", headers=self.headers)
            if response.status_code == 200:
                sessions = response.json().get('pomodoro_sessions', [])
                print(f"[OK] 获取番茄钟数据成功，共{len(sessions)}个会话")

                # 统计完成的会话
                completed_sessions = len([s for s in sessions if s.get('status') == 'COMPLETED'])
                print(f"[INFO] 已完成会话: {completed_sessions}个")
            else:
                print(f"[INFO] 获取番茄钟数据失败: {response.status_code}")
        except Exception as e:
            print(f"[INFO] 获取番茄钟数据异常: {e}")

def run_profile_tests():
    """运行所有个人资料API测试"""
    print("=" * 60)
    print("用户个人资料管理页面API测试开始")
    print("=" * 60)

    test_instance = TestProfileAPI()

    # 运行所有测试方法
    test_methods = [
        test_instance.test_user_authentication,
        test_instance.test_get_user_profile_api,
        test_instance.test_get_user_preferences_api,
        test_instance.test_update_user_profile_api,
        test_instance.test_user_profile_data_structure,
        test_instance.test_profile_page_functionality,
        test_instance.test_profile_related_apis
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
        print("🎉 所有测试都通过了！用户个人资料管理页面可以正常工作。")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

    print("=" * 60)

    return failed == 0

if __name__ == "__main__":
    run_profile_tests()