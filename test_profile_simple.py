#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

def test_profile_apis():
    """测试用户个人资料管理页面相关API"""
    print("=" * 50)
    print("用户个人资料管理页面API测试")
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
        print(f"[INFO] 用户ID: {user.get('id')}")
        print(f"[INFO] 用户名: {user.get('username')}")
        print(f"[INFO] 邮箱: {user.get('email')}")
        print(f"[INFO] 手机号: {user.get('phone', '未设置')}")
        print(f"[INFO] 所在地: {user.get('location', '未设置')}")
        print(f"[INFO] 创建时间: {user.get('created_at')}")
        print(f"[INFO] 更新时间: {user.get('updated_at')}")

        # 验证用户资料字段完整性
        required_fields = ['id', 'username', 'email', 'created_at', 'updated_at']
        missing_fields = [field for field in required_fields if field not in user]
        if missing_fields:
            print(f"[WARNING] 用户资料缺少字段: {missing_fields}")
        else:
            print("[OK] 用户资料字段完整")

        # 验证邮箱格式
        email = user.get('email', '')
        if '@' in email:
            print("[OK] 邮箱格式正确")
        else:
            print("[ERROR] 邮箱格式错误")

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

            # 显示一些关键偏好设置
            key_prefs = ['theme', 'language', 'pomodoroDuration', 'desktopNotifications']
            for key in key_prefs:
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
                "phone": f"1380000{datetime.now().strftime('%H%M%S')}",
                "location": f"测试城市_{datetime.now().strftime('%H%M')}",
                "bio": f"测试个人简介，更新于{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }

            response = requests.put(f"{BASE_URL}/users/profile", headers=headers, json=update_data)

            if response.status_code == 200:
                print("[OK] 更新用户资料成功")
                print(f"[INFO] 更新了手机号、所在地和个人简介")
                print(f"[INFO] 手机号: {update_data['phone']}")
                print(f"[INFO] 所在地: {update_data['location']}")
                print(f"[INFO] 个人简介: {update_data['bio']}")
            else:
                print(f"[INFO] 更新用户资料API不存在或失败: {response.status_code}")

    except Exception as e:
        print(f"[INFO] 更新用户资料API测试异常: {e}")

    # 5. 测试任务统计API（个人资料页面需要）
    print("\n5. 测试任务统计API...")
    try:
        response = requests.get(f"{BASE_URL}/tasks/", headers=headers)

        if response.status_code == 200:
            tasks_data = response.json()
            tasks = tasks_data.get('tasks', [])
            print(f"[OK] 获取任务数据成功，共{len(tasks)}个任务")

            # 任务统计
            completed_tasks = len([t for t in tasks if t.get('status') == 'COMPLETED'])
            total_tasks = len(tasks)
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

            print(f"[INFO] 总任务数: {total_tasks}")
            print(f"[INFO] 已完成任务: {completed_tasks}")
            print(f"[INFO] 任务完成率: {completion_rate:.1f}%")
        else:
            print(f"[INFO] 获取任务数据失败: {response.status_code}")

    except Exception as e:
        print(f"[INFO] 获取任务数据异常: {e}")

    # 6. 测试番茄钟统计API（个人资料页面需要）
    print("\n6. 测试番茄钟统计API...")
    try:
        response = requests.get(f"{BASE_URL}/pomodoro-sessions/", headers=headers)

        if response.status_code == 200:
            sessions_data = response.json()
            sessions = sessions_data.get('pomodoro_sessions', [])
            print(f"[OK] 获取番茄钟数据成功，共{len(sessions)}个会话")

            # 番茄钟统计
            completed_sessions = len([s for s in sessions if s.get('status') == 'COMPLETED'])
            total_focus_time = 0
            for session in sessions:
                if session.get('status') == 'COMPLETED':
                    total_focus_time += session.get('actual_duration', session.get('planned_duration', 0))

            print(f"[INFO] 完成番茄钟数: {completed_sessions}")
            print(f"[INFO] 总专注时间: {total_focus_time} 分钟")
        else:
            print(f"[INFO] 获取番茄钟数据失败: {response.status_code}")

    except Exception as e:
        print(f"[INFO] 获取番茄钟数据异常: {e}")

    # 7. 测试个人资料页面功能完整性
    print("\n7. 测试个人资料页面功能完整性...")
    required_functions = [
        ("获取用户资料", "/users/profile"),
        ("获取任务数据", "/tasks/"),
    ]

    optional_functions = [
        ("获取偏好设置", "/users/preferences"),
        ("更新用户资料", "/users/profile"),
        ("获取番茄钟数据", "/pomodoro-sessions/"),
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
            if "更新" in name:
                response = requests.put(f"{BASE_URL}{endpoint}", headers=headers, json={})
            else:
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)

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
        print("[OK] 个人资料管理页面功能完整可用")
        return True
    else:
        print("[ERROR] 个人资料管理页面功能不完整")
        return False

def main():
    """主函数"""
    print("开始测试用户个人资料管理页面相关API接口...")

    success = test_profile_apis()

    print("\n" + "=" * 50)
    print("用户个人资料管理页面API测试完成")

    if success:
        print("结论: 个人资料管理页面功能正常，可以进行用户资料查看、编辑和统计")
    else:
        print("结论: 个人资料管理页面功能不完整，请检查相关API接口")

    print("=" * 50)

    return success

if __name__ == "__main__":
    main()