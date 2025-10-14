#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import sys
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api"

def test_pomodoro_api():
    print("开始测试番茄钟会话API...")

    # 1. 用户登录获取token
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

    # 2. 获取任务列表（需要任务来创建番茄钟会话）
    print("2. 获取任务列表...")
    try:
        response = requests.get(f"{BASE_URL}/tasks", headers=headers)
        if response.status_code == 200:
            tasks = response.json()
            print(f"[OK] 获取到 {len(tasks)} 个任务")
        else:
            print(f"[ERROR] 获取任务列表失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    # 如果没有任务，创建一个测试任务
    if not tasks:
        print("2.1 创建测试任务...")
        # 先获取项目列表
        try:
            response = requests.get(f"{BASE_URL}/projects", headers=headers)
            if response.status_code == 200:
                projects = response.json()
                project_id = projects[0]['id'] if projects else None
            else:
                project_id = None
        except:
            project_id = None

        # 获取任务分类
        try:
            response = requests.get(f"{BASE_URL}/task-categories", headers=headers)
            if response.status_code == 200:
                categories = response.json()
                category_id = categories[0]['id'] if categories else None
            else:
                category_id = None
        except:
            category_id = None

        # 创建任务
        task_data = {
            "title": "番茄钟测试任务",
            "description": "用于测试番茄钟功能的任务",
            "planned_start_time": datetime.now().isoformat(),
            "estimated_pomodoros": 1,
            "task_type": "FLEXIBLE",
            "category_id": category_id or "test-category",
            "priority": "MEDIUM"
        }

        if project_id:
            task_data["project_id"] = project_id

        try:
            response = requests.post(f"{BASE_URL}/tasks", json=task_data, headers=headers)
            if response.status_code == 201:
                task = response.json()
                tasks = [task]
                print("[OK] 测试任务创建成功")
            else:
                print(f"[ERROR] 测试任务创建失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

    # 3. 创建番茄钟会话
    print("3. 创建番茄钟会话...")
    task = tasks[0]
    pomodoro_data = {
        "task_id": task['id'],
        "planned_duration": 25,
        "session_type": "FOCUS"
    }

    try:
        response = requests.post(f"{BASE_URL}/pomodoro-sessions", json=pomodoro_data, headers=headers)
        if response.status_code == 201:
            pomodoro_session = response.json().get('pomodoro_session')
            print(f"[OK] 番茄钟会话创建成功: ID={pomodoro_session['id']}")
        else:
            print(f"[ERROR] 番茄钟会话创建失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    session_id = pomodoro_session['id']

    # 4. 开始番茄钟会话
    print("4. 开始番茄钟会话...")
    try:
        response = requests.post(f"{BASE_URL}/pomodoro-sessions/{session_id}/start", headers=headers)
        if response.status_code == 200:
            print("[OK] 番茄钟会话已开始")
        else:
            print(f"[ERROR] 开始番茄钟会话失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    # 5. 获取活跃会话
    print("5. 获取活跃会话...")
    try:
        response = requests.get(f"{BASE_URL}/pomodoro-sessions/active", headers=headers)
        if response.status_code == 200:
            active_session = response.json().get('active_session')
            if active_session:
                print(f"[OK] 找到活跃会话: ID={active_session['id']}")
            else:
                print("[ERROR] 没有找到活跃会话")
                return False
        else:
            print(f"[ERROR] 获取活跃会话失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    # 6. 等待几秒钟模拟工作时间
    print("6. 模拟工作3秒...")
    time.sleep(3)

    # 7. 完成番茄钟会话
    print("7. 完成番茄钟会话...")
    try:
        complete_data = {
            "completion_summary": "成功完成了番茄钟会话，专注度很高"
        }
        response = requests.post(f"{BASE_URL}/pomodoro-sessions/{session_id}/complete", json=complete_data, headers=headers)
        if response.status_code == 200:
            completed_session = response.json().get('pomodoro_session')
            print(f"[OK] 番茄钟会话已完成，实际持续时间: {completed_session['actual_duration']}分钟")
        else:
            print(f"[ERROR] 完成番茄钟会话失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    # 8. 创建第二个会话并测试中断
    print("8. 创建第二个会话并测试中断...")
    try:
        response = requests.post(f"{BASE_URL}/pomodoro-sessions", json=pomodoro_data, headers=headers)
        if response.status_code == 201:
            pomodoro_session2 = response.json().get('pomodoro_session')
            session_id2 = pomodoro_session2['id']
            print(f"[OK] 第二个会话创建成功: ID={session_id2}")

            # 开始会话
            response = requests.post(f"{BASE_URL}/pomodoro-sessions/{session_id2}/start", headers=headers)
            if response.status_code == 200:
                print("[OK] 第二个会话已开始")

                # 等待2秒
                time.sleep(2)

                # 中断会话
                interrupt_data = {
                    "interruption_reason": "测试中断功能"
                }
                response = requests.post(f"{BASE_URL}/pomodoro-sessions/{session_id2}/interrupt", json=interrupt_data, headers=headers)
                if response.status_code == 200:
                    interrupted_session = response.json().get('pomodoro_session')
                    print(f"[OK] 会话已中断，实际持续时间: {interrupted_session['actual_duration']}分钟")
                else:
                    print(f"[ERROR] 中断会话失败: {response.status_code}")
                    return False
            else:
                print(f"[ERROR] 开始第二个会话失败: {response.status_code}")
                return False
        else:
            print(f"[ERROR] 创建第二个会话失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    # 9. 获取会话列表
    print("9. 获取会话列表...")
    try:
        response = requests.get(f"{BASE_URL}/pomodoro-sessions", headers=headers)
        if response.status_code == 200:
            sessions = response.json().get('pomodoro_sessions', [])
            print(f"[OK] 获取到 {len(sessions)} 个番茄钟会话")
            for session in sessions:
                print(f"   - 会话{session['id']}: {session['status']} ({session['session_type']}) - {session['actual_duration']}分钟")
        else:
            print(f"[ERROR] 获取会话列表失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    # 10. 获取特定会话详情
    print("10. 获取会话详情...")
    try:
        response = requests.get(f"{BASE_URL}/pomodoro-sessions/{session_id}", headers=headers)
        if response.status_code == 200:
            session_detail = response.json().get('pomodoro_session')
            print(f"[OK] 获取会话详情成功: {session_detail['status']}")
        else:
            print(f"[ERROR] 获取会话详情失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    print("所有番茄钟API测试通过!")
    return True

if __name__ == "__main__":
    try:
        if test_pomodoro_api():
            print("番茄钟API功能正常，计时器界面可以使用!")
            sys.exit(0)
        else:
            print("番茄钟API测试失败")
            sys.exit(1)
    except Exception as e:
        print(f"测试异常: {e}")
        sys.exit(1)