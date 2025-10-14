#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import sys
import time
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

def test_pomodoro_basic():
    print("开始基础番茄钟功能测试...")

    # 1. 登录
    print("1. 用户登录...")
    login_data = {
        "username": "demo_user",
        "password": "demo123456"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get('access_token')
            print("[OK] 登录成功")
        else:
            print(f"[ERROR] 登录失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 2. 获取任务列表
    print("2. 获取任务列表...")
    try:
        response = requests.get(f"{BASE_URL}/tasks", headers=headers)
        if response.status_code == 200:
            tasks = response.json()
            print(f"[OK] 获取到 {len(tasks)} 个任务")
        else:
            print(f"[ERROR] 获取任务失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    if not tasks:
        print("[ERROR] 没有任务，无法创建番茄钟会话")
        return False

    # 3. 创建番茄钟会话
    print("3. 创建番茄钟会话...")
    task = tasks[0]
    pomodoro_data = {
        "task_id": task['id'],
        "planned_duration": 1,  # 只测试1分钟
        "session_type": "FOCUS"
    }

    try:
        response = requests.post(f"{BASE_URL}/pomodoro-sessions", json=pomodoro_data, headers=headers)
        if response.status_code == 201:
            session = response.json().get('pomodoro_session')
            print(f"[OK] 会话创建成功: ID={session['id']}")
        else:
            print(f"[ERROR] 创建会话失败: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    session_id = session['id']

    # 4. 开始会话
    print("4. 开始会话...")
    try:
        response = requests.post(f"{BASE_URL}/pomodoro-sessions/{session_id}/start", headers=headers)
        if response.status_code == 200:
            print("[OK] 会话已开始")
        else:
            print(f"[ERROR] 开始会话失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    # 5. 检查活跃会话
    print("5. 检查活跃会话...")
    try:
        response = requests.get(f"{BASE_URL}/pomodoro-sessions/active", headers=headers)
        if response.status_code == 200:
            active = response.json()
            if active.get('active_session'):
                print("[OK] 找到活跃会话")
            else:
                print("[ERROR] 没有找到活跃会话")
                return False
        else:
            print(f"[ERROR] 获取活跃会话失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    # 6. 等待2秒后完成会话
    print("6. 模拟工作2秒...")
    time.sleep(2)

    # 7. 完成会话
    print("7. 完成会话...")
    try:
        complete_data = {
            "completion_summary": "测试完成"
        }
        response = requests.post(f"{BASE_URL}/pomodoro-sessions/{session_id}/complete", json=complete_data, headers=headers)
        if response.status_code == 200:
            completed = response.json().get('pomodoro_session')
            print(f"[OK] 会话完成，实际用时: {completed['actual_duration']}分钟")
        else:
            print(f"[ERROR] 完成会话失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    print("基础番茄钟功能测试通过!")
    return True

if __name__ == "__main__":
    try:
        if test_pomodoro_basic():
            print("番茄钟基础功能正常，可以开发计时器界面!")
        else:
            print("番茄钟功能测试失败")
    except Exception as e:
        print(f"测试异常: {e}")