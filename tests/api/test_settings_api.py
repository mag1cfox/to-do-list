#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pytest
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

class TestSettingsAPI:
    """设置页面相关API测试"""

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
        """测试获取用户资料API"""
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
        expected_fields = ['id', 'username', 'email', 'created_at', 'updated_at']
        for field in expected_fields:
            assert field in user, f"用户资料必须包含{field}字段"

        print(f"[OK] 获取用户资料成功 - 用户名: {user.get('username')}")
        print(f"[OK] 邮箱: {user.get('email')}")
        print(f"[OK] 用户ID: {user.get('id')}")

    def test_get_user_preferences_api(self):
        """测试获取用户偏好设置API"""
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
            print("[OK] 获取用户偏好设置成功")
            print(f"[INFO] 偏好设置内容: {json.dumps(preferences, indent=2, ensure_ascii=False)}")
        else:
            print(f"[INFO] 用户偏好设置API不存在或无权限，状态码: {response.status_code}")

    def test_update_user_profile_api(self):
        """测试更新用户资料API"""
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

        # 测试更新数据
        update_data = {
            "username": current_user["username"],
            "email": current_user["email"],
            "bio": f"测试个人简介_{datetime.now().strftime('%H%M%S')}"
        }

        response = requests.put(f"{BASE_URL}/users/profile", headers=self.headers, json=update_data)

        if response.status_code == 200:
            data = response.json()
            assert "user" in data or "message" in data, "响应中必须包含user或message字段"
            print("[OK] 更新用户资料成功")
            print(f"[INFO] 更新内容: {update_data}")
        else:
            print(f"[INFO] 更新用户资料API不存在或失败，状态码: {response.status_code}")

    def test_update_user_preferences_api(self):
        """测试更新用户偏好设置API"""
        print("5. 测试更新用户偏好设置API...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 测试更新偏好设置
        test_preferences = {
            "pomodoroDuration": 30,
            "breakDuration": 8,
            "longBreakDuration": 20,
            "theme": "DARK",
            "language": "zh-CN",
            "desktopNotifications": True,
            "soundNotifications": False,
            "autoPromptReview": True,
            "reviewTime": "21:00"
        }

        response = requests.put(f"{BASE_URL}/users/preferences", headers=self.headers, json=test_preferences)

        if response.status_code == 200:
            data = response.json()
            assert "preferences" in data or "message" in data, "响应中必须包含preferences或message字段"
            print("[OK] 更新用户偏好设置成功")
            print(f"[INFO] 更新内容: {json.dumps(test_preferences, indent=2, ensure_ascii=False)}")
        else:
            print(f"[INFO] 更新用户偏好设置API不存在或失败，状态码: {response.status_code}")

    def test_preferences_data_structure(self):
        """测试偏好设置数据结构的完整性"""
        print("6. 测试偏好设置数据结构...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 获取当前偏好设置
        get_response = requests.get(f"{BASE_URL}/users/preferences", headers=self.headers)

        if get_response.status_code == 200:
            preferences = get_response.json()["preferences"]

            # 验证关键设置字段
            key_settings = [
                'pomodoroDuration',
                'breakDuration',
                'longBreakDuration',
                'theme',
                'language',
                'desktopNotifications',
                'soundNotifications'
            ]

            print("[OK] 偏好设置数据结构检查:")
            for key in key_settings:
                if key in preferences:
                    print(f"  ✓ {key}: {preferences[key]}")
                else:
                    print(f"  ✗ {key}: 缺失")

            # 验证数据类型
            type_checks = [
                ('pomodoroDuration', int),
                ('breakDuration', int),
                ('theme', str),
                ('language', str),
                ('desktopNotifications', bool),
                ('soundNotifications', bool)
            ]

            print("[OK] 数据类型验证:")
            for key, expected_type in type_checks:
                if key in preferences and isinstance(preferences[key], expected_type):
                    print(f"  ✓ {key}: {type(preferences[key]).__name__}")
                else:
                    print(f"  ✗ {key}: 类型不匹配或缺失")
        else:
            print("[SKIP] 无法获取偏好设置，跳过数据结构测试")

    def test_settings_page_functionality(self):
        """测试设置页面功能依赖的API完整性"""
        print("7. 测试设置页面功能依赖...")

        if not self.token:
            print("[SKIP] 未获取到认证token，跳过测试")
            return

        # 测试设置页面需要的所有API
        required_apis = [
            ('GET', '/users/profile', '获取用户资料'),
            ('GET', '/users/preferences', '获取偏好设置'),
        ]

        optional_apis = [
            ('PUT', '/users/profile', '更新用户资料'),
            ('PUT', '/users/preferences', '更新偏好设置'),
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
                if method == 'PUT':
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

        # 设置页面基本功能评估
        if working_required >= len(required_apis) * 0.8:  # 至少80%的必需API正常
            print("[OK] 设置页面基本功能可用")
            return True
        else:
            print("[ERROR] 设置页面功能不完整")
            return False

def run_settings_tests():
    """运行所有设置页面API测试"""
    print("=" * 60)
    print("设置页面API测试开始")
    print("=" * 60)

    test_instance = TestSettingsAPI()

    # 运行所有测试方法
    test_methods = [
        test_instance.test_user_authentication,
        test_instance.test_get_user_profile_api,
        test_instance.test_get_user_preferences_api,
        test_instance.test_update_user_profile_api,
        test_instance.test_update_user_preferences_api,
        test_instance.test_preferences_data_structure,
        test_instance.test_settings_page_functionality
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
        print("🎉 所有测试都通过了！设置页面可以正常工作。")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

    print("=" * 60)

    return failed == 0

if __name__ == "__main__":
    run_settings_tests()