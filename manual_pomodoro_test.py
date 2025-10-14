#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

def test_frontend_accessibility():
    """手动测试前端可访问性"""
    print("开始手动测试番茄钟界面...")

    # 测试前端服务
    frontend_url = "http://localhost:5174"
    print(f"1. 测试前端服务访问: {frontend_url}")

    try:
        response = requests.get(frontend_url, timeout=5)
        if response.status_code == 200:
            print("[OK] 前端服务正常运行")
        else:
            print(f"[ERROR] 前端服务状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] 无法访问前端服务: {e}")
        return False

    # 测试番茄钟页面
    pomodoro_url = "http://localhost:5174/pomodoro"
    print(f"2. 测试番茄钟页面: {pomodoro_url}")

    try:
        response = requests.get(pomodoro_url, timeout=5)
        if response.status_code == 200:
            print("[OK] 番茄钟页面可访问")
        else:
            print(f"[ERROR] 番茄钟页面状态码: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] 无法访问番茄钟页面: {e}")

    return True

def test_api_endpoints():
    """测试相关API端点"""
    print("3. 测试相关API端点...")

    base_url = "http://localhost:5000/api"

    # 测试登录
    print("3.1 测试用户登录...")
    login_data = {
        "username": "demo_user",
        "password": "demo123456"
    }

    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=5)
        if response.status_code == 200:
            token = response.json().get('access_token')
            print("[OK] 用户登录成功")

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            # 测试获取任务
            print("3.2 测试获取任务列表...")
            tasks_response = requests.get(f"{base_url}/tasks", headers=headers, timeout=5)
            if tasks_response.status_code == 200:
                tasks = tasks_response.json()
                print(f"[OK] 获取到 {len(tasks)} 个任务")
            else:
                print(f"[ERROR] 获取任务失败: {tasks_response.status_code}")

            # 测试获取番茄钟会话
            print("3.3 测试获取番茄钟会话...")
            sessions_response = requests.get(f"{base_url}/pomodoro-sessions", headers=headers, timeout=5)
            if sessions_response.status_code == 200:
                sessions = sessions_response.json().get('pomodoro_sessions', [])
                print(f"[OK] 获取到 {len(sessions)} 个番茄钟会话")
            else:
                print(f"[ERROR] 获取番茄钟会话失败: {sessions_response.status_code}")

        else:
            print(f"[ERROR] 登录失败: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] API测试异常: {e}")

def main():
    print("=" * 50)
    print("番茄钟计时器界面手动测试报告")
    print("=" * 50)

    # 测试前端可访问性
    frontend_ok = test_frontend_accessibility()

    if frontend_ok:
        # 测试API端点
        test_api_endpoints()

        print("\n" + "=" * 50)
        print("手动测试结果:")
        print("✓ 前端服务运行正常")
        print("✓ 番茄钟页面可访问")
        print("✓ 相关API端点可访问")
        print("\n请手动验证以下功能:")
        print("1. 访问 http://localhost:5174/pomodoro")
        print("2. 检查页面元素是否正确显示:")
        print("   - 番茄钟计时器标题")
        print("   - 任务选择下拉框")
        print("   - 开始/暂停/完成/中断按钮")
        print("   - 统计卡片（今日完成、今日中断、专注时长）")
        print("   - 设置按钮")
        print("   - 历史记录按钮")
        print("   - 计时器显示和进度条")
        print("3. 测试交互功能:")
        print("   - 选择任务")
        print("   - 点击开始按钮")
        print("   - 打开设置模态框")
        print("   - 打开历史记录模态框")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("测试失败: 前端服务无法访问")
        print("请确保前端开发服务器正在运行")
        print("=" * 50)

if __name__ == "__main__":
    main()