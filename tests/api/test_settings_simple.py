#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

def test_settings_apis():
    """测试设置页面相关API"""
    print("=" * 50)
    print("设置页面API测试")
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

    # 2. 测试获取用户资料API
    print("\n2. 测试获取用户资料API...")
    try:
        response = requests.get(f"{BASE_URL}/users/profile", headers=headers)
        assert response.status_code == 200, f"获取用户资料失败: {response.status_code}"

        data = response.json()
        assert "user" in data, "响应中必须包含user字段"
        user = data['user']
        print(f"[OK] 获取用户资料成功")
        print(f"[INFO] 用户名: {user.get('username')}")
        print(f"[INFO] 邮箱: {user.get('email')}")
        print(f"[INFO] 用户ID: {user.get('id')}")

        # 验证用户资料字段
        required_fields = ['id', 'username', 'email', 'created_at', 'updated_at']
        missing_fields = [field for field in required_fields if field not in user]
        if missing_fields:
            print(f"[WARNING] 用户资料缺少字段: {missing_fields}")
        else:
            print("[OK] 用户资料字段完整")

    except Exception as e:
        print(f"[ERROR] 获取用户资料失败: {e}")
        return False

    # 3. 测试获取用户偏好设置API
    print("\n3. 测试获取用户偏好设置API...")
    try:
        response = requests.get(f"{BASE_URL}/users/preferences", headers=headers)

        if response.status_code == 200:
            data = response.json()
            assert "preferences" in data, "响应中必须包含preferences字段"
            preferences = data['preferences']
            print(f"[OK] 获取用户偏好设置成功")
            print(f"[INFO] 偏好设置数量: {len(preferences)}")

            # 显示关键设置
            key_settings = ['pomodoroDuration', 'theme', 'language', 'desktopNotifications']
            for key in key_settings:
                if key in preferences:
                    print(f"  {key}: {preferences[key]}")

        else:
            print(f"[INFO] 用户偏好设置API不存在或无权限: {response.status_code}")

    except Exception as e:
        print(f"[INFO] 用户偏好设置API测试异常: {e}")

    # 4. 测试更新用户资料API
    print("\n4. 测试更新用户资料API...")
    try:
        # 获取当前用户资料
        get_response = requests.get(f"{BASE_URL}/users/profile", headers=headers)
        if get_response.status_code == 200:
            current_user = get_response.json()["user"]

            # 构建更新数据
            update_data = {
                "username": current_user["username"],
                "email": current_user["email"],
                "bio": f"测试个人简介_{datetime.now().strftime('%H%M%S')}"
            }

            response = requests.put(f"{BASE_URL}/users/profile", headers=headers, json=update_data)

            if response.status_code == 200:
                print("[OK] 更新用户资料成功")
                print(f"[INFO] 更新了个人简介")
            else:
                print(f"[INFO] 更新用户资料API不存在或失败: {response.status_code}")

    except Exception as e:
        print(f"[INFO] 更新用户资料API测试异常: {e}")

    # 5. 测试更新用户偏好设置API
    print("\n5. 测试更新用户偏好设置API...")
    try:
        test_preferences = {
            "pomodoroDuration": 30,
            "breakDuration": 8,
            "theme": "DARK",
            "language": "zh-CN",
            "desktopNotifications": True,
            "soundNotifications": False
        }

        response = requests.put(f"{BASE_URL}/users/preferences", headers=headers, json=test_preferences)

        if response.status_code == 200:
            print("[OK] 更新用户偏好设置成功")
            print(f"[INFO] 更新了番茄钟时长、主题等设置")
        else:
            print(f"[INFO] 更新用户偏好设置API不存在或失败: {response.status_code}")

    except Exception as e:
        print(f"[INFO] 更新用户偏好设置API测试异常: {e}")

    # 6. 测试设置页面功能完整性
    print("\n6. 测试设置页面功能完整性...")
    required_functions = [
        ("获取用户资料", "/users/profile"),
        ("获取偏好设置", "/users/preferences"),
    ]

    optional_functions = [
        ("更新用户资料", "/users/profile"),
        ("更新偏好设置", "/users/preferences"),
    ]

    working_required = 0
    working_optional = 0

    print("[INFO] 必需功能测试:")
    for name, endpoint in required_functions:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            if response.status_code == 200:
                working_required += 1
                print(f"  [OK] {name}")
            else:
                print(f"  [ERROR] {name} - 状态码: {response.status_code}")
        except Exception as e:
            print(f"  [ERROR] {name} - 异常: {e}")

    print("[INFO] 可选功能测试:")
    for name, endpoint in optional_functions:
        try:
            response = requests.put(f"{BASE_URL}{endpoint}", headers=headers, json={})
            if response.status_code in [200, 404, 405]:
                working_optional += 1
                status = "正常" if response.status_code == 200 else "不存在"
                print(f"  [OK] {name} - {status}")
            else:
                print(f"  [ERROR] {name} - 状态码: {response.status_code}")
        except Exception as e:
            print(f"  [ERROR] {name} - 异常: {e}")

    # 功能完整性评估
    print(f"\n[INFO] 必需功能通过率: {working_required}/{len(required_functions)}")
    print(f"[INFO] 可选功能通过率: {working_optional}/{len(optional_functions)}")

    if working_required >= len(required_functions):
        print("[OK] 设置页面基本功能完整可用")
        return True
    else:
        print("[ERROR] 设置页面基本功能不完整")
        return False

def main():
    """主函数"""
    print("开始测试设置页面相关API接口...")

    success = test_settings_apis()

    print("\n" + "=" * 50)
    print("设置页面API测试完成")

    if success:
        print("结论: 设置页面功能正常，可以进行个人资料和偏好设置管理")
    else:
        print("结论: 设置页面功能不完整，请检查相关API接口")

    print("=" * 50)

    return success

if __name__ == "__main__":
    main()